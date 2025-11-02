# E2E n8n Agent Pipeline - Quick Start Guide

## 🚀 5-Minute Setup

### Prerequisites
- n8n running (http://localhost:8001)
- PostgreSQL running (docker container `db`)
- Ollama + OpenWebUI running
- Model pulled: `qwen2.5:7b-instruct-q4_K_M`

### Step 1: Database Setup (1 min)

```bash
cd /Users/socrateshlapolosa/Development/health-service-idp

# Run schema
docker exec -i db psql -U postgres -d postgres < n8n-workflows/database/e2e-schema.sql

# Verify
docker exec -it db psql -U postgres -d postgres -c "\dt e2e_*"
```

Expected output:
```
e2e_projects
functional_requirements
shared_context
expert_consultations
...
```

### Step 2: Import Workflows (2 min)

1. Open n8n: http://localhost:8001
2. Click "Workflows" → "Import from File"
3. Import these files in order:
   - `n8n-workflows/workflows/0-business-analyst-e2e.json`
   - `n8n-workflows/workflows/1-prd-generator-orchestrator.json`
   - `n8n-workflows/workflows/2-expert-compliance-risk.json`
4. Activate all workflows (toggle switch)

### Step 3: Configure PostgreSQL (1 min)

1. In n8n: Click "Credentials" → "Add Credential"
2. Search "PostgreSQL"
3. Configure:
   - **Name:** `PostgreSQL Main` (exact match required)
   - **Host:** `db`
   - **Database:** `postgres`
   - **User:** `postgres`
   - **Password:** `password`
   - **Port:** `5432`
4. Save

### Step 4: Open Chat Interface (1 min)

```bash
cd n8n-workflows/chat-interfaces
python3 -m http.server 8080
```

Then open: http://localhost:8080/business-analyst-chat.html

---

## 💬 Test Conversation

### Example 1: Mobile App

```
You: I want to build a mobile app for tracking daily habits
Assistant: Great! Let me gather some details. What would you like to name this project?

You: HabitTracker
Assistant: Perfect! Is this a mobile app, web app, or something else?

You: Mobile app for iOS and Android
Assistant: Excellent! What are the core features you want to include?

You: 1. Track daily habits, 2. Reminder notifications, 3. Progress visualization with charts, 4. Social features to share with friends
Assistant: Great features! Are there any technical or business constraints?

You: Need to launch in 3 months, budget is $50K
Assistant: Got it. Any non-functional requirements like performance or security needs?

You: Should support 10K users, need data encryption
Assistant: Perfect! Where should I deploy the OAM definitions?

You: https://github.com/myorg/habittracker
Assistant: ✅ Requirements complete! Creating project...

[PRD generation starts automatically]
```

### Example 2: Backend Service

```
You: I need a backend API for managing customer support tickets
Assistant: Sounds good! What should we call this project?

You: SupportHub
Assistant: Great! What type of project is this?

You: Backend API service
Assistant: Perfect! What are the main features?

You: REST API for tickets, email notifications, admin dashboard, ticket routing
Assistant: Excellent! Any constraints?

You: Must integrate with existing CRM, GDPR compliant
Assistant: Important! Any performance or security requirements?

You: 99.9% uptime, OAuth2 authentication, sub-200ms response time
Assistant: Where should the OAM definitions go?

You: https://github.com/myorg/support-hub
Assistant: ✅ All set! Generating PRD...
```

---

## 📊 Monitor Progress

### View Active Projects

```bash
docker exec -it db psql -U postgres -d postgres -c \
  "SELECT * FROM v_project_dashboard ORDER BY created_at DESC;"
```

### Check Expert Consultations

```bash
docker exec -it db psql -U postgres -d postgres -c \
  "SELECT expert_name, status, duration_seconds
   FROM expert_consultations
   WHERE project_id = 'YOUR_PROJECT_ID'
   ORDER BY started_at;"
```

### View Generated PRD

```bash
docker exec -it db psql -U postgres -d postgres -c \
  "SELECT markdown_content
   FROM prd_documents
   ORDER BY created_at DESC
   LIMIT 1;" \
  | less
```

---

## 🔧 Troubleshooting

### Chat Interface Shows Error

```bash
# Check n8n is running
docker ps | grep n8n

# Check Business Analyst workflow is active
# Visit: http://localhost:8001/workflows
# Verify "0 - Business Analyst" has green toggle

# Check PostgreSQL
docker exec -it db psql -U postgres -c "SELECT 1"
```

### LLM Taking Too Long

```bash
# Check Ollama
curl http://ollama:11434/api/tags

# If model missing, pull it
docker exec ollama ollama pull qwen2.5:7b-instruct-q4_K_M
```

### Database Connection Failed

```bash
# Verify credentials in n8n match:
# Name: PostgreSQL Main
# Host: db
# Database: postgres
# User: postgres
# Password: password

# Test connection
docker exec -it db psql -U postgres -d postgres -c "\dt"
```

---

## ⏭️ Next Steps

1. **Test the pipeline** - Run end-to-end test
2. **Create remaining experts** - Workflows 3-8 (see EXPERT_WORKFLOW_TEMPLATES.md)
3. **Customize prompts** - Adjust for your domain
4. **Add authentication** - Secure webhooks
5. **Integrate with migration platform** - Update intent router

---

## 📚 Full Documentation

- **Complete Guide:** `README.md`
- **Expert Templates:** `docs/EXPERT_WORKFLOW_TEMPLATES.md`
- **Implementation Summary:** `IMPLEMENTATION_SUMMARY.md`

---

**Ready in 5 minutes!** 🎉