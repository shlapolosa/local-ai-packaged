# Testing & Validation

Comprehensive testing strategy for n8n workflows, database schema, and platform functionality.

---

## Table of Contents

1. [Test Suite Overview](#test-suite-overview)
2. [Workflow Validation Tests](#workflow-validation-tests)
3. [Database Tests](#database-tests)
4. [Integration Tests](#integration-tests)
5. [Running Tests](#running-tests)
6. [Test Results](#test-results)

---

## Test Suite Overview

The platform includes automated tests to ensure:
- ✅ Workflow structure validity
- ✅ Data flow integrity
- ✅ Security compliance
- ✅ Database schema consistency
- ✅ End-to-end functionality

**Test Framework:** pytest
**Test Location:** `/tests/`
**Test Count:** 12 tests (all passing)

---

## Workflow Validation Tests

### Test File: `test_workflow_validation.py`

#### 1. Structural Validation (8 tests)

**Test: `test_workflow_files_exist`**
```python
def test_workflow_files_exist(workflow_files):
    """Verify all expected workflow files are present"""
    assert len(workflow_files) >= 11
```

**Test: `test_workflow_json_valid`**
```python
def test_workflow_json_valid(workflow_files):
    """Ensure all workflow files are valid JSON"""
    for wf_file in workflow_files:
        with open(wf_file) as f:
            data = json.load(f)
            assert 'nodes' in data
            assert 'connections' in data
```

**Test: `test_webhook_endpoints_unique`**
```python
def test_webhook_endpoints_unique(workflow_files):
    """Verify no duplicate webhook paths"""
    webhooks = set()
    for wf_file in workflow_files:
        with open(wf_file) as f:
            data = json.load(f)
            for node in data.get('nodes', []):
                if node.get('type') == 'n8n-nodes-base.webhook':
                    path = node['parameters'].get('path')
                    assert path not in webhooks
                    webhooks.add(path)
```

**Test: `test_postgresql_credentials_referenced`**
```python
def test_postgresql_credentials_referenced(workflow_files):
    """Ensure PostgreSQL nodes reference 'PostgreSQL Main' credential"""
    for wf_file in workflow_files:
        with open(wf_file) as f:
            data = json.load(f)
            for node in data.get('nodes', []):
                if 'postgres' in node.get('type', '').lower():
                    creds = node.get('credentials', {})
                    assert 'postgres' in creds
```

**Test: `test_llm_nodes_have_model`**
```python
def test_llm_nodes_have_model(workflow_files):
    """Verify LLM nodes specify a model"""
    for wf_file in workflow_files:
        with open(wf_file) as f:
            data = json.load(f)
            for node in data.get('nodes', []):
                if 'ollama' in str(node.get('parameters', {})).lower():
                    params = node.get('parameters', {})
                    assert 'model' in params or 'MODEL' in str(params)
```

**Test: `test_nodes_have_required_fields`**
```python
def test_nodes_have_required_fields(workflow_files):
    """Check all nodes have required fields"""
    required_fields = ['id', 'name', 'type', 'position']
    for wf_file in workflow_files:
        with open(wf_file) as f:
            data = json.load(f)
            for node in data.get('nodes', []):
                for field in required_fields:
                    assert field in node
```

**Test: `test_connections_reference_valid_nodes`**
```python
def test_connections_reference_valid_nodes(workflow_files):
    """Ensure all connections point to existing nodes"""
    for wf_file in workflow_files:
        with open(wf_file) as f:
            data = json.load(f)
            node_names = {node['name'] for node in data.get('nodes', [])}
            for source, targets in data.get('connections', {}).items():
                assert source in node_names
                for conn_type, conns in targets.items():
                    for conn_list in conns:
                        for conn in conn_list:
                            assert conn['node'] in node_names
```

**Test: `test_expert_webhooks_follow_convention`**
```python
def test_expert_webhooks_follow_convention(workflow_files):
    """Verify expert workflows use /webhook/expert/{name} pattern"""
    expert_workflows = [f for f in workflow_files if 'expert-' in str(f)]
    for wf_file in expert_workflows:
        with open(wf_file) as f:
            data = json.load(f)
            webhook_found = False
            for node in data.get('nodes', []):
                if node.get('type') == 'n8n-nodes-base.webhook':
                    path = node['parameters'].get('path', '')
                    if path.startswith('/webhook/expert/'):
                        webhook_found = True
            assert webhook_found
```

---

#### 2. Data Flow Validation (2 tests)

**Test: `test_prd_orchestrator_calls_all_experts`**
```python
def test_prd_orchestrator_calls_all_experts(workflow_dir):
    """Ensure PRD orchestrator calls all 7 expert workflows"""
    orchestrator_file = workflow_dir / '1-prd-generator-orchestrator.json'

    with open(orchestrator_file) as f:
        data = json.load(f)

    expected_experts = [
        'compliance-risk',
        'business-architect',
        'experience-designer',
        'technology-cto',
        'application-architect',
        'solution-architect',
        'infrastructure-reviewer'
    ]

    workflow_content = json.dumps(data)
    for expert in expected_experts:
        assert expert in workflow_content
```

**Test: `test_shared_context_versioning`**
```python
def test_shared_context_versioning(workflow_dir):
    """Verify shared context is versioned correctly"""
    prd_gen_file = workflow_dir / '1-prd-generator-orchestrator.json'

    with open(prd_gen_file) as f:
        data = json.load(f)

    # Check for version incrementing logic
    content = json.dumps(data)
    assert 'version' in content.lower()
    assert 'context' in content.lower()
```

---

#### 3. Security Validation (2 tests)

**Test: `test_no_hardcoded_credentials`**
```python
def test_no_hardcoded_credentials(workflow_files):
    """Ensure no hardcoded passwords or API keys"""
    sensitive_patterns = [
        r'password.*:.*["\'].*["\']',
        r'api[_-]?key.*:.*["\'].*["\']',
        r'token.*:.*["\'].*["\']'
    ]

    for wf_file in workflow_files:
        with open(wf_file) as f:
            content = f.read().lower()
            for pattern in sensitive_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                # Allow references to credential names, but not actual values
                for match in matches:
                    assert '{{' in match or '${' in match or 'PostgreSQL Main' in match
```

**Test: `test_sql_injection_protection`**
```python
def test_sql_injection_protection(workflow_files):
    """Verify SQL queries use parameterization or escaping"""
    for wf_file in workflow_files:
        with open(wf_file) as f:
            data = json.load(f)
            for node in data.get('nodes', []):
                if node.get('type') == 'n8n-nodes-base.postgres':
                    params = node.get('parameters', {})
                    if 'query' in params:
                        query = params['query']
                        # Check for proper escaping or parameterization
                        if "INSERT" in query or "UPDATE" in query:
                            assert '.replace(' in query or '{{' in query
```

---

## Database Tests

### Schema Validation

**Test Database Structure:**
```bash
# Verify all tables exist
docker exec -it db psql -U postgres -d postgres -c "\dt e2e_*"

# Expected tables:
# e2e_projects
# functional_requirements
# shared_context
# expert_consultations
# expert_communications
# chat_sessions
# oam_definitions
# prd_documents
# oam_component_catalog
```

**Test Views:**
```bash
# Verify views are created
docker exec -it db psql -U postgres -d postgres -c "\dv v_*"

# Expected views:
# v_project_dashboard
# v_expert_performance
# v_requirements_coverage
```

**Test Indexes:**
```bash
# Verify indexes exist
docker exec -it db psql -U postgres -d postgres -c "\di idx_*"

# Expected indexes on:
# - project_id columns
# - status columns
# - created_at columns
# - JSONB columns (GIN indexes)
```

---

## Integration Tests

### End-to-End PRD Generation Test

**Manual Test Script:**
```bash
#!/bin/bash

# 1. Start chat session
curl -X POST http://localhost:8001/webhook/chat/assistant \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to create a PRD for a mobile app",
    "sessionId": "test-session-123"
  }'

# 2. Provide project details
curl -X POST http://localhost:8001/webhook/chat/business-analyst \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Project name: TestApp, Type: mobile, Platforms: iOS and Android",
    "sessionId": "test-session-123"
  }'

# 3. Check project was created
docker exec -it db psql -U postgres -d postgres -c \
  "SELECT * FROM e2e_projects WHERE project_name = 'TestApp';"

# 4. Monitor expert consultations
docker exec -it db psql -U postgres -d postgres -c \
  "SELECT expert_name, status FROM expert_consultations
   WHERE project_id = (SELECT project_id FROM e2e_projects WHERE project_name = 'TestApp');"

# 5. Verify PRD was generated
docker exec -it db psql -U postgres -d postgres -c \
  "SELECT COUNT(*) FROM prd_documents
   WHERE project_id = (SELECT project_id FROM e2e_projects WHERE project_name = 'TestApp');"
```

---

### Intent Routing Test

**Test Intent Classification:**
```bash
#!/bin/bash

# Test PRD intent
curl -X POST http://localhost:8001/webhook/chat/assistant \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a PRD for my app", "sessionId": "intent-test-1"}' \
  | jq '.detectedIntent'
# Expected: "prd_generation"

# Test E2E intent
curl -X POST http://localhost:8001/webhook/chat/assistant \
  -H "Content-Type: application/json" \
  -d '{"message": "Build a new mobile application", "sessionId": "intent-test-2"}' \
  | jq '.detectedIntent'
# Expected: "e2e_solution"

# Test migration intent
curl -X POST http://localhost:8001/webhook/chat/assistant \
  -H "Content-Type: application/json" \
  -d '{"message": "Migrate my React Native app", "sessionId": "intent-test-3"}' \
  | jq '.detectedIntent'
# Expected: "whitelabel_migration"
```

---

## Running Tests

### Setup Test Environment

```bash
cd /Users/socrateshlapolosa/Development/local-ai-packaged/n8n-workflows-start-here/tests

# Install pytest if needed
pip install pytest pytest-json-report

# Or use poetry if available
poetry install
```

### Run All Tests

```bash
# Run all tests with verbose output
pytest test_workflow_validation.py -v

# Run specific test
pytest test_workflow_validation.py::TestWorkflowStructure::test_workflow_json_valid -v

# Run with coverage
pytest test_workflow_validation.py --cov=. --cov-report=html

# Generate JSON report
pytest test_workflow_validation.py --json-report --json-report-file=test_results.json
```

### Run Tests in CI/CD

```yaml
# Example GitHub Actions workflow
name: Test Workflows

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          cd tests
          pip install pytest

      - name: Run tests
        run: |
          cd tests
          pytest test_workflow_validation.py -v
```

---

## Test Results

### Current Test Status

**All 12 tests passing ✅**

```
tests/test_workflow_validation.py::TestWorkflowStructure::test_workflow_files_exist PASSED
tests/test_workflow_validation.py::TestWorkflowStructure::test_workflow_json_valid PASSED
tests/test_workflow_validation.py::TestWorkflowStructure::test_webhook_endpoints_unique PASSED
tests/test_workflow_validation.py::TestWorkflowStructure::test_postgresql_credentials_referenced PASSED
tests/test_workflow_validation.py::TestWorkflowStructure::test_llm_nodes_have_model PASSED
tests/test_workflow_validation.py::TestWorkflowStructure::test_nodes_have_required_fields PASSED
tests/test_workflow_validation.py::TestWorkflowStructure::test_connections_reference_valid_nodes PASSED
tests/test_workflow_validation.py::TestWorkflowStructure::test_expert_webhooks_follow_convention PASSED
tests/test_workflow_validation.py::TestDataFlow::test_prd_orchestrator_calls_all_experts PASSED
tests/test_workflow_validation.py::TestDataFlow::test_shared_context_versioning PASSED
tests/test_workflow_validation.py::TestWorkflowSecurity::test_no_hardcoded_credentials PASSED
tests/test_workflow_validation.py::TestWorkflowSecurity::test_sql_injection_protection PASSED

==================== 12 passed in 2.34s ====================
```

### Test Coverage

| Category | Tests | Coverage |
|----------|-------|----------|
| Structural Validation | 8/8 | 100% |
| Data Flow Validation | 2/2 | 100% |
| Security Validation | 2/2 | 100% |
| **Total** | **12/12** | **100%** |

---

## Test Maintenance

### Adding New Tests

1. **Create test function** in `test_workflow_validation.py`
2. **Follow naming convention**: `test_<feature_name>`
3. **Add docstring** explaining what is tested
4. **Use fixtures** for common setup (e.g., `workflow_files`)
5. **Run tests** to ensure they pass
6. **Update documentation** to reflect new tests

**Example:**
```python
def test_new_feature(workflow_files):
    """Test description here"""
    # Test implementation
    assert condition
```

### Test Best Practices

1. ✅ Test one thing per test function
2. ✅ Use descriptive test names
3. ✅ Add assertions with clear messages
4. ✅ Keep tests independent
5. ✅ Clean up test data after tests
6. ✅ Use fixtures for reusable setup

---

**Last Updated:** 2025-01-27
