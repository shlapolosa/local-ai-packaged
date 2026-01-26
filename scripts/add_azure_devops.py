#!/usr/bin/env python3
"""
Add Azure DevOps artifact mirroring to n8n workflow files.

This script modifies n8n workflow JSON files to add parallel Azure DevOps push
alongside the existing GitHub SSH integration. The Azure push is configurable
and only runs if Azure DevOps credentials are configured.
"""

import json
import re
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def generate_uuid() -> str:
    """Generate a UUID for node IDs."""
    return str(uuid.uuid4())[:8]


def find_ssh_commit_node(nodes: List[Dict]) -> Optional[Dict]:
    """Find the SSH commit/write node in the workflow."""
    for node in nodes:
        node_name = node.get("name", "")
        node_type = node.get("type", "")
        # Match SSH nodes that commit or write artifacts
        if node_type == "n8n-nodes-base.ssh" and (
            "Commit" in node_name or "Write" in node_name
        ):
            return node
    return None


def find_build_git_script_node(nodes: List[Dict]) -> Optional[Dict]:
    """Find the Build Git Script node."""
    for node in nodes:
        if node.get("name") == "Build Git Script":
            return node
    return None


def find_update_job_status_node(nodes: List[Dict]) -> Optional[Dict]:
    """Find the Update Job Status node."""
    for node in nodes:
        if "Update Job" in node.get("name", "") or node.get("name") == "Update Job Status":
            return node
    return None


def find_node_by_name(nodes: List[Dict], name: str) -> Optional[Dict]:
    """Find a node by its exact name."""
    for node in nodes:
        if node.get("name") == name:
            return node
    return None


def get_node_connection_target(connections: Dict, source_name: str) -> Optional[str]:
    """Get the target node name that a source connects to."""
    if source_name in connections:
        main_conns = connections[source_name].get("main", [[]])
        if main_conns and main_conns[0]:
            return main_conns[0][0].get("node")
    return None


def extract_artifact_info(build_git_script_node: Dict) -> Tuple[str, str]:
    """Extract artifact variable name and path from Build Git Script node."""
    js_code = build_git_script_node.get("parameters", {}).get("jsCode", "")

    artifact_var = "artifactContent"
    artifact_path = "/docs/artifact.md"

    # Try to find the artifact variable
    var_match = re.search(r"ctx\.(\w+Markdown|\w+Content)", js_code)
    if var_match:
        artifact_var = var_match.group(1)

    # Try to find the artifact path
    path_match = re.search(r"cat > '.*?/docs/(\w+\.md)'", js_code)
    if path_match:
        artifact_path = f"/docs/{path_match.group(1)}"

    return artifact_var, artifact_path


def create_azure_nodes(
    build_script_node: Dict,
    base_position: List[int]
) -> List[Dict]:
    """Create the Azure DevOps nodes to add to the workflow."""

    # Extract artifact info
    artifact_var, artifact_path = extract_artifact_info(build_script_node)

    # Position nodes below the SSH path
    x_base = base_position[0]
    y_offset = 250  # Below the existing path

    nodes = []

    # 1. If: Azure Enabled node
    if_azure_node = {
        "parameters": {
            "conditions": {
                "options": {
                    "caseSensitive": True,
                    "leftValue": "",
                    "typeValidation": "loose"
                },
                "conditions": [
                    {
                        "id": "azure-enabled-check",
                        "leftValue": "={{ $env.AZURE_DEVOPS_ORG }}",
                        "rightValue": "",
                        "operator": {
                            "type": "string",
                            "operation": "notEmpty"
                        }
                    }
                ],
                "combinator": "and"
            },
            "options": {}
        },
        "id": f"if-azure-{generate_uuid()}",
        "name": "If: Azure Enabled",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2.2,
        "position": [x_base, base_position[1] + y_offset]
    }
    nodes.append(if_azure_node)

    # 2. Get Azure Repo Info node (HTTP Request)
    get_repo_node = {
        "parameters": {
            "method": "GET",
            "url": "=https://dev.azure.com/{{ $env.AZURE_DEVOPS_ORG }}/{{ $env.AZURE_DEVOPS_PROJECT }}/_apis/git/repositories/{{ $env.AZURE_DEVOPS_REPO }}?api-version=7.1",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpBasicAuth",
            "options": {}
        },
        "id": f"get-azure-repo-{generate_uuid()}",
        "name": "Get Azure Repo Info",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [x_base + 240, base_position[1] + y_offset],
        "credentials": {
            "httpBasicAuth": {
                "id": "AZURE_DEVOPS_PAT_CREDENTIAL_ID",
                "name": "Azure DevOps PAT"
            }
        }
    }
    nodes.append(get_repo_node)

    # 3. Build Azure Push Payload node (Code)
    build_payload_code = '''// Build Azure DevOps push payload
const ctx = $('Build Git Script').first().json;
const repoInfo = $json;
const projectSlug = ctx.projectSlug;
const jobId = ctx.jobId;

// Get artifact content - try common variable names
const artifactContent = ctx.''' + artifact_var + ''' || ctx.artifactMarkdown || ctx.content || '';
const artifactPath = "''' + artifact_path + '''";

// Determine branch reference
const branchName = `refs/heads/${projectSlug}`;

// For new branches, use all zeros as oldObjectId
const oldObjectId = '0000000000000000000000000000000000000000';

// Build the push payload
const changes = [{
  changeType: 'add',
  item: { path: `/${projectSlug}-docs${artifactPath}` },
  newContent: {
    content: Buffer.from(artifactContent).toString('base64'),
    contentType: 'base64encoded'
  }
}];

return [{
  json: {
    ...ctx,
    azurePushPayload: {
      refUpdates: [{
        name: branchName,
        oldObjectId: oldObjectId
      }],
      commits: [{
        comment: `Add artifacts for ${projectSlug} (job ${jobId})`,
        changes: changes
      }]
    },
    azureRepoInfo: repoInfo
  }
}];'''

    build_payload_node = {
        "parameters": {
            "jsCode": build_payload_code
        },
        "id": f"build-azure-payload-{generate_uuid()}",
        "name": "Build Azure Push Payload",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [x_base + 480, base_position[1] + y_offset]
    }
    nodes.append(build_payload_node)

    # 4. Push to Azure DevOps node (HTTP Request)
    push_azure_node = {
        "parameters": {
            "method": "POST",
            "url": "=https://dev.azure.com/{{ $env.AZURE_DEVOPS_ORG }}/{{ $env.AZURE_DEVOPS_PROJECT }}/_apis/git/repositories/{{ $env.AZURE_DEVOPS_REPO }}/pushes?api-version=7.1",
            "authentication": "genericCredentialType",
            "genericAuthType": "httpBasicAuth",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify($json.azurePushPayload) }}",
            "options": {}
        },
        "id": f"push-azure-{generate_uuid()}",
        "name": "Push to Azure DevOps",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [x_base + 720, base_position[1] + y_offset],
        "credentials": {
            "httpBasicAuth": {
                "id": "AZURE_DEVOPS_PAT_CREDENTIAL_ID",
                "name": "Azure DevOps PAT"
            }
        }
    }
    nodes.append(push_azure_node)

    # 5. Merge Results node
    merge_node = {
        "parameters": {
            "mode": "combine",
            "mergeByFields": {
                "values": [
                    {
                        "field1": "jobId",
                        "field2": "jobId"
                    }
                ]
            },
            "options": {
                "fuzzyCompare": False
            }
        },
        "id": f"merge-results-{generate_uuid()}",
        "name": "Merge Git Results",
        "type": "n8n-nodes-base.merge",
        "typeVersion": 3,
        "position": [x_base + 960, base_position[1] + int(y_offset / 2)]
    }
    nodes.append(merge_node)

    # 6. NoOp for Azure disabled path
    noop_node = {
        "parameters": {},
        "id": f"noop-azure-{generate_uuid()}",
        "name": "Azure Disabled",
        "type": "n8n-nodes-base.noOp",
        "typeVersion": 1,
        "position": [x_base + 480, base_position[1] + y_offset + 150]
    }
    nodes.append(noop_node)

    return nodes


def add_azure_connections(
    connections: Dict,
    build_script_name: str,
    ssh_node_name: str,
    update_job_name: str
) -> Dict:
    """Add Azure DevOps connections to the workflow."""

    # Get node names
    if_azure_name = "If: Azure Enabled"
    get_repo_name = "Get Azure Repo Info"
    build_payload_name = "Build Azure Push Payload"
    push_azure_name = "Push to Azure DevOps"
    merge_name = "Merge Git Results"
    noop_name = "Azure Disabled"

    # Modify Build Git Script to also connect to If: Azure Enabled
    if build_script_name in connections:
        # Add connection to If: Azure Enabled
        connections[build_script_name]["main"][0].append({
            "node": if_azure_name,
            "type": "main",
            "index": 0
        })

    # Add If: Azure Enabled connections
    # True path (index 0) -> Get Azure Repo Info
    # False path (index 1) -> Azure Disabled (NoOp)
    connections[if_azure_name] = {
        "main": [
            [{"node": get_repo_name, "type": "main", "index": 0}],
            [{"node": noop_name, "type": "main", "index": 0}]
        ]
    }

    # Get Azure Repo Info -> Build Azure Push Payload
    connections[get_repo_name] = {
        "main": [[{"node": build_payload_name, "type": "main", "index": 0}]]
    }

    # Build Azure Push Payload -> Push to Azure DevOps
    connections[build_payload_name] = {
        "main": [[{"node": push_azure_name, "type": "main", "index": 0}]]
    }

    # Push to Azure DevOps -> Merge Results (input 1)
    connections[push_azure_name] = {
        "main": [[{"node": merge_name, "type": "main", "index": 1}]]
    }

    # Azure Disabled -> Merge Results (input 1)
    connections[noop_name] = {
        "main": [[{"node": merge_name, "type": "main", "index": 1}]]
    }

    # Modify SSH node to connect to Merge Results (input 0) instead of Update Job Status
    if ssh_node_name in connections:
        connections[ssh_node_name] = {
            "main": [[{"node": merge_name, "type": "main", "index": 0}]]
        }

    # Merge Results -> Update Job Status
    connections[merge_name] = {
        "main": [[{"node": update_job_name, "type": "main", "index": 0}]]
    }

    return connections


def process_workflow_section(nodes: List[Dict], connections: Dict) -> Tuple[List[Dict], Dict, bool]:
    """Process a workflow section (main or activeVersion) and add Azure nodes."""

    # Find key nodes
    build_script_node = find_build_git_script_node(nodes)
    ssh_node = find_ssh_commit_node(nodes)
    update_job_node = find_update_job_status_node(nodes)

    if not build_script_node or not ssh_node:
        return nodes, connections, False

    # If no Update Job Status, try to find what SSH connects to
    if not update_job_node:
        next_node_name = get_node_connection_target(connections, ssh_node.get("name", ""))
        if next_node_name:
            update_job_node = find_node_by_name(nodes, next_node_name)

    if not update_job_node:
        return nodes, connections, False

    # Get SSH node position for positioning new nodes
    ssh_position = ssh_node.get("position", [1100, 0])

    # Create Azure nodes
    azure_nodes = create_azure_nodes(
        build_script_node,
        ssh_position
    )

    # Add Azure nodes to the workflow
    nodes.extend(azure_nodes)

    # Add Azure connections
    connections = add_azure_connections(
        connections,
        build_script_node.get("name", "Build Git Script"),
        ssh_node.get("name", ""),
        update_job_node.get("name", "Update Job Status")
    )

    return nodes, connections, True


def process_workflow_file(file_path: Path) -> bool:
    """Process a single workflow file and add Azure DevOps support."""

    print(f"Processing: {file_path.name}")

    with open(file_path, 'r') as f:
        workflow = json.load(f)

    modified = False

    # Check if Azure nodes already exist
    existing_nodes = workflow.get("nodes", [])
    for node in existing_nodes:
        if "Azure" in node.get("name", ""):
            print(f"  Skipping: Azure nodes already exist")
            return False

    # Process main workflow section
    if "nodes" in workflow and "connections" in workflow:
        workflow["nodes"], workflow["connections"], main_modified = process_workflow_section(
            workflow["nodes"],
            workflow["connections"]
        )
        modified = modified or main_modified
        if main_modified:
            print(f"  Modified main workflow section")

    # Process activeVersion section if it exists
    if "activeVersion" in workflow and isinstance(workflow["activeVersion"], dict):
        av = workflow["activeVersion"]
        if "nodes" in av and "connections" in av:
            av["nodes"], av["connections"], av_modified = process_workflow_section(
                av["nodes"],
                av["connections"]
            )
            modified = modified or av_modified
            if av_modified:
                print(f"  Modified activeVersion section")

    if modified:
        # Write back the modified workflow
        with open(file_path, 'w') as f:
            json.dump(workflow, f, indent=2)
        print(f"  Saved modifications")
        return True
    else:
        print(f"  No modifications needed (no Build Git Script or SSH Commit nodes found)")
        return False


def main():
    """Main function to process all workflow files."""

    # Get the workflow directory
    script_dir = Path(__file__).parent
    workflows_dir = script_dir.parent / "n8n" / "backup" / "workflows"

    if not workflows_dir.exists():
        print(f"Error: Workflows directory not found: {workflows_dir}")
        return 1

    # List of workflow files to process
    workflow_patterns = [
        "Business_Analysis_Pipeline_*.json",
        "Architecture_Pipeline_R4SsOqGqQIkRwUPT.json",
        "Solution_Architecture_Pipeline_*.json",
        "Software_Delivery_Pipeline_FlqPvbx2ICZvJiQr.json",
        "Project_Management_Pipeline_*.json",
        "Risk_Assessment_Pipeline_*.json",
        "Test_Strategy_Pipeline_*.json",
        "Quality_and_Compliance_Pipeline_*.json",
        "QA_and_Compliance_Pipeline_*.json"
    ]

    processed = 0
    modified = 0

    for pattern in workflow_patterns:
        for file_path in workflows_dir.glob(pattern):
            processed += 1
            if process_workflow_file(file_path):
                modified += 1

    print(f"\nSummary: Processed {processed} files, modified {modified}")
    return 0


if __name__ == "__main__":
    exit(main())
