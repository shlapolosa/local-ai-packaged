"""
title: Knowledge Management Pipe
author: Based on Cole Medin's n8n_pipe, extended for Knowledge Management
author_url: https://www.youtube.com/@ColeMedin
version: 1.1.0

Knowledge Management pipe that enables:
- Listing available knowledge corpora
- Querying knowledge across collections
- Uploading new knowledge (files or pasted content)
- Reloading all collections
- Checking knowledge status
"""

from typing import Optional, Callable, Awaitable, List
from pydantic import BaseModel, Field
from pathlib import Path
import time
import requests
import base64
import json
import re


def extract_event_info(event_emitter) -> tuple[Optional[str], Optional[str]]:
    """Extract chat_id and message_id from event emitter closure."""
    if not event_emitter or not event_emitter.__closure__:
        return None, None
    for cell in event_emitter.__closure__:
        if isinstance(request_info := cell.cell_contents, dict):
            chat_id = request_info.get("chat_id")
            message_id = request_info.get("message_id")
            return chat_id, message_id
    return None, None


def extract_corpus_from_message(message: str) -> Optional[str]:
    """Extract corpus name from upload command."""
    # Pattern: "upload to <corpus>" or "add to <corpus>"
    patterns = [
        r'upload\s+(?:this\s+)?to\s+([a-z-]+)',
        r'add\s+(?:this\s+)?to\s+([a-z-]+)',
        r'save\s+(?:this\s+)?to\s+([a-z-]+)',
        r'to\s+([a-z-]+)\s*:',
    ]
    message_lower = message.lower()
    for pattern in patterns:
        match = re.search(pattern, message_lower)
        if match:
            return match.group(1)
    return None


def extract_inline_content(message: str) -> Optional[str]:
    """Extract inline markdown content from message."""
    # Look for content after corpus specification
    # Pattern: "Add this to data-standards:\n\n# Content..."
    patterns = [
        r'to\s+[a-z-]+\s*:\s*\n+([\s\S]+)',
        r':\s*```(?:markdown|md)?\s*([\s\S]+?)```',
        r':\s*\n+```(?:markdown|md)?\s*([\s\S]+?)```',
    ]
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # Check if message contains markdown after colon
    if ':' in message:
        parts = message.split(':', 1)
        if len(parts) > 1:
            potential_content = parts[1].strip()
            # Check if it looks like markdown content
            if potential_content.startswith('#') or potential_content.startswith('-') or '\n' in potential_content:
                return potential_content
    
    return None


class Pipe:
    class Valves(BaseModel):
        knowledge_webhook_url: str = Field(
            default="http://n8n:5678/webhook/knowledge-agent",
            description="n8n Knowledge Agent webhook URL"
        )
        n8n_bearer_token: str = Field(
            default="",
            description="Bearer token for n8n webhook authentication (optional)"
        )
        emit_interval: float = Field(
            default=2.0,
            description="Interval in seconds between status emissions"
        )
        enable_status_indicator: bool = Field(
            default=True,
            description="Enable or disable status indicator emissions"
        )

    def __init__(self):
        self.type = "pipe"
        self.id = "knowledge_pipe"
        self.name = "Knowledge Assistant"
        self.valves = self.Valves()
        self.last_emit_time = 0

    async def emit_status(
        self,
        __event_emitter__: Callable[[dict], Awaitable[None]],
        level: str,
        message: str,
        done: bool,
    ):
        """Emit status updates to the UI."""
        current_time = time.time()
        if (
            __event_emitter__
            and self.valves.enable_status_indicator
            and (
                current_time - self.last_emit_time >= self.valves.emit_interval or done
            )
        ):
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "status": "complete" if done else "in_progress",
                        "level": level,
                        "description": message,
                        "done": done,
                    },
                }
            )
            self.last_emit_time = current_time

    def extract_files_from_openwebui(self, __files__: Optional[List[dict]]) -> List[dict]:
        """
        Extract files from Open WebUI's __files__ reserved argument.
        
        The __files__ structure contains:
        - file.id: unique file ID
        - file.filename: original filename
        - file.data.content: parsed text content (if available)
        - file.meta.name: file name
        - file.meta.content_type: MIME type
        
        Files are stored at: /app/backend/data/uploads/{file_id}_{filename}
        """
        files = []
        
        if not __files__:
            return files
        
        for file_entry in __files__:
            try:
                # Get file info from the nested structure
                file_info = file_entry.get("file", {})
                if not file_info:
                    continue
                
                file_id = file_info.get("id", "")
                filename = file_info.get("filename", "uploaded_file")
                meta = file_info.get("meta", {})
                data = file_info.get("data", {})
                
                # Try to get parsed content first (already extracted by Open WebUI)
                content = data.get("content", "")
                
                # If no parsed content, try to read the file from disk
                if not content and file_id and filename:
                    file_path = Path(f"/app/backend/data/uploads/{file_id}_{filename}")
                    if file_path.exists():
                        try:
                            # Read binary for encoding
                            with open(file_path, "rb") as f:
                                raw_content = f.read()
                            # Try to decode as text first
                            try:
                                content = raw_content.decode("utf-8")
                            except UnicodeDecodeError:
                                # If not text, base64 encode it
                                content = base64.b64encode(raw_content).decode("utf-8")
                        except Exception as e:
                            content = f"Error reading file: {str(e)}"
                
                if content:
                    files.append({
                        "name": meta.get("name", filename),
                        "content": content,
                        "type": meta.get("content_type", "text/plain"),
                        "encoding": "utf-8"  # Content is already text or will be base64
                    })
                    
            except Exception as e:
                # Log error but continue processing other files
                continue
        
        return files

    def extract_files_from_body(self, body: dict) -> List[dict]:
        """Extract files from the request body (fallback method)."""
        files = []
        messages = body.get("messages", [])
        
        if not messages:
            return files
        
        last_message = messages[-1]
        
        # Check for files in message content (Open WebUI format)
        if isinstance(last_message.get("content"), list):
            for item in last_message["content"]:
                if isinstance(item, dict):
                    # Handle image/file attachments
                    if item.get("type") == "image_url":
                        image_url = item.get("image_url", {})
                        url = image_url.get("url", "")
                        if url.startswith("data:"):
                            # Extract base64 data
                            try:
                                header, data = url.split(",", 1)
                                mime_type = header.split(":")[1].split(";")[0]
                                files.append({
                                    "name": "uploaded_file",
                                    "content": data,
                                    "type": mime_type,
                                    "encoding": "base64"
                                })
                            except (ValueError, IndexError):
                                pass
                    elif item.get("type") == "file":
                        file_data = item.get("file", {})
                        files.append({
                            "name": file_data.get("name", "uploaded_file"),
                            "content": file_data.get("data", ""),
                            "type": file_data.get("type", "text/plain"),
                            "encoding": "base64" if file_data.get("data", "").startswith("data:") else "utf-8"
                        })
        
        # Check for files in body directly (multiple locations Open WebUI might use)
        for files_key in ["files", "attachments", "uploaded_files"]:
            if files_key in body:
                for f in body[files_key]:
                    if isinstance(f, dict):
                        # Get file content - could be in different fields
                        content = f.get("data") or f.get("content") or f.get("file", {}).get("data", "")
                        
                        # Handle data URLs
                        if isinstance(content, str) and content.startswith("data:"):
                            try:
                                header, content = content.split(",", 1)
                            except ValueError:
                                pass
                        
                        files.append({
                            "name": f.get("name", f.get("filename", "uploaded_file")),
                            "content": content,
                            "type": f.get("type", f.get("mime_type", "text/plain")),
                            "encoding": "base64"
                        })
                    elif isinstance(f, str):
                        # Could be a file path or base64 content
                        files.append({
                            "name": "uploaded_file",
                            "content": f,
                            "type": "text/plain",
                            "encoding": "base64"
                        })
        
        # Check for file info in metadata (another Open WebUI location)
        metadata = body.get("metadata", {})
        if "files" in metadata:
            for f in metadata["files"]:
                if isinstance(f, dict) and f.get("data"):
                    content = f.get("data", "")
                    if content.startswith("data:"):
                        try:
                            _, content = content.split(",", 1)
                        except ValueError:
                            pass
                    files.append({
                        "name": f.get("name", f.get("filename", "uploaded_file")),
                        "content": content,
                        "type": f.get("type", "text/plain"),
                        "encoding": "base64"
                    })
        
        return files

    def get_text_content(self, message: dict) -> str:
        """Extract text content from a message."""
        content = message.get("content", "")
        
        if isinstance(content, str):
            return content
        
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                elif isinstance(item, str):
                    text_parts.append(item)
            return " ".join(text_parts)
        
        return str(content)

    async def pipe(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __event_emitter__: Callable[[dict], Awaitable[None]] = None,
        __event_call__: Callable[[dict], Awaitable[dict]] = None,
        __files__: Optional[List[dict]] = None,
    ) -> Optional[str]:
        """Main pipe function that processes knowledge management requests."""
        
        messages = body.get("messages", [])

        if not messages:
            await self.emit_status(
                __event_emitter__,
                "error",
                "No messages found in the request body",
                True,
            )
            return "No messages found in the request body"

        # Extract user message
        user_message = self.get_text_content(messages[-1])
        chat_id, _ = extract_event_info(__event_emitter__)

        await self.emit_status(
            __event_emitter__, "info", "Processing knowledge request...", False
        )

        # Extract files from __files__ (Open WebUI reserved argument)
        files = self.extract_files_from_openwebui(__files__)
        
        # Fall back to body extraction if no files found via __files__
        if not files:
            files = self.extract_files_from_body(body)
        
        # Extract corpus if mentioned
        corpus = extract_corpus_from_message(user_message)
        
        # Extract inline content if present
        inline_content = extract_inline_content(user_message)

        # Build payload for n8n
        payload = {
            "sessionId": chat_id or "default",
            "message": user_message,
            "hasFiles": len(files) > 0,
            "corpus": corpus,
            "inlineContent": inline_content,
        }
        
        # Add files if present
        if files:
            payload["files"] = files
        
        # Add user info if available
        if __user__:
            payload["user"] = {
                "id": __user__.get("id"),
                "name": __user__.get("name"),
                "email": __user__.get("email"),
                "role": __user__.get("role"),
            }

        try:
            headers = {"Content-Type": "application/json"}
            if self.valves.n8n_bearer_token:
                headers["Authorization"] = f"Bearer {self.valves.n8n_bearer_token}"

            await self.emit_status(
                __event_emitter__, "info", "Calling Knowledge Agent...", False
            )

            response = requests.post(
                self.valves.knowledge_webhook_url,
                json=payload,
                headers=headers,
                timeout=180  # 3 minute timeout for long operations
            )

            if response.status_code in [200, 202]:
                response_data = response.json()
                
                # Extract the output from various response formats
                if isinstance(response_data, dict):
                    result = response_data.get("output") or response_data.get("response") or response_data.get("message")
                    if not result:
                        # Try to format the whole response
                        result = self.format_response(response_data)
                else:
                    result = str(response_data)

                await self.emit_status(__event_emitter__, "info", "Complete", True)
                return result
            else:
                error_msg = f"Knowledge Agent error: {response.status_code} - {response.text}"
                await self.emit_status(__event_emitter__, "error", error_msg, True)
                return error_msg

        except requests.exceptions.Timeout:
            await self.emit_status(__event_emitter__, "error", "Request timed out", True)
            return "The request timed out. The operation may still be running in the background."
        except Exception as e:
            await self.emit_status(
                __event_emitter__,
                "error",
                f"Error: {str(e)}",
                True,
            )
            return f"Error: {str(e)}"

    def format_response(self, response_data: dict) -> str:
        """Format the response data into a readable string."""
        
        # Handle list response
        if response_data.get("intent") == "list" or "collections" in response_data:
            collections = response_data.get("collections", [])
            if collections:
                lines = ["**Available Knowledge Collections**\n"]
                lines.append("| Collection | Description | Documents |")
                lines.append("|------------|-------------|-----------|")
                for col in collections:
                    name = col.get("name", col.get("collection", "Unknown"))
                    desc = col.get("description", "")[:40]
                    count = col.get("documentCount", col.get("count", 0))
                    lines.append(f"| {name} | {desc} | {count} |")
                return "\n".join(lines)
        
        # Handle upload response
        if response_data.get("intent") == "upload" or "uploaded" in response_data:
            status = response_data.get("status", "completed")
            collection = response_data.get("collection", "unknown")
            docs = response_data.get("documentsLoaded", response_data.get("chunks", 0))
            return f"**Upload {status}**\n\nCollection: {collection}\nDocuments loaded: {docs}"
        
        # Handle status response
        if response_data.get("intent") == "status":
            return response_data.get("statusReport", json.dumps(response_data, indent=2))
        
        # Handle help response
        if response_data.get("intent") == "help":
            return response_data.get("helpText", self.get_help_text())
        
        # Default: return as formatted JSON
        return f"```json\n{json.dumps(response_data, indent=2)}\n```"

    def get_help_text(self) -> str:
        """Return help text for knowledge management."""
        return """**Knowledge Assistant Help**

I can help you manage and query the knowledge base. Here's what I can do:

**Commands:**
- **List knowledge**: "What knowledge do you have?" or "List collections"
- **Query**: Ask any question and I'll search relevant knowledge
- **Upload file**: Attach a .md file and say "upload to <collection-name>"
- **Upload content**: "Add to <collection-name>: <your markdown content>"
- **Status**: "Knowledge status" to see collection statistics
- **Reload**: "Reload all knowledge" to refresh all collections

**Available Collections:**
- capability-maps
- reference-architectures
- compliance-requirements
- data-standards
- security-standards
- guardrails-principles
- existing-landscape
- testing-standards

**Example queries:**
- "What are the patient care capabilities?"
- "What HIPAA requirements apply to data storage?"
- "Show me reference architectures for microservices"
"""
