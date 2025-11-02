# Intent-Aware Configuration Assistant

The Configuration Assistant now intelligently detects **what you want to do** and routes you to the appropriate workflow!

## 🎯 Supported Intents

### 1. White-Label Migration 🔄
**Keywords:** migrate, migration, react native, native, iOS, Android, white-label, platform, mono-repo

**What it does:**
- Migrates React Native apps to native platforms
- Uses the white-label approach from the presentation
- Creates mono-repo with platform-specific implementations
- Guided through Stage 0-3 migration process

**Triggers:**
```
👤 "I want to migrate my React Native app to native"
👤 "Help me convert my RN app to iOS and Android"
👤 "White-label migration for my mobile app"
```

---

### 2. End-to-End Solution 🏗️ (Coming Soon)
**Keywords:** build, create, develop, new app, solution, project, from scratch

**What it will do:**
- Build complete solutions from scratch
- Full-stack development assistance
- Architecture planning and implementation

**Triggers:**
```
👤 "I want to build a new mobile app"
👤 "Help me create a solution from scratch"
👤 "Develop a new project for me"
```

**Status:** Not implemented yet. Will notify user and offer white-label migration instead.

---

### 3. Help ❓
**Keywords:** help, what can you do, capabilities, options

**What it does:**
- Shows available services
- Explains capabilities
- Guides user to choose an intent

---

### 4. Unknown ❌
**What it does:**
- Asks clarifying questions
- Suggests available options
- Re-routes once intent is clear

---

## 🧠 How Intent Detection Works

### Architecture Flow

```
User Message
    ↓
Intent Router (n8n)
    ↓
LLM Intent Classification
    ↓
┌──────────────┬─────────────────┬──────────────┐
│              │                 │              │
Whitelabel  E2E Solution      Help      Unknown Intent
Workflow    (Coming Soon)    Response    Clarification
    ↓              ↓              ↓             ↓
Returns        Returns        Returns       Ask for
Response       "Soon"         Options       Clarification
```

### Intent Detection Process

**Step 1: Initial Message**
```
User: "I need to migrate my app"
  ↓
LLM analyzes message
  ↓
Returns:
{
  "intent": "whitelabel_migration",
  "confidence": 0.95,
  "reasoning": "User wants to migrate app - clear white-label intent",
  "clarificationNeeded": false
}
```

**Step 2: Route to Workflow**
```
If intent = "whitelabel_migration" → Call White-Label Config Workflow
If intent = "e2e_solution" → Show "Coming Soon" message
If intent = "help" → Show capabilities
If intent = "unknown" → Ask clarifying questions
```

**Step 3: Continue Conversation**
```
Once intent is detected, all subsequent messages go directly to
the appropriate sub-workflow without re-detecting intent.
```

---

## 🎨 User Experience Examples

### Example 1: Clear Intent
```
🤖 Hi! What would you like to do today?

👤 I want to migrate my React Native app to native iOS and Android

[Intent Detected: 🔄 White-Label Migration]

🤖 Great! Let's set up your white-label migration.
   Could you provide your React Native repository URL?

👤 https://github.com/myorg/my-app

🤖 Perfect! Where should I create the monorepo?

[... continues with white-label workflow ...]
```

### Example 2: Unclear Intent - Needs Clarification
```
🤖 Hi! What would you like to do today?

👤 I need help with my app

🤖 I can help you with:

   🔄 White-Label Migration - Migrate React Native apps to native
   🏗️ End-to-End Solutions - Build new solutions (coming soon)

   What would you like to do?

👤 I want to migrate to native

[Intent Detected: 🔄 White-Label Migration]

🤖 Got it! Let's migrate your app. What's your RN repo URL?

[... continues ...]
```

### Example 3: E2E Solution (Not Yet Available)
```
🤖 Hi! What would you like to do today?

👤 I want to build a new mobile app from scratch

[Intent Detected: 🏗️ End-to-End Solution]

🤖 🏗️ End-to-End Solution Development

   This feature is coming soon! We'll help you build complete
   solutions from scratch.

   For now, I can help you with:
   🔄 White-Label Migration - Migrate React Native apps

   Would you like to try that instead?

👤 No thanks

🤖 No problem! Check back soon for end-to-end solutions.
```

---

## 🔧 Adding New Intents

When you're ready to add the E2E Solution (or any new intent):

### Step 1: Create the Sub-Workflow

```json
// Example: 0-e2e-solution-config.json
{
  "name": "E2E Solution Configuration",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "chat/e2e-config",
        "responseMode": "responseNode"
      },
      "name": "E2E Config Trigger",
      "type": "n8n-nodes-base.webhook",
      ...
    },
    // ... nodes to collect:
    // - Project type (mobile, web, backend, etc.)
    // - Tech stack preferences
    // - Features required
    // - Timeline
    // etc.
  ]
}
```

### Step 2: Update Intent Router LLM Prompt

Edit `0-configuration-assistant-intent-router.json`:

```javascript
// In "Detect Intent with LLM" node, update system prompt:

"Available intents:\\n\\n1. **whitelabel_migration** - ...\\n\\n2. **e2e_solution** - User wants end-to-end solution development. Now IMPLEMENTED! Keywords: build, create, develop, new app, solution, project\\n\\n..."
```

### Step 3: Add Route in Switch Node

Edit `0-configuration-assistant-intent-router.json`:

Find the "Route by Intent" switch node and update connections:

```json
{
  "Route by Intent": {
    "main": [
      [{"node": "Call White-Label Config Workflow"}],  // Case 0: whitelabel_migration
      [{"node": "Call E2E Config Workflow"}],          // Case 1: e2e_solution (NEW!)
      [],                                               // Case 2: help
      [{"node": "Respond Unknown Intent"}]             // Case 3: unknown
    ]
  }
}
```

### Step 4: Add HTTP Request Node

Add new node to call your E2E workflow:

```json
{
  "parameters": {
    "url": "http://n8n:5678/webhook/chat/e2e-config",
    "requestMethod": "POST",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {"name": "message", "value": "={{ $json.userMessage }}"},
        {"name": "history", "value": "={{ $json.conversationHistory }}"},
        {"name": "sessionId", "value": "={{ $json.sessionId }}"},
        {"name": "state", "value": "={{ $json.sessionState.workflowState }}"}
      ]
    }
  },
  "name": "Call E2E Config Workflow",
  "type": "n8n-nodes-base.httpRequest"
}
```

### Step 5: Update UI (Optional)

Update `chat-interface.html` to show E2E intent badge:

```javascript
function updateIntentBadge(intent) {
  // ... existing code ...

  if (intent === 'e2e_solution') {
    intentEmoji = '🏗️';
    intentText = 'End-to-End Solution';
  }

  // ...
}
```

Update welcome message:

```javascript
window.onload = () => {
  addMessage('assistant', 'Hi! 👋 I can help you with:\n\n🔄 **White-Label Migration**\n🏗️ **End-to-End Solutions** ✨ NEW!\n\nWhat would you like to do?');
};
```

### Step 6: Update OpenWebUI Function

Update `openwebui-function.py`:

```python
intent_names = {
    "whitelabel_migration": "🔄 White-Label Migration",
    "e2e_solution": "🏗️ End-to-End Solution",  # Remove "coming soon"
    "unknown": "❓ Unknown Intent"
}
```

### Step 7: Test the Flow

```bash
# 1. Import new E2E config workflow
# 2. Import updated intent router
# 3. Test in chat interface:

👤 "I want to build a new app"
# Should detect e2e_solution intent
# Should route to E2E workflow
# Should collect project requirements
```

---

## 🧪 Testing Intent Detection

### Test Cases

**Test 1: White-Label Migration**
```
Input: "Migrate my React Native app"
Expected Intent: whitelabel_migration
Expected Confidence: > 0.8
```

**Test 2: E2E Solution**
```
Input: "Build a new mobile app from scratch"
Expected Intent: e2e_solution
Expected Confidence: > 0.8
```

**Test 3: Ambiguous**
```
Input: "Help me with my app"
Expected Intent: unknown or help
Expected: Ask clarifying question
```

**Test 4: Mixed Keywords**
```
Input: "I want to build and migrate my app"
Expected: Ask which one: build new or migrate existing?
```

### Manual Testing

```bash
# Test via curl
curl -X POST http://localhost:8001/webhook/chat/assistant \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to migrate my React Native app",
    "history": [],
    "sessionId": null,
    "state": null
  }'

# Check response for:
# - Correct intent detected
# - Appropriate routing
# - Proper response message
```

### Confidence Tuning

If intent detection is too aggressive or too conservative:

**Adjust confidence threshold:**

In "Need Clarification?" node:
```javascript
// Current: confidence < 0.7 asks for clarification
// More aggressive (fewer clarifications):
if (confidence < 0.5) { askClarification() }

// More conservative (more clarifications):
if (confidence < 0.9) { askClarification() }
```

**Adjust LLM temperature:**

In "Detect Intent with LLM" node:
```json
{
  "temperature": 0.2  // Lower = more consistent/conservative
                      // Higher = more creative/flexible
}
```

---

## 📊 Intent Analytics

Track which intents users are triggering:

```sql
-- Add to database schema
CREATE TABLE intent_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT,
  detected_intent TEXT,
  confidence FLOAT,
  user_message TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Query popular intents
SELECT
  detected_intent,
  COUNT(*) as count,
  AVG(confidence) as avg_confidence
FROM intent_logs
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY detected_intent
ORDER BY count DESC;
```

**Add logging to Intent Router:**

```javascript
// In "Parse Intent Response" node, add:
await fetch('http://web-ui:3000/api/log-intent', {
  method: 'POST',
  body: JSON.stringify({
    sessionId: sessionId,
    intent: intentData.intent,
    confidence: intentData.confidence,
    userMessage: userMessage
  })
});
```

---

## 🎯 Best Practices

### 1. Clear Intent Definitions
- **Good:** "whitelabel_migration - Migrate existing React Native apps to native platforms"
- **Bad:** "migration - Do migration stuff"

### 2. Non-Overlapping Keywords
- Ensure each intent has unique keywords
- If overlap is unavoidable, use clarifying questions

### 3. Confidence Thresholds
- Set appropriate confidence thresholds per intent
- Critical intents (e.g., payment) should require higher confidence

### 4. Fallback Gracefully
- Always have a "help" or "unknown" path
- Never leave user stuck without options

### 5. Context Awareness
- Consider conversation history in intent detection
- User might clarify intent in second message

---

## 🚀 Quick Start (Updated)

**With Intent Detection:**

```bash
# 1. Import workflows (in order)
# - 0-configuration-assistant-intent-router.json (NEW!)
# - 0-configuration-assistant.json (white-label sub-workflow)
# - 1-11: All other workflows

# 2. Open chat
open n8n-workflows/chat-interface.html

# 3. Start chatting - assistant detects intent automatically!
👤 "I need help migrating my app"

[Intent Detected: 🔄 White-Label Migration]

🤖 "Great! Let's migrate your app..."
```

---

## 🎓 Advanced: Multi-Turn Intent Refinement

For complex scenarios where intent evolves:

```
👤 "I need help with my mobile app"
🤖 "What do you want to do with it?"

👤 "I want to make it faster and support more platforms"
🤖 "Are you looking to:
     A) Migrate existing app to native (faster performance)
     B) Build a new optimized version from scratch?"

👤 "Migrate the existing one"

[Intent Detected: whitelabel_migration]
```

This is handled automatically by the LLM analyzing conversation history!

---

**Ready to detect intents and route users intelligently! 🎯**
