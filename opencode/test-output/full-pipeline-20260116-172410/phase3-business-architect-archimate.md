The tool call was made with a JSON payload that matches this format:

```
{
  "user_question": "How do I format an answer based on the tool's output?",
  "tool_path": "/architecture",
  "payload": {
    "name": "TOGAF Phase C: Application Architecture using ArchiMate standards"
  },
  "schema": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Tool Call Input Schema",
    "description": "Describes the structure of the input payload for a tool call.",
    "type": "object",
    "properties": {
      "user_question": {
        "type": "string"
      },
      "tool_path": {
        "type": "string"
      },
      "payload": {
        "type": "object",
        "additionalProperties": true
      }
    }
  },
  "skill_name": "archimate"
}
```

If you provide the correct payload, I can provide an assistance.
