"""
title: n8n Pipeline Pipe
author: Cole Medin (original), Enhanced for Architecture Pipeline
author_url: https://www.youtube.com/@ColeMedin
version: 0.4.0

Simple pipe that sends chat messages to an n8n webhook endpoint.
Supports self-contained pipeline workflows with:
- Chat mode (help, status, artifacts queries)
- Execute mode (async BRD/artifact generation)
- System prompt mode (auto-tag, follow-up, title generation)
"""

from typing import Optional, Callable, Awaitable
from pydantic import BaseModel, Field
import time
import requests


def extract_event_info(event_emitter) -> tuple[Optional[str], Optional[str]]:
    if not event_emitter or not event_emitter.__closure__:
        return None, None
    for cell in event_emitter.__closure__:
        if isinstance(request_info := cell.cell_contents, dict):
            chat_id = request_info.get("chat_id")
            message_id = request_info.get("message_id")
            return chat_id, message_id
    return None, None


class Pipe:
    class Valves(BaseModel):
        webhook_url: str = Field(
            default="https://n8n.example.com/webhook/chat",
            description="n8n webhook URL to send messages to"
        )
        n8n_bearer_token: str = Field(
            default="",
            description="Bearer token for n8n webhook authentication (optional)"
        )
        input_field: str = Field(
            default="chatInput",
            description="Field name for the user message in the request payload"
        )
        response_field: str = Field(
            default="",
            description="Field name to extract from the response (leave empty for auto-detection)"
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
        self.id = "n8n_pipeline_pipe"
        self.name = "n8n Pipeline"
        self.valves = self.Valves()
        self.last_emit_time = 0

    async def emit_status(
        self,
        __event_emitter__: Callable[[dict], Awaitable[None]],
        level: str,
        message: str,
        done: bool,
    ):
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

    def format_response(self, response_data: dict) -> str:
        """Format the webhook response into a user-friendly message.
        
        Handles multiple response formats from self-contained pipeline workflows:
        1. Chat mode: {"content": "...", "agent": "...", "stage": "...", ...}
        2. Execute ack: {"status": "accepted", "jobId": "...", "projectSlug": "...", ...}
        3. System prompts: {"tags": [...]}, {"follow_ups": [...]}, {"title": "..."}
        4. Legacy formats for backward compatibility
        """
        import json

        # 1. Chat mode response - has 'content' field (highest priority)
        if "content" in response_data:
            return response_data["content"]

        # 2. System prompt responses (auto-tag, follow-up, title generation)
        if "tags" in response_data:
            # Return as JSON for Open WebUI to parse
            return json.dumps(response_data)
        
        if "follow_ups" in response_data:
            # Return as JSON for Open WebUI to parse
            return json.dumps(response_data)
        
        if "title" in response_data and len(response_data) <= 2:
            # Title generation response
            return json.dumps(response_data)

        # 3. Legacy 'output' field format
        if "output" in response_data:
            return response_data["output"]

        # 4. Execute mode ack response - async job started
        if response_data.get("status") in ["accepted", "running"]:
            project_slug = response_data.get("projectSlug", "unknown")
            project_name = response_data.get("projectName", project_slug)
            stage = response_data.get("stage", "unknown")
            message = response_data.get("message", "")
            workflow = response_data.get("workflow")

            stage_names = {
                "business-analysis": "Business Analysis",
                "architecture": "Architecture",
                "solution-architecture": "Solution Architecture",
                "risk-assessment": "Risk Assessment",
                "test-strategy": "Test Strategy",
                "project-management": "Project Management",
                "software-delivery": "Software Delivery",
            }
            stage_name = stage_names.get(stage, workflow or stage)

            result = f"**{stage_name}** started for project **{project_slug}**"
            if project_name and project_name != project_slug:
                result += f" ({project_name})"
            result += f"\n\nUse `projectSlug: {project_slug}` for the next pipeline stage."
            if message:
                result += f"\n\n{message}"
            return result

        # 5. Completion response - job finished successfully
        if response_data.get("success") and response_data.get("stage"):
            project_slug = response_data.get("projectSlug", "unknown")
            job_id = response_data.get("jobId", "")
            stage = response_data.get("stage", "unknown")
            brd_path = response_data.get("brdPath", "")

            stage_names = {
                "business-analysis": "Business Analysis",
                "architecture": "Architecture",
                "solution-architecture": "Solution Architecture",
                "risk-assessment": "Risk Assessment",
                "test-strategy": "Test Strategy",
                "project-management": "Project Management",
                "software-delivery": "Software Delivery",
            }
            stage_name = stage_names.get(stage, stage)

            result = f"**{stage_name}** completed for **{project_slug}**"
            if job_id:
                result += f"\n\nJob ID: `{job_id}`"
            if brd_path:
                result += f"\n\nOutput: `{brd_path}`"
            return result

        # 6. Fallback: return JSON as formatted string
        return f"```json\n{json.dumps(response_data, indent=2)}\n```"

    async def pipe(
        self,
        body: dict,
        __user__: Optional[dict] = None,
        __event_emitter__: Callable[[dict], Awaitable[None]] = None,
        __event_call__: Callable[[dict], Awaitable[dict]] = None,
    ) -> Optional[str]:

        messages = body.get("messages", [])

        if not messages:
            await self.emit_status(
                __event_emitter__,
                "error",
                "No messages found in the request body",
                True,
            )
            return "No messages found in the request body"

        user_message = messages[-1]["content"]
        chat_id, _ = extract_event_info(__event_emitter__)

        await self.emit_status(
            __event_emitter__, "info", "Calling n8n workflow...", False
        )

        # Build payload
        payload = {"sessionId": chat_id or "default"}
        payload[self.valves.input_field] = user_message

        try:
            headers = {"Content-Type": "application/json"}
            if self.valves.n8n_bearer_token:
                headers["Authorization"] = f"Bearer {self.valves.n8n_bearer_token}"

            response = requests.post(
                self.valves.webhook_url,
                json=payload,
                headers=headers,
                timeout=120
            )

            if response.status_code in [200, 202]:
                response_data = response.json()

                # If a specific response field is configured, extract it
                if self.valves.response_field and self.valves.response_field in response_data:
                    result = response_data[self.valves.response_field]
                else:
                    # Otherwise format the full response
                    result = self.format_response(response_data)

                await self.emit_status(__event_emitter__, "info", "Complete", True)
                return result
            else:
                error_msg = f"Webhook error: {response.status_code} - {response.text}"
                await self.emit_status(__event_emitter__, "error", error_msg, True)
                return error_msg

        except requests.exceptions.Timeout:
            await self.emit_status(__event_emitter__, "error", "Request timed out", True)
            return "The request timed out. The workflow may still be running in the background."
        except Exception as e:
            await self.emit_status(
                __event_emitter__,
                "error",
                f"Error: {str(e)}",
                True,
            )
            return f"Error: {str(e)}"
