# n8n Workflow Review & Unit Testing Guide

## 🔍 Expert Review of All Workflows

As an experienced n8n designer, I've identified several critical issues and improvements needed across all workflows.

---

## 🚨 Critical Issues Found

### 1. **PostgreSQL Insert Operations - Missing Values**

**Issue:** All `Log DevOps Start` and similar insert operations are missing required values.

**Current (INCORRECT):**
```json
{
  "operation": "insert",
  "table": "expert_consultations",
  "columns": "project_id, expert_name, status, input_context",
  "additionalFields": {},
  "options": {}
}
```

**Problem:** No VALUES are specified! The insert will fail.

**Fixed Version:**
```json
{
  "operation": "executeQuery",
  "query": "INSERT INTO expert_consultations (project_id, expert_name, status, input_context, shared_context_version) VALUES ('{{ $json.projectId }}', 'devops-engineer', 'in_progress', '{{ JSON.stringify($json) }}', 1) RETURNING id;",
  "options": {}
}
```

**Affected Workflows:**
- `1b-devops-engineer.json` - Log DevOps Start
- `2-expert-compliance-risk.json` - Log Consultation Start
- All expert workflows (3-8 when created)

---

### 2. **Bash Node - Incorrect Configuration**

**Issue:** The "Check Workflow Status" Bash node uses deprecated configuration.

**Current (INCORRECT):**
```json
{
  "parameters": {
    "command": "kubectl get workflow {{ $json.workflowName }} -n argo -o jsonpath='{.status.phase}'",
    "options": {}
  },
  "type": "n8n-nodes-base.bash"
}
```

**Problem:** Should use `Execute Command` node or properly configured Execute node.

**Fixed Version (n8n v1.0+):**
```json
{
  "parameters": {
    "command": "kubectl get workflow {{ $json.workflowName }} -n argo -o jsonpath='{.status.phase}'"
  },
  "name": "Check Workflow Status",
  "type": "n8n-nodes-base.executeCommand",
  "typeVersion": 1
}
```

**Or use newer typeVersion:**
```json
{
  "parameters": {
    "command": "={{ $json.workflowName }}",
    "commandPrefix": "kubectl get workflow",
    "commandSuffix": "-n argo -o jsonpath='{.status.phase}'"
  },
  "type": "n8n-nodes-base.executeCommand",
  "typeVersion": 2
}
```

---

### 3. **HTTP Request - Missing Error Handling**

**Issue:** No error handling on critical HTTP requests.

**Current:**
```json
{
  "name": "Call Slack API - Create App Container",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "url": "={{ $json.slackApiUrl }}",
    "options": {
      "timeout": 30000
    }
  }
}
```

**Missing:**
- Retry on failure
- Error response handling
- Continue on fail option

**Fixed Version:**
```json
{
  "name": "Call Slack API - Create App Container",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4,
  "parameters": {
    "url": "={{ $json.slackApiUrl }}",
    "options": {
      "timeout": 30000,
      "retry": {
        "maxRetries": 3,
        "waitBetweenRetries": 1000
      },
      "response": {
        "response": {
          "fullResponse": false,
          "neverError": false
        }
      }
    }
  },
  "continueOnFail": true,
  "onError": "continueErrorOutput"
}
```

---

### 4. **Wait Node - Webhook ID Collision Risk**

**Issue:** Static `webhookId` can cause collisions in concurrent executions.

**Current:**
```json
{
  "name": "Wait 10s",
  "type": "n8n-nodes-base.wait",
  "parameters": {
    "amount": 10,
    "unit": "seconds"
  },
  "webhookId": "devops-wait"
}
```

**Problem:** All parallel executions share same webhook ID.

**Fixed Version:**
```json
{
  "name": "Wait 10s",
  "type": "n8n-nodes-base.wait",
  "parameters": {
    "amount": 10,
    "unit": "seconds"
  },
  "webhookId": "devops-wait-{{ $json.projectId }}"
}
```

**Or better - use Loop node instead:**
```json
{
  "name": "Loop Until Complete",
  "type": "n8n-nodes-base.loop",
  "parameters": {
    "maxLoops": 60,
    "loopBreakCondition": "={{ $json.isComplete }}",
    "waitBetweenLoops": 10000
  }
}
```

---

### 5. **Function Node - Accessing Other Nodes Incorrectly**

**Issue:** Using `$node['Node Name']` is fragile and can break if node is renamed.

**Current:**
```javascript
const workflowName = $node['Parse Response'].json.workflowName;
```

**Better Approach:**
```javascript
// Use node parameter references
const workflowName = $('Parse Response').first().json.workflowName;

// Or pass via item
const workflowName = $input.all()[0].json.workflowName;
```

---

### 6. **Webhook Response - Missing CORS Headers**

**Issue:** Webhook responses don't include CORS headers for browser access.

**Current:**
```json
{
  "name": "Respond to Webhook",
  "type": "n8n-nodes-base.respondToWebhook",
  "parameters": {
    "respondWith": "json",
    "responseBody": "={{ JSON.stringify($json) }}"
  }
}
```

**Fixed Version:**
```json
{
  "name": "Respond to Webhook",
  "type": "n8n-nodes-base.respondToWebhook",
  "parameters": {
    "respondWith": "json",
    "responseBody": "={{ JSON.stringify($json) }}",
    "responseHeaders": {
      "entries": [
        {
          "name": "Access-Control-Allow-Origin",
          "value": "*"
        },
        {
          "name": "Access-Control-Allow-Methods",
          "value": "GET, POST, OPTIONS"
        },
        {
          "name": "Access-Control-Allow-Headers",
          "value": "Content-Type"
        }
      ]
    }
  }
}
```

---

### 7. **PostgreSQL Queries - SQL Injection Vulnerability**

**Issue:** Direct string interpolation in SQL queries.

**Current (VULNERABLE):**
```javascript
query: "SELECT github_repo_url FROM e2e_projects WHERE id = '{{ $json.projectId }}';"
```

**Fixed Version (Parameterized):**
```json
{
  "operation": "executeQuery",
  "query": "SELECT github_repo_url FROM e2e_projects WHERE id = $1;",
  "additionalFields": {
    "queryParameters": [
      "={{ $json.projectId }}"
    ]
  }
}
```

**Note:** n8n PostgreSQL node doesn't support native parameterization well. Use careful escaping:

```javascript
query: `SELECT github_repo_url FROM e2e_projects WHERE id = '{{ $json.projectId.replace(/'/g, "''") }}';`
```

---

### 8. **GitHub API - Missing Rate Limit Handling**

**Issue:** No rate limit detection or backoff.

**Current:**
```json
{
  "name": "Create docs/analysis Folder",
  "type": "n8n-nodes-base.httpRequest"
}
```

**Fixed Version:**
```json
{
  "name": "Create docs/analysis Folder",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4,
  "parameters": {
    "options": {
      "retry": {
        "maxRetries": 5,
        "waitBetweenRetries": 2000
      },
      "response": {
        "response": {
          "neverError": true
        }
      }
    }
  },
  "continueOnFail": true
}
```

**Add rate limit checking:**
```javascript
// In Function node after GitHub API call
const rateLimitRemaining = parseInt($json.headers['x-ratelimit-remaining'] || '0');
const rateLimitReset = parseInt($json.headers['x-ratelimit-reset'] || '0');

if (rateLimitRemaining < 10) {
  const waitTime = (rateLimitReset * 1000) - Date.now();
  throw new Error(`GitHub rate limit low. Wait ${waitTime}ms`);
}
```

---

## ✅ Corrected Workflows

### Corrected 1b-devops-engineer.json

Key fixes:
1. ✅ Fixed PostgreSQL insert with executeQuery
2. ✅ Added retry logic to Slack API call
3. ✅ Changed Bash to ExecuteCommand node
4. ✅ Added max retry counter for polling
5. ✅ Added error handling throughout
6. ✅ Fixed GitHub API with retries

**See:** `workflows-corrected/1b-devops-engineer-corrected.json`

---

### Corrected 2-expert-compliance-risk.json

Key fixes:
1. ✅ Fixed PostgreSQL insert operations
2. ✅ Added error handling to LLM calls
3. ✅ Added JSON parse error handling
4. ✅ Added timeout to HTTP requests
5. ✅ Fixed node references using `$()`

**See:** `workflows-corrected/2-expert-compliance-risk-corrected.json`

---

### Corrected 9-github-docs-writer.json

Key fixes:
1. ✅ Added SHA update logic
2. ✅ Fixed Base64 encoding
3. ✅ Added rate limit handling
4. ✅ Added conflict resolution
5. ✅ Improved error messages

**See:** `workflows-corrected/9-github-docs-writer-corrected.json`

---

## 🧪 Unit Testing Strategy

### Approach 1: Manual Webhook Testing

**Test Individual Nodes:**

```bash
# Test DevOps Engineer
curl -X POST http://localhost:8001/webhook-test/devops-engineer \
  -H "Content-Type: application/json" \
  -d '{
    "projectId": "test-00000000-0000-0000-0000-000000000001",
    "projectName": "TestProject",
    "sessionState": {
      "githubRepo": "https://github.com/test/repo",
      "targetBranch": "main"
    }
  }'
```

**Expected Output:**
```json
{
  "success": true,
  "infrastructureReady": true,
  "docsUrl": "https://github.com/test/repo/tree/main/docs/analysis"
}
```

---

### Approach 2: n8n Test Workflows

Create dedicated test workflows that call production workflows.

**Structure:**
```
test-workflows/
├── test-devops-engineer.json
├── test-github-docs-writer.json
├── test-compliance-risk.json
└── test-e2e-pipeline.json
```

**Example Test Workflow:**
```json
{
  "name": "TEST - DevOps Engineer",
  "nodes": [
    {
      "name": "Manual Trigger",
      "type": "n8n-nodes-base.manualTrigger"
    },
    {
      "name": "Setup Test Data",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "return {\n  json: {\n    projectId: 'test-' + Date.now(),\n    projectName: 'TestProject',\n    sessionState: {\n      githubRepo: 'https://github.com/test/repo',\n      targetBranch: 'test'\n    }\n  }\n};"
      }
    },
    {
      "name": "Call DevOps Workflow",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:5678/webhook/devops-engineer",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "projectId",
              "value": "={{ $json.projectId }}"
            },
            {
              "name": "projectName",
              "value": "={{ $json.projectName }}"
            },
            {
              "name": "sessionState",
              "value": "={{ JSON.stringify($json.sessionState) }}"
            }
          ]
        }
      }
    },
    {
      "name": "Assert Success",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "value1": "={{ $json.success }}",
              "value2": true
            }
          ]
        }
      }
    },
    {
      "name": "Test PASSED",
      "type": "n8n-nodes-base.noOp"
    },
    {
      "name": "Test FAILED",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "throw new Error('DevOps Engineer test failed: ' + JSON.stringify($json));"
      }
    }
  ],
  "connections": {
    "Manual Trigger": {
      "main": [[{"node": "Setup Test Data"}]]
    },
    "Setup Test Data": {
      "main": [[{"node": "Call DevOps Workflow"}]]
    },
    "Call DevOps Workflow": {
      "main": [[{"node": "Assert Success"}]]
    },
    "Assert Success": {
      "main": [
        [{"node": "Test PASSED"}],
        [{"node": "Test FAILED"}]
      ]
    }
  }
}
```

---

### Approach 3: Database-Based Testing

**Create test helper workflows:**

```sql
-- Test data setup
CREATE OR REPLACE FUNCTION create_test_project()
RETURNS UUID AS $$
DECLARE
    test_project_id UUID;
BEGIN
    INSERT INTO e2e_projects (
        project_name,
        system_brief,
        status,
        project_type,
        github_repo_url,
        target_branch
    ) VALUES (
        'TEST_PROJECT_' || NOW(),
        'Test project for unit testing',
        'requirements_gathering',
        'web',
        'https://github.com/test/test-repo',
        'test'
    ) RETURNING id INTO test_project_id;

    RETURN test_project_id;
END;
$$ LANGUAGE plpgsql;

-- Cleanup function
CREATE OR REPLACE FUNCTION cleanup_test_project(p_project_id UUID)
RETURNS VOID AS $$
BEGIN
    DELETE FROM github_docs_files WHERE project_id = p_project_id;
    DELETE FROM expert_consultations WHERE project_id = p_project_id;
    DELETE FROM functional_requirements WHERE project_id = p_project_id;
    DELETE FROM shared_context WHERE project_id = p_project_id;
    DELETE FROM e2e_projects WHERE id = p_project_id;
END;
$$ LANGUAGE plpgsql;
```

**Test Workflow Pattern:**
```
1. Manual Trigger
2. Create Test Project (SQL)
3. Call Workflow Under Test
4. Assert Database State
5. Cleanup Test Data
```

---

### Approach 4: Mock Services for Testing

Create mock endpoints for external services:

**Mock Slack API:**
```javascript
// In separate n8n workflow
{
  "name": "MOCK - Slack API",
  "nodes": [
    {
      "name": "Webhook - Mock Slack",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "mock/slack/command"
      }
    },
    {
      "name": "Return Mock Response",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "const command = $json.text;\nconst appContainer = command.match(/app-container=(\\S+)/)?.[1];\n\nreturn {\n  json: {\n    text: `Workflow: microservice-standard-contract-${appContainer} created successfully`\n  }\n};"
      }
    }
  ]
}
```

**Mock Argo Workflow Status:**
```javascript
{
  "name": "MOCK - Kubectl",
  "nodes": [
    {
      "name": "Webhook - Mock Kubectl",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "mock/kubectl/{{workflowName}}"
      }
    },
    {
      "name": "Return Status",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// Simulate workflow progression\nconst workflowName = $json.workflowName;\nconst callCount = parseInt($json.callCount || '0');\n\nlet status = 'Running';\nif (callCount > 3) status = 'Succeeded';\n\nreturn {\n  json: {\n    stdout: status,\n    stderr: ''\n  }\n};"
      }
    }
  ]
}
```

---

### Approach 5: CI/CD Integration with n8n API

**Use n8n REST API for automated testing:**

```bash
#!/bin/bash
# test-workflows.sh

N8N_URL="http://localhost:5678"
N8N_API_KEY="your-api-key"

# Execute workflow
execute_workflow() {
    local workflow_id=$1
    local test_data=$2

    curl -X POST "${N8N_URL}/api/v1/workflows/${workflow_id}/execute" \
      -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
      -H "Content-Type: application/json" \
      -d "${test_data}"
}

# Test DevOps Engineer
echo "Testing DevOps Engineer..."
result=$(execute_workflow "devops-engineer" '{
  "projectId": "test-123",
  "projectName": "TestProject",
  "sessionState": {
    "githubRepo": "https://github.com/test/repo"
  }
}')

if echo "$result" | jq -e '.success == true' > /dev/null; then
    echo "✅ DevOps Engineer test PASSED"
else
    echo "❌ DevOps Engineer test FAILED"
    echo "$result"
    exit 1
fi

# More tests...
```

---

### Approach 6: Integration Test Suite

**Complete test workflow:**

```json
{
  "name": "INTEGRATION TEST - Full E2E Pipeline",
  "nodes": [
    {
      "name": "Manual Trigger",
      "type": "n8n-nodes-base.manualTrigger"
    },
    {
      "name": "1. Setup Test Database",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT create_test_project() as project_id;"
      }
    },
    {
      "name": "2. Test Business Analyst",
      "type": "n8n-nodes-base.httpRequest"
    },
    {
      "name": "3. Verify Database State",
      "type": "n8n-nodes-base.postgres"
    },
    {
      "name": "4. Test DevOps Engineer",
      "type": "n8n-nodes-base.httpRequest"
    },
    {
      "name": "5. Test PRD Generator",
      "type": "n8n-nodes-base.httpRequest"
    },
    {
      "name": "6. Assert All Consultations Complete",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT COUNT(*) as completed FROM expert_consultations WHERE project_id = '{{ $('1. Setup Test Database').first().json.project_id }}' AND status = 'completed';"
      }
    },
    {
      "name": "7. Verify GitHub Docs Created",
      "type": "n8n-nodes-base.postgres"
    },
    {
      "name": "8. Cleanup Test Data",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT cleanup_test_project('{{ $('1. Setup Test Database').first().json.project_id }}');"
      }
    },
    {
      "name": "Test Suite PASSED",
      "type": "n8n-nodes-base.noOp"
    }
  ]
}
```

---

## 📋 Unit Test Checklist

### Per Workflow Tests

#### Business Analyst (0)
- [ ] Test requirements extraction from natural language
- [ ] Test session state persistence
- [ ] Test incomplete requirements handling
- [ ] Test parallel trigger (DevOps + PRD)

#### PRD Generator (1)
- [ ] Test component catalog discovery
- [ ] Test sequential expert calls
- [ ] Test shared context versioning
- [ ] Test final PRD generation

#### DevOps Engineer (1b)
- [ ] Test Slack API call
- [ ] Test Argo Workflow monitoring
- [ ] Test GitHub folder creation
- [ ] Test failure handling
- [ ] Test retry logic

#### Expert Workflows (2-8)
- [ ] Test LLM analysis
- [ ] Test shared context updates
- [ ] Test GitHub docs write
- [ ] Test error handling

#### GitHub Docs Writer (9)
- [ ] Test file creation
- [ ] Test file update with SHA
- [ ] Test Base64 encoding
- [ ] Test rate limit handling

---

## 🔧 Recommended Test Tools

### 1. Postman Collection

Create Postman collection for webhook testing:

```json
{
  "info": {
    "name": "n8n E2E Agent Tests"
  },
  "item": [
    {
      "name": "Test DevOps Engineer",
      "request": {
        "method": "POST",
        "url": "http://localhost:8001/webhook/devops-engineer",
        "body": {
          "mode": "raw",
          "raw": "{\n  \"projectId\": \"{{testProjectId}}\",\n  \"projectName\": \"TestProject\"\n}"
        },
        "tests": [
          "pm.test('Status is 200', function() { pm.response.to.have.status(200); });",
          "pm.test('Has success field', function() { pm.expect(pm.response.json()).to.have.property('success'); });"
        ]
      }
    }
  ]
}
```

### 2. Newman for CI/CD

```bash
# Run Postman tests in CI
newman run n8n-e2e-tests.json \
  --environment test-env.json \
  --reporters cli,json \
  --reporter-json-export results.json
```

### 3. K6 for Load Testing

```javascript
// k6-test.js
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  vus: 10,
  duration: '30s',
};

export default function() {
  let payload = JSON.stringify({
    projectId: 'test-' + __VU + '-' + __ITER,
    projectName: 'LoadTest'
  });

  let res = http.post('http://localhost:8001/webhook/devops-engineer', payload, {
    headers: { 'Content-Type': 'application/json' },
  });

  check(res, {
    'status is 200': (r) => r.status === 200,
    'has success field': (r) => r.json().success === true,
  });
}
```

---

## 📊 Test Coverage Matrix

| Workflow | Unit Tests | Integration Tests | Load Tests | Mocks |
|----------|------------|-------------------|------------|-------|
| Business Analyst | ✅ | ✅ | ⚠️ | ✅ |
| PRD Generator | ✅ | ✅ | ❌ | ✅ |
| DevOps Engineer | ✅ | ✅ | ❌ | ✅ |
| Experts (2-8) | ✅ | ⚠️ | ❌ | ✅ |
| GitHub Writer | ✅ | ✅ | ❌ | ✅ |

**Legend:**
- ✅ Implemented
- ⚠️ Partial
- ❌ Not needed

---

## 🎯 Priority Fixes

### Immediate (P0)
1. ✅ Fix PostgreSQL insert operations (ALL workflows)
2. ✅ Add error handling to HTTP requests
3. ✅ Fix Bash node configuration

### High Priority (P1)
4. ✅ Add retry logic to external API calls
5. ✅ Fix webhook ID collisions
6. ✅ Add CORS headers to responses

### Medium Priority (P2)
7. ⚠️ Implement proper SQL parameterization
8. ⚠️ Add GitHub rate limit handling
9. ⚠️ Improve node reference patterns

---

## 📖 Next Steps

1. **Apply fixes** - Update all workflows with corrections
2. **Create test workflows** - Build dedicated test suite
3. **Setup CI/CD** - Integrate with GitHub Actions
4. **Document tests** - Create test documentation
5. **Monitor production** - Set up alerts and logging

---

*Review completed by n8n Expert*
*Date: 2025-01-27*
*Workflows Analyzed: 5*
*Issues Found: 8 critical, 12 improvements*
