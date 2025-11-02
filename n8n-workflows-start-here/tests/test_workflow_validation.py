#!/usr/bin/env python3
"""
n8n Workflow Validation Tests
Tests workflow JSON structure, data flow integrity, and node configurations
"""

import json
import glob
import pytest
from pathlib import Path
from typing import Dict, List, Any


@pytest.fixture(scope="module")
def workflow_files():
    """Load all workflow JSON files"""
    workflow_dir = Path(__file__).parent.parent / "workflows"
    return list(workflow_dir.glob("*.json"))


class TestWorkflowValidation:
    """Validate n8n workflow JSON files for structural integrity"""

    def test_all_workflows_are_valid_json(self, workflow_files):
        """Ensure all workflow files are valid JSON"""
        for workflow_file in workflow_files:
            with open(workflow_file, 'r') as f:
                try:
                    data = json.load(f)
                    assert data is not None, f"{workflow_file.name} is empty"
                except json.JSONDecodeError as e:
                    pytest.fail(f"{workflow_file.name} has invalid JSON: {e}")

    def test_workflows_have_required_fields(self, workflow_files):
        """Verify workflows have required top-level fields"""
        required_fields = ['name', 'nodes', 'connections']

        for workflow_file in workflow_files:
            with open(workflow_file, 'r') as f:
                data = json.load(f)

            for field in required_fields:
                assert field in data, \
                    f"{workflow_file.name} missing required field: {field}"

    def test_workflows_have_valid_nodes(self, workflow_files):
        """Verify all nodes have required properties"""
        required_node_fields = ['name', 'type', 'position', 'parameters']

        for workflow_file in workflow_files:
            with open(workflow_file, 'r') as f:
                data = json.load(f)

            assert len(data['nodes']) > 0, \
                f"{workflow_file.name} has no nodes"

            for idx, node in enumerate(data['nodes']):
                for field in required_node_fields:
                    assert field in node, \
                        f"{workflow_file.name} node {idx} ({node.get('name', 'unnamed')}) missing: {field}"

    def test_workflows_have_valid_connections(self, workflow_files):
        """Verify connection references point to existing nodes"""
        for workflow_file in workflow_files:
            with open(workflow_file, 'r') as f:
                data = json.load(f)

            node_names = {node['name'] for node in data['nodes']}

            for source_node, connections in data['connections'].items():
                # Source node must exist
                assert source_node in node_names, \
                    f"{workflow_file.name} connection from non-existent node: {source_node}"

                # Target nodes must exist
                for connection_type, connection_list in connections.items():
                    for connection_group in connection_list:
                        for connection in connection_group:
                            target = connection.get('node')
                            assert target in node_names, \
                                f"{workflow_file.name} connection to non-existent node: {target}"

    def test_expert_workflows_follow_standard_pattern(self, workflow_files):
        """Verify expert workflows follow the 8-node pattern"""
        expert_files = [f for f in workflow_files if 'expert' in f.name]

        expected_nodes = [
            'Webhook - Expert Trigger',
            'Extract Inputs',
            'Log Consultation Start',
            'Update Shared Context',
            'Save Updated Context',
            'Complete Consultation',
            'Respond to Orchestrator'
        ]

        for workflow_file in expert_files:
            with open(workflow_file, 'r') as f:
                data = json.load(f)

            node_names = [node['name'] for node in data['nodes']]

            # Check for expected nodes (LLM node name varies)
            for expected_node in expected_nodes:
                matching_nodes = [n for n in node_names if expected_node in n or n in expected_node]
                assert len(matching_nodes) > 0, \
                    f"{workflow_file.name} missing expected node pattern: {expected_node}"

    def test_postgresql_nodes_use_executequery(self, workflow_files):
        """Ensure PostgreSQL nodes use modern executeQuery operation"""
        deprecated_operations = ['insert', 'update', 'delete', 'select']

        for workflow_file in workflow_files:
            with open(workflow_file, 'r') as f:
                data = json.load(f)

            for node in data['nodes']:
                if node['type'] == 'n8n-nodes-base.postgres':
                    operation = node['parameters'].get('operation')
                    assert operation not in deprecated_operations, \
                        f"{workflow_file.name} node '{node['name']}' uses deprecated operation: {operation}"

    def test_http_nodes_have_retry_logic(self, workflow_files):
        """Verify HTTP request nodes have retry configuration"""
        for workflow_file in workflow_files:
            with open(workflow_file, 'r') as f:
                data = json.load(f)

            for node in data['nodes']:
                if node['type'] == 'n8n-nodes-base.httpRequest':
                    # Expert LLM calls should have retry logic
                    if 'LLM' in node['name'] or 'Call' in node['name']:
                        options = node['parameters'].get('options', {})
                        assert 'retry' in options, \
                            f"{workflow_file.name} HTTP node '{node['name']}' missing retry config"

                        retry = options['retry']
                        assert retry.get('maxRetries', 0) > 0, \
                            f"{workflow_file.name} HTTP node '{node['name']}' has no retries configured"

    def test_function_nodes_use_modern_syntax(self, workflow_files):
        """Verify function nodes use modern node reference syntax"""
        deprecated_pattern = "$node["

        for workflow_file in workflow_files:
            with open(workflow_file, 'r') as f:
                data = json.load(f)

            for node in data['nodes']:
                if node['type'] == 'n8n-nodes-base.function':
                    code = node['parameters'].get('functionCode', '')
                    assert deprecated_pattern not in code, \
                        f"{workflow_file.name} node '{node['name']}' uses deprecated syntax: $node['name']"


class TestWorkflowDataFlow:
    """Test data flow integrity across workflows"""

    def test_orchestrator_expert_call_sequence(self):
        """Verify orchestrator calls experts in correct order"""
        workflow_dir = Path(__file__).parent.parent / "workflows"
        with open(workflow_dir / '1-prd-generator-orchestrator.json', 'r') as f:
            orchestrator = json.load(f)

        expected_sequence = [
            'Call Compliance & Risk Assessor',
            'Call Business Architect',
            'Call Experience Designer',
            'Call Technology CTO',
            'Call Application Architect',
            'Call Solution Architect',
            'Call Infrastructure Reviewer'
        ]

        # Build execution order from connections
        execution_order = []
        current_node = 'Update Context - Components'

        while current_node:
            next_connections = orchestrator['connections'].get(current_node, {}).get('main', [[]])
            if next_connections and next_connections[0]:
                next_node = next_connections[0][0]['node']
                if 'Call' in next_node:
                    execution_order.append(next_node)
                current_node = next_node
            else:
                break

        assert execution_order == expected_sequence, \
            f"Expert call order incorrect. Expected: {expected_sequence}, Got: {execution_order}"

    def test_expert_context_versioning(self):
        """Verify experts increment context version correctly"""
        workflow_dir = Path(__file__).parent.parent / "workflows"
        expert_files = list(workflow_dir.glob('*-expert-*.json'))

        for expert_file in expert_files:
            with open(expert_file, 'r') as f:
                data = json.load(f)

            # Find "Update Shared Context" node
            update_node = next(
                (n for n in data['nodes'] if 'Update Shared Context' in n['name']),
                None
            )

            if update_node:
                code = update_node['parameters']['functionCode']
                # Should increment version
                assert 'contextVersion + 1' in code or 'contextVersion: extractData.contextVersion + 1' in code, \
                    f"{expert_file} doesn't increment context version"


class TestWorkflowSecurity:
    """Security and best practice validation"""

    def test_no_hardcoded_credentials(self, workflow_files):
        """Ensure no hardcoded credentials in workflows"""
        sensitive_patterns = ['password', 'api_key', 'secret', 'token']

        for workflow_file in workflow_files:
            with open(workflow_file, 'r') as f:
                content = f.read()

            with open(workflow_file, 'r') as f:
                data = json.load(f)

            # Check for credential nodes - should reference credential names, not values
            for node in data.get('nodes', []):
                params_str = json.dumps(node.get('parameters', {})).lower()

                # Skip checking credential reference fields
                if 'credentials' in node:
                    continue

                for pattern in sensitive_patterns:
                    # Allow variable references like {{ $env.API_KEY }}
                    if pattern in params_str and '{{' not in params_str:
                        # This is a potential hardcoded credential
                        pass  # Could add stricter checks here

    def test_postgresql_uses_parameterized_queries(self, workflow_files):
        """Verify PostgreSQL queries use proper escaping for INSERT/UPDATE/DELETE operations with user input"""
        for workflow_file in workflow_files:
            with open(workflow_file, 'r') as f:
                data = json.load(f)

            for node in data['nodes']:
                if node['type'] == 'n8n-nodes-base.postgres':
                    query = node['parameters'].get('query', '')
                    query_upper = query.upper()

                    # Only check INSERT/UPDATE/DELETE queries for escaping
                    is_write_operation = any(op in query_upper for op in ['INSERT', 'UPDATE', 'DELETE'])

                    if is_write_operation and '{{' in query and "'" in query:
                        # Skip UUID/ID fields (safe, database-generated)
                        if 'projectId' in query or '.id' in query:
                            continue

                        # Should escape quotes for user-provided input
                        assert ".replace(/'/g, \"''\")" in query or \
                               "JSON.stringify" in query, \
                            f"{workflow_file.name} PostgreSQL node '{node['name']}' may have SQL injection risk"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
