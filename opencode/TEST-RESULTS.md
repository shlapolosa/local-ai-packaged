# JSON Output Pipeline - Test Results

## Summary

**Date:** 2026-01-16

**Objective:** Validate end-to-end JSON transformation pipeline for TOGAF/ArchiMate agents

## Test Results

### Transformation Scripts ✅ ALL WORKING

| Script | Input | Output | Status |
|--------|-------|--------|--------|
| `json-to-markdown.py` | BRD/PRD JSON | Formatted Markdown | ✅ Working |
| `json-to-archimate.py` | Architecture JSON | ArchiMate 3.1 XML | ✅ Working |
| `json-to-openapi.py` | API JSON | OpenAPI 3.1 YAML | ✅ Working |
| `json-to-sql.py` | Schema JSON | PostgreSQL DDL | ✅ Working |

### Model Output via Raw Ollama API ✅ WORKING

**Test Command:**
```bash
curl -s https://ollama.socrates-hlapolosa.org/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5:7b-instruct-q4_K_M",
    "messages": [
      {"role": "system", "content": "Output ONLY JSON. First char {, last char }. No explanations."},
      {"role": "user", "content": "Generate BRD JSON for: Healthcare appointment booking. 85% phone, 8min calls, 35% abandon. Goal: 40% call reduction. Budget $250K, 8 months. Epic FHIR. HIPAA."}
    ],
    "stream": false,
    "options": {"temperature": 0.1}
  }' | jq -r '.message.content'
```

**Result:** Valid JSON with correct healthcare content

### Model Output via OpenCode ⚠️ PARTIAL - CONTENT ISSUE

**Issue Identified:** OpenCode adds folder/file context to prompts. The model prioritizes this context over user input, generating content about "Local AI Packaged" (folder name) instead of the requested healthcare project.

**Evidence:**
- Skill receives correct input: `{"description":"Healthcare appointment booking..."}`
- Model outputs: `"title": "BRD: Local AI Packaged App Development"`
- Same prompt via raw API outputs: `"title": "BRD: Healthcare Appointment Booking System"`

## Recommended Solution for n8n Workflow

### Option 1: Direct Ollama API (Recommended)

Call Ollama API directly from n8n instead of through OpenCode:

```javascript
// n8n HTTP Request node
const response = await $http.post('https://ollama.socrates-hlapolosa.org/api/chat', {
  model: 'qwen2.5:7b-instruct-q4_K_M',
  messages: [
    { role: 'system', content: 'Output ONLY JSON. First char {, last char }.' },
    { role: 'user', content: `Generate BRD JSON for: ${requirements}. Schema: {...}` }
  ],
  stream: false,
  options: { temperature: 0.1 }
});
const jsonOutput = response.message.content;
```

Then use transformation scripts:
```bash
echo "$jsonOutput" > /tmp/brd.json
python3 scripts/json-to-markdown.py /tmp/brd.json /tmp/brd.md
```

### Option 2: Fix OpenCode Context (Complex)

Investigate OpenCode source to find where folder context is injected and disable it.

### Option 3: Post-Processing (Workaround)

Accept OpenCode output and replace project name in JSON before transformation.

## Pipeline Architecture

```
┌─────────────┐      ┌─────────────┐      ┌──────────────┐
│   Ollama    │      │    JSON     │      │  Transform   │
│   API       │ ───► │  Validate   │ ───► │   Script     │
│  (direct)   │      │             │      │              │
└─────────────┘      └─────────────┘      └──────────────┘
                                                 │
                           ┌─────────────────────┼─────────────────────┐
                           │                     │                     │
                           ▼                     ▼                     ▼
                    ┌────────────┐        ┌────────────┐        ┌────────────┐
                    │  Markdown  │        │ ArchiMate  │        │  OpenAPI   │
                    │   (BRD)    │        │    XML     │        │   YAML     │
                    └────────────┘        └────────────┘        └────────────┘
```

## Test Artifacts

- `/tmp/healthcare-brd.json` - Valid BRD JSON
- `/tmp/healthcare-brd.md` - Transformed Markdown
- `/tmp/ba-agent-qwen.txt` - OpenCode output (wrong content)
- `/tmp/raw-api-brd.json` - Direct API output (correct content)

## Next Steps

1. Update n8n workflow to call Ollama API directly
2. Add JSON validation step before transformation
3. Test full pipeline: n8n → Ollama → JSON → Transform → Git commit
