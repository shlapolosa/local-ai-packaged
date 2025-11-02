"""
OpenWebUI Function: AI Configuration Assistant (Intent-Aware)

This function integrates with n8n Configuration Assistant workflow
to provide interactive setup for multiple intents:
- White-Label Migration (React Native → Native)
- End-to-End Solution Development (coming soon)

Installation:
1. Go to OpenWebUI → Workspace → Functions
2. Click "Create New Function"
3. Paste this code
4. Save and enable
5. Start chatting - the assistant will detect your intent!
"""

import requests
import json
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Pipe:
    """OpenWebUI Pipe for Migration Configuration Assistant"""

    class Valves(BaseModel):
        """Configuration valves for the pipe"""
        n8n_url: str = Field(
            default="http://n8n:5678",
            description="n8n base URL (use http://n8n:5678 for Docker network)"
        )
        webhook_path: str = Field(
            default="/webhook/chat/assistant",
            description="Configuration assistant webhook path (intent router)"
        )

    def __init__(self):
        self.type = "manifold"
        self.name = "AI Configuration Assistant"
        self.valves = self.Valves()
        self.session_states = {}  # Store session states per user

    def pipes(self) -> list[dict[str, str]]:
        """Return available pipes"""
        return [
            {
                "id": "ai-assistant",
                "name": "🤖 AI Configuration Assistant"
            }
        ]

    def pipe(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __event_emitter__=None
    ) -> str:
        """Main pipe function - handles chat interaction"""

        # Extract user message
        messages = body.get("messages", [])
        if not messages:
            return "Please send a message to start configuring your migration."

        user_message = messages[-1].get("content", "")

        # Get or create session
        user_id = __user__.get("id") if __user__ else "default"
        session_id = self.session_states.get(user_id, {}).get("sessionId")
        session_state = self.session_states.get(user_id, {}).get("sessionState")

        # Build conversation history
        conversation_history = [
            {
                "role": msg.get("role"),
                "content": msg.get("content")
            }
            for msg in messages[:-1]  # Exclude current message
        ]

        # Prepare request to n8n
        payload = {
            "message": user_message,
            "history": conversation_history,
            "sessionId": session_id,
            "state": session_state
        }

        try:
            # Call n8n Configuration Assistant
            url = f"{self.valves.n8n_url}{self.valves.webhook_path}"
            response = requests.post(
                url,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()

            # Update session state
            if user_id:
                self.session_states[user_id] = {
                    "sessionId": result.get("sessionId"),
                    "sessionState": result.get("sessionState")
                }

            # Get detected intent
            intent = result.get("intent")

            # Emit intent detection if detected
            if intent and __event_emitter__:
                intent_names = {
                    "whitelabel_migration": "🔄 White-Label Migration",
                    "e2e_solution": "🏗️ End-to-End Solution",
                    "unknown": "❓ Unknown Intent"
                }
                __event_emitter__({
                    "type": "status",
                    "data": {
                        "description": f"Detected: {intent_names.get(intent, intent)}",
                        "done": False
                    }
                })

            # Check if task completed
            if result.get("complete"):
                # Clear session
                if user_id in self.session_states:
                    del self.session_states[user_id]

                # Emit success event
                if __event_emitter__:
                    __event_emitter__({
                        "type": "status",
                        "data": {
                            "description": "✅ Configuration complete!",
                            "done": True
                        }
                    })

                return result.get("message", "Configuration complete!")

            # Show progress (only for whitelabel migration)
            assistant_message = result.get("message", "")

            if intent == "whitelabel_migration":
                progress = result.get("progress", {})
                if any(progress.values()):
                    progress_text = "\\n\\n**Progress:**\\n"
                    progress_text += f"- React Native Repo: {'✅' if progress.get('repoRN') else '⏳'}\\n"
                    progress_text += f"- Monorepo URL: {'✅' if progress.get('monorepoUrl') else '⏳'}\\n"
                    progress_text += f"- Platforms: {'✅' if progress.get('platforms') else '⏳'}\\n"
                    progress_text += f"- Reviewers: {'✅' if progress.get('reviewers') else '⏳'}\\n"
                    return f"{assistant_message}\\n{progress_text}"

            return assistant_message

        except requests.exceptions.RequestException as e:
            return f"❌ Error connecting to n8n: {str(e)}\\n\\nPlease ensure n8n is running and the Configuration Assistant workflow is active."
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"

    def on_startup(self):
        """Called when pipe starts"""
        print("Migration Configuration Assistant started")

    def on_shutdown(self):
        """Called when pipe stops"""
        print("Migration Configuration Assistant stopped")
