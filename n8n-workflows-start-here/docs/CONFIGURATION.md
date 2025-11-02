# Configuration Assistant - Interactive Chat Setup

Instead of manually crafting JSON requests, use the Configuration Assistant to set up your migration through a friendly conversation!

## 🎯 What It Does

The Configuration Assistant:
- **Asks questions one at a time** - No overwhelming forms
- **Validates your responses** - Catches mistakes early
- **Shows your progress** - Visual progress bar
- **Confirms before starting** - Review everything before triggering
- **Automatically starts migration** - No manual API calls needed

## 🚀 Three Ways to Use It

### Option 1: Web Chat Interface (Easiest)

**Best for:** Quick testing, standalone usage

1. **Import the workflow:**
   ```bash
   # In n8n UI, import:
   # 0-configuration-assistant.json
   # Activate the workflow
   ```

2. **Open the chat interface:**
   ```bash
   open n8n-workflows/chat-interface.html
   # Or serve it:
   python3 -m http.server 8080
   # Then open: http://localhost:8080/chat-interface.html
   ```

3. **Start chatting!**
   - Assistant will guide you through each step
   - Provide information as requested
   - Confirm when ready
   - Migration starts automatically!

**Example conversation:**
```
🤖 Hi! I'm here to help you set up your migration.
   Could you please provide the URL of your React Native repository?

👤 https://github.com/myorg/my-rn-app

🤖 Great! Now, where should I create the monorepo for the migration?

👤 https://github.com/shlapolosa/coding-assistant

🤖 Perfect! Which platforms do you want to target?
   Options: iOS, Android, Web (you can choose multiple)

👤 iOS and Android

🤖 Excellent! What migration stages do you want to complete?
   - Stage 0: Scaffold
   - Stage 1: Analysis
   - Stage 2: Contracts
   - Stage 3: Code generation

👤 Stages 1 through 3

🤖 Who should review the PRs? (GitHub username)

👤 shlapolosa

🤖 Perfect! Let me summarize your configuration:

   ✅ React Native Repo: https://github.com/myorg/my-rn-app
   ✅ Monorepo: https://github.com/shlapolosa/coding-assistant
   ✅ Platforms: iOS, Android
   ✅ Stages: 1 → 3
   ✅ Reviewer: @shlapolosa

   Does this look correct? (yes/no)

👤 yes

🤖 ✅ Migration started successfully!
   Migration ID: abc-123-def-456

   You can monitor progress and approve PRs on GitHub:
   https://github.com/shlapolosa/coding-assistant/pulls
```

---

### Option 2: OpenWebUI Function (Best Experience)

**Best for:** Integrated experience, using OpenWebUI daily

1. **Import n8n workflow:**
   ```bash
   # Import: 0-configuration-assistant.json
   # Activate it
   ```

2. **Add function to OpenWebUI:**
   - Go to OpenWebUI (http://localhost:8002)
   - Navigate to: Workspace → Functions
   - Click "Create New Function"
   - Copy content from `openwebui-function.py`
   - Paste and save
   - Enable the function

3. **Start a new chat in OpenWebUI:**
   - Select "🤖 Migration Setup Assistant" from the model dropdown
   - Start chatting!

4. **Benefits:**
   - Integrated with your OpenWebUI workspace
   - Session persistence
   - Full markdown support
   - Can reference previous migrations

---

### Option 3: Direct API Calls (For Automation)

**Best for:** Scripts, CI/CD, programmatic usage

```bash
# Start conversation
curl -X POST http://localhost:8001/webhook/chat/migration-config \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to migrate my React Native app",
    "history": [],
    "sessionId": null,
    "state": null
  }'

# Response includes sessionId and sessionState
# Continue conversation with updated session

curl -X POST http://localhost:8001/webhook/chat/migration-config \
  -H "Content-Type: application/json" \
  -d '{
    "message": "https://github.com/myorg/my-rn-app",
    "history": [...],
    "sessionId": "abc-123",
    "state": {...}
  }'

# When complete, you'll get:
# { "complete": true, "migrationId": "..." }
```

---

## 📋 Required Information

The assistant will collect:

1. **React Native Repository URL** (required)
   - Example: `https://github.com/myorg/rn-app`
   - The codebase you want to migrate from

2. **Existing Native Repository** (optional)
   - Example: `https://github.com/myorg/native-app`
   - Leave empty if starting fresh

3. **Monorepo URL** (required)
   - Example: `https://github.com/shlapolosa/coding-assistant`
   - Where the migration will be created

4. **Target Platforms** (required, at least one)
   - Options: `ios`, `android`, `web`
   - Example: "iOS and Android" or "all three"

5. **Migration Stages** (required)
   - Start stage: 0-3
   - End stage: 0-3
   - Example: "Stage 1 through 3"

6. **GitHub Reviewers** (required, at least one)
   - Example: `shlapolosa` or `@shlapolosa`
   - Who will approve PRs

7. **Target Branch** (optional, defaults to 'main')
   - Example: `main` or `develop`

---

## 🎨 Conversation Tips

**Natural language works!**
```
✅ "My RN repo is https://github.com/myorg/app"
✅ "iOS and Android please"
✅ "Stages 1, 2, and 3"
✅ "shlapolosa should review"
✅ "yes" / "looks good" / "confirm" / "start"
```

**Assistant is smart:**
- Extracts URLs automatically
- Recognizes platform names (iOS, Android, Web)
- Understands stage numbers
- Parses GitHub usernames (with or without @)

**You can provide multiple pieces at once:**
```
👤 My repo is https://github.com/myorg/rn-app and I want to migrate
   to https://github.com/shlapolosa/monorepo for iOS and Android
```

---

## 🔧 Configuration

### Customize n8n Workflow

Edit `0-configuration-assistant.json` to customize:

**Change LLM model:**
```json
{
  "model": "qwen2.5-coder:32b"  // Use larger model for better understanding
}
```

**Adjust temperature:**
```json
{
  "temperature": 0.3  // Lower = more consistent, Higher = more creative
}
```

**Customize system prompt:**
Edit the system message in the "Chat with Assistant" node to change assistant personality or add domain-specific knowledge.

### Customize Chat Interface

Edit `chat-interface.html`:

**Change n8n URL:**
```javascript
const N8N_URL = 'http://localhost:8001';  // Change if n8n is elsewhere
```

**Customize styling:**
Modify the `<style>` section to match your brand colors.

**Add welcome message:**
```javascript
window.onload = () => {
  addMessage('assistant', 'Your custom welcome message here!');
};
```

---

## 🐛 Troubleshooting

### "Error connecting to n8n"
- **Check n8n is running:** `docker ps | grep n8n`
- **Check workflow is active:** Open n8n UI, verify "Configuration Assistant" is ON
- **Check URL:** Ensure `N8N_URL` points to correct address
- **CORS issues:** If using chat-interface.html from file://, serve it via HTTP

### "Assistant not understanding me"
- **Be more specific:** Instead of "yes", try "yes, that's correct"
- **Provide full URLs:** `https://github.com/org/repo` not `org/repo`
- **One thing at a time:** If assistant misses something, provide it again
- **Use keywords:** "iOS", "Stage 1", "@username"

### "Migration didn't start"
- **Check confirmation:** Did you confirm with "yes" or similar?
- **Check Master Orchestrator:** Ensure `2-master-orchestrator.json` is imported and active
- **Check logs:** In n8n UI, view execution logs for errors
- **Validate config:** Ensure all required fields were collected

### "Session lost between messages"
- **Web interface:** Normal - sessions stored in memory, lost on refresh
- **OpenWebUI:** Persistent per user
- **API:** Pass `sessionId` and `state` in each request

---

## 🎓 Advanced Usage

### Custom Validation

Add validation logic in "Parse LLM Response & Update State" node:

```javascript
// Validate GitHub URL
if (updatedState.repoRN && !updatedState.repoRN.startsWith('https://github.com/')) {
  return {
    json: {
      assistantMessage: "⚠️ Please provide a valid GitHub URL starting with https://github.com/",
      action: null,
      sessionState: updatedState,
      sessionId: sessionId
    }
  };
}
```

### Add New Fields

1. **Update session state initialization:**
```javascript
let sessionState = $json.state || {
  // ... existing fields ...
  customField: null,  // Add your field
  step: 0
};
```

2. **Update system prompt:**
Add your new field to the "Required information" list in the system message.

3. **Add extraction logic:**
```javascript
// Check for custom field
if (userMessage.includes('custom value')) {
  updatedState.customField = extractedValue;
  updatedState.step = Math.max(updatedState.step, 6);
}
```

### Multi-language Support

Update system prompt with language-specific instructions:

```javascript
const language = userMessage.match(/language:\s*(\w+)/)?.[1] || 'english';
const systemPrompt = PROMPTS[language] || PROMPTS['english'];
```

---

## 📊 Monitoring

### View Active Sessions

Sessions are stored in n8n workflow execution data:

1. Go to n8n UI
2. Click "Executions"
3. Find "Configuration Assistant" executions
4. View execution data to see session states

### Track Conversions

Count how many conversations lead to migrations:

```sql
-- In PostgreSQL
SELECT
  DATE(created_at) as date,
  COUNT(*) as migrations_started
FROM migrations
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

---

## 🚀 Next Steps

1. **Import workflow:** `0-configuration-assistant.json`
2. **Choose interface:** Web chat, OpenWebUI, or API
3. **Test it:** Start a conversation!
4. **Customize:** Adjust prompts, styling, validation
5. **Share:** Give link to team members

---

## 🆘 Need Help?

- **n8n workflow not working:** Check n8n execution logs
- **Chat interface issues:** Open browser console (F12)
- **OpenWebUI function errors:** Check OpenWebUI logs
- **Assistant giving wrong responses:** Adjust system prompt temperature

---

🤖 **Pro Tip:** The assistant learns from conversation context. If it misses something, just provide it again in the next message!
