# Troubleshooting Guide

Common issues and solutions for the n8n workflow automation platform.

---

## Table of Contents

1. [Chat Interface Issues](#chat-interface-issues)
2. [Database Connection Problems](#database-connection-problems)
3. [LLM and Ollama Issues](#llm-and-ollama-issues)
4. [Workflow Execution Errors](#workflow-execution-errors)
5. [Intent Routing Problems](#intent-routing-problems)
6. [Expert Consultation Failures](#expert-consultation-failures)
7. [GitHub Integration Issues](#github-integration-issues)
8. [Performance Problems](#performance-problems)

---

## Chat Interface Issues

### Issue: Chat Interface Shows "Error Connecting to Workflow"

**Symptoms:**
- Browser shows connection error
- No response from chat interface
- Console shows `ERR_CONNECTION_REFUSED`

**Diagnosis:**
```bash
# Check n8n is running
docker ps | grep n8n

# Check n8n logs
docker logs n8n

# Test webhook endpoint
curl -X POST http://localhost:8001/webhook/chat/assistant \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "sessionId": "test-123"}'
```

**Solutions:**

1. **Verify n8n is running:**
   ```bash
   docker ps | grep n8n
   # Should show: n8n container running on port 5678
   ```

2. **Check workflow is active:**
   - Visit: http://localhost:8001/workflows
   - Find "0 - Configuration Assistant - Intent Router"
   - Verify toggle switch is green (active)

3. **Verify PostgreSQL credentials:**
   - n8n → Credentials → PostgreSQL Main
   - Test connection

4. **Update N8N_URL in chat HTML:**
   ```html
   <!-- If n8n is not on localhost:8001, update: -->
   const N8N_URL = 'http://YOUR_N8N_HOST:8001';
   ```

5. **Serve HTML via HTTP:**
   ```bash
   # Don't open file:// URLs directly
   cd /Users/socrateshlapolosa/Development/local-ai-packaged/n8n-workflows-start-here
   python3 -m http.server 8080
   # Then: http://localhost:8080/chat-interface.html
   ```

---

### Issue: Chat Interface Shows Blank Response

**Symptoms:**
- Message sends successfully
- No response appears
- No error message

**Diagnosis:**
```bash
# Check n8n execution logs
# Visit: http://localhost:8001/executions

# Check PostgreSQL for chat session
docker exec -it db psql -U postgres -d postgres -c \
  "SELECT * FROM chat_sessions ORDER BY created_at DESC LIMIT 1;"
```

**Solutions:**

1. **Check LLM is responding:**
   ```bash
   curl http://ollama:11434/api/generate \
     -d '{"model":"qwen2.5:7b-instruct-q4_K_M","prompt":"test"}'
   ```

2. **Verify workflow execution:**
   - Go to n8n → Executions
   - Look for recent execution of Intent Router
   - Check for errors in execution log

3. **Clear browser cache:**
   - Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
   - Clear localStorage:
     ```javascript
     // In browser console:
     localStorage.clear();
     ```

---

## Database Connection Problems

### Issue: "Connection to PostgreSQL Failed"

**Symptoms:**
- n8n shows database connection error
- Workflow fails at PostgreSQL node
- Error: `ECONNREFUSED` or `password authentication failed`

**Diagnosis:**
```bash
# Test PostgreSQL connection
docker exec -it db psql -U postgres -d postgres -c "SELECT 1"

# Check PostgreSQL is running
docker ps | grep db

# Check credentials
docker exec -it db psql -U postgres -c "\du"
```

**Solutions:**

1. **Verify PostgreSQL is running:**
   ```bash
   docker ps | grep db
   # Should show: postgres container running
   ```

2. **Test connection manually:**
   ```bash
   docker exec -it db psql -U postgres -d postgres -c "SELECT 1"
   # Should return: 1
   ```

3. **Check n8n credentials configuration:**
   - n8n → Credentials → PostgreSQL Main
   - **Name:** `PostgreSQL Main` (exact match!)
   - **Host:** `db` (or your actual host)
   - **Database:** `postgres`
   - **User:** `postgres`
   - **Password:** `password` (check your .env)
   - **Port:** `5432`
   - Click "Test" button

4. **Verify schema is loaded:**
   ```bash
   docker exec -it db psql -U postgres -d postgres -c "\dt e2e_*"
   # Should show all e2e_* tables
   ```

5. **If schema missing, reload:**
   ```bash
   docker exec -i db psql -U postgres -d postgres < database/e2e-schema.sql
   ```

---

### Issue: "Table does not exist" Error

**Symptoms:**
- Error: `relation "e2e_projects" does not exist`
- Workflow fails at database query

**Diagnosis:**
```bash
# List all tables
docker exec -it db psql -U postgres -d postgres -c "\dt"

# Check specific schema
docker exec -it db psql -U postgres -d postgres -c "\dt e2e_*"
```

**Solutions:**

1. **Load database schema:**
   ```bash
   cd /Users/socrateshlapolosa/Development/local-ai-packaged/n8n-workflows-start-here
   docker exec -i db psql -U postgres -d postgres < database/e2e-schema.sql
   ```

2. **Verify tables created:**
   ```bash
   docker exec -it db psql -U postgres -d postgres -c "\dt e2e_*"
   ```

3. **Check correct database selected:**
   - Credential should point to database: `postgres` (not `template1` or other)

---

## LLM and Ollama Issues

### Issue: "LLM Request Timeout" or "No Response from Ollama"

**Symptoms:**
- Workflow hangs at LLM node
- Timeout error after 120 seconds
- No response from Ollama

**Diagnosis:**
```bash
# Check Ollama is running
curl http://ollama:11434/api/tags

# Check OpenWebUI
curl http://open-webui:8080/api/health

# List installed models
docker exec ollama ollama list
```

**Solutions:**

1. **Verify Ollama is running:**
   ```bash
   curl http://ollama:11434/api/tags
   # Should return JSON with model list
   ```

2. **Check model is installed:**
   ```bash
   docker exec ollama ollama list
   # Should show: qwen2.5:7b-instruct-q4_K_M
   ```

3. **Pull model if missing:**
   ```bash
   docker exec ollama ollama pull qwen2.5:7b-instruct-q4_K_M
   ```

4. **Increase timeout in HTTP Request nodes:**
   - Edit workflow → HTTP Request node
   - Options → Timeout: 300000 (5 minutes)

5. **Check GPU/CPU usage:**
   ```bash
   # If using GPU
   nvidia-smi

   # Check CPU usage
   top
   ```

6. **Restart Ollama if needed:**
   ```bash
   docker restart ollama
   ```

---

### Issue: "Model Not Found" Error

**Symptoms:**
- Error: `model 'qwen2.5:7b-instruct-q4_K_M' not found`
- LLM request fails immediately

**Solutions:**

1. **Pull the model:**
   ```bash
   docker exec ollama ollama pull qwen2.5:7b-instruct-q4_K_M
   ```

2. **Verify model name in workflows:**
   - Check HTTP Request nodes sending to Ollama
   - Model parameter should be: `qwen2.5:7b-instruct-q4_K_M`

3. **Use alternative model:**
   ```bash
   # If 7B model doesn't work, try smaller model
   docker exec ollama ollama pull qwen2.5:3b
   ```

---

## Workflow Execution Errors

### Issue: "Workflow Execution Failed"

**Symptoms:**
- Red error icon in n8n executions
- Workflow stops mid-execution
- Generic error message

**Diagnosis:**
1. Go to n8n → Executions
2. Click on failed execution
3. Click on red error node
4. Review error details

**Common Errors and Solutions:**

#### "Cannot read property 'json' of undefined"

**Cause:** Previous node didn't return expected data

**Solution:**
```javascript
// Use safe access with fallback
$('NodeName').first().json || {}
$('NodeName').all() || []

// Check if data exists
const data = $('NodeName').first();
if (!data) {
  return { error: 'No data from previous node' };
}
```

#### "Expression error: Cannot convert undefined to object"

**Cause:** Accessing property on undefined object

**Solution:**
```javascript
// Before:
$json.user.name

// After (safe access):
$json.user?.name || 'Unknown'
```

#### "SQL Syntax Error"

**Cause:** Malformed SQL query, often from user input

**Solution:**
```javascript
// Always escape user input:
const escapedName = '{{ $json.projectName.replace(/'/g, "''") }}';

// Use parameterized queries when possible:
INSERT INTO e2e_projects (project_name)
VALUES ($1)
```

---

### Issue: "Node Execution Timeout"

**Symptoms:**
- Workflow stops after 2 minutes
- Error: `Execution timed out`

**Solutions:**

1. **Increase workflow timeout:**
   - Workflow Settings → Execution Timeout: 3600 (1 hour)

2. **Increase node timeout:**
   - HTTP Request node → Options → Timeout: 600000 (10 minutes)

3. **Split long-running tasks:**
   - Break into multiple workflows
   - Use webhook callbacks for long operations

---

## Intent Routing Problems

### Issue: "Intent Always Detected as 'unknown'"

**Symptoms:**
- All messages route to "unknown" intent
- Never routes to PRD or migration workflows

**Diagnosis:**
```bash
# Test intent classification directly
curl -X POST http://localhost:8001/webhook/chat/assistant \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a PRD", "sessionId": "debug-123"}' \
  | jq '.detectedIntent, .confidence'
```

**Solutions:**

1. **Check LLM is working:**
   ```bash
   curl http://ollama:11434/api/generate \
     -d '{"model":"qwen2.5:7b-instruct-q4_K_M","prompt":"test"}'
   ```

2. **Verify intent classification prompt:**
   - Edit Intent Router workflow
   - Check "LLM - Classify Intent" node
   - Ensure system prompt includes all 3 intents

3. **Lower confidence threshold:**
   - Find "Route by Confidence" node
   - Lower threshold from 0.7 to 0.5

4. **Add more keywords:**
   - Edit system prompt
   - Add domain-specific keywords for your use case

---

### Issue: "Wrong Intent Detected"

**Symptoms:**
- PRD request routes to migration
- Migration request routes to PRD

**Solutions:**

1. **Add explicit keywords to message:**
   ```
   Instead of: "I want to build an app"
   Use: "I need a PRD for building a mobile app"
   ```

2. **Update LLM temperature:**
   - Edit Intent Router → LLM node
   - Lower temperature: 0.1 (more deterministic)

3. **Provide conversation history:**
   - Intent router uses last 5 messages
   - Clarify intent in follow-up messages

---

## Expert Consultation Failures

### Issue: "Expert Consultation Stuck in 'in_progress'"

**Symptoms:**
- Expert never completes
- Database shows status = 'in_progress'
- No error logged

**Diagnosis:**
```bash
# Check expert consultation status
docker exec -it db psql -U postgres -d postgres -c \
  "SELECT expert_name, status, started_at
   FROM expert_consultations
   WHERE status = 'in_progress'
   ORDER BY started_at DESC;"

# Check n8n executions for expert workflow
```

**Solutions:**

1. **Check expert workflow is active:**
   - n8n → Workflows → Find expert workflow
   - Verify toggle is green (active)

2. **Check for LLM timeout:**
   - Experts often take 2-5 minutes
   - Increase HTTP Request timeout to 600000ms (10 min)

3. **Manually mark as failed and retry:**
   ```sql
   UPDATE expert_consultations
   SET status = 'failed', error_message = 'Manual timeout reset'
   WHERE consultation_id = 'CONSULTATION_ID';

   -- Then trigger expert again via PRD Generator
   ```

4. **Check shared context is valid JSON:**
   ```sql
   SELECT context_data FROM shared_context
   WHERE project_id = 'PROJECT_ID'
   ORDER BY version DESC LIMIT 1;

   -- Should be valid JSONB
   ```

---

### Issue: "Context Version Mismatch"

**Symptoms:**
- Error: `Context version X does not match expected version Y`
- Expert consultation fails

**Solutions:**

1. **Check current context version:**
   ```sql
   SELECT MAX(version) FROM shared_context
   WHERE project_id = 'PROJECT_ID';
   ```

2. **Reset context to latest version:**
   - PRD Generator should auto-load latest version
   - If manual fix needed:
     ```sql
     UPDATE e2e_projects
     SET current_stage = 'expert_consultation'
     WHERE project_id = 'PROJECT_ID';
     ```

---

## GitHub Integration Issues

### Issue: "GitHub API Rate Limit Exceeded"

**Symptoms:**
- Error: `API rate limit exceeded for user`
- GitHub operations fail

**Solutions:**

1. **Use Personal Access Token (PAT):**
   - Create PAT with `repo` scope
   - Add to n8n credentials

2. **Wait for rate limit reset:**
   ```bash
   # Check when limit resets
   curl -H "Authorization: token YOUR_PAT" \
     https://api.github.com/rate_limit
   ```

3. **Reduce API calls:**
   - Batch operations where possible
   - Cache repository data

---

### Issue: "GitHub PR Creation Failed"

**Symptoms:**
- Error: `Resource not accessible by integration`
- No PR created

**Solutions:**

1. **Verify PAT permissions:**
   - PAT must have `repo` scope (full control)
   - For organizations: PAT owner must be org member

2. **Check repository exists:**
   ```bash
   curl -H "Authorization: token YOUR_PAT" \
     https://api.github.com/repos/owner/repo
   ```

3. **Verify branch exists:**
   - PRD Generator creates `prd-generation` branch
   - Check it was created successfully

---

## Performance Problems

### Issue: "Slow Workflow Execution"

**Symptoms:**
- Workflows take too long
- Expert consultations >10 minutes

**Solutions:**

1. **Optimize LLM parameters:**
   - Reduce max_tokens: 2000 (from 4000)
   - Use smaller model for non-critical experts

2. **Enable parallel expert execution:**
   - Modify PRD Orchestrator
   - Call non-dependent experts in parallel

3. **Add caching:**
   - Cache LLM responses for repeated queries
   - Use PostgreSQL for response cache

4. **Database query optimization:**
   - Add indexes on frequently queried columns
   - Use prepared statements

---

### Issue: "High Database Load"

**Symptoms:**
- Slow queries
- Connection pool exhausted

**Solutions:**

1. **Configure connection pooling:**
   - PostgreSQL: `max_connections = 100`
   - n8n: Use connection pooling in credentials

2. **Optimize queries:**
   ```sql
   -- Use indexes
   CREATE INDEX idx_project_status ON e2e_projects(status);

   -- Limit result sets
   SELECT * FROM e2e_projects
   ORDER BY created_at DESC
   LIMIT 10;
   ```

3. **Archive old data:**
   ```sql
   -- Move completed projects to archive table
   CREATE TABLE e2e_projects_archive AS
   SELECT * FROM e2e_projects
   WHERE status = 'completed' AND completed_at < NOW() - INTERVAL '30 days';

   DELETE FROM e2e_projects
   WHERE status = 'completed' AND completed_at < NOW() - INTERVAL '30 days';
   ```

---

## Getting Help

If issues persist:

1. **Check n8n community:** https://community.n8n.io/
2. **Review n8n logs:** `docker logs n8n`
3. **Check PostgreSQL logs:** `docker logs db`
4. **Check Ollama logs:** `docker logs ollama`

---

**Last Updated:** 2025-01-27
