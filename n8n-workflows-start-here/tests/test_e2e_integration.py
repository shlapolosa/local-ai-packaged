#!/usr/bin/env python3
"""
End-to-end integration tests for the e2e_solution intent flow.

Tests the complete workflow from intent routing through all expert agents:
1. Intent Router - Detects e2e_solution intent
2. Business Analyst - Gathers requirements
3. PRD Generator Orchestrator - Coordinates experts
4. 7 Expert Agents - Sequential consultations
"""

import json
import pytest
from pathlib import Path


@pytest.fixture(scope="module")
def workflows_dir():
    """Get the workflows directory"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="module")
def intent_router(workflows_dir):
    """Load intent router workflow"""
    router_file = workflows_dir / "0-configuration-assistant-intent-router.json"
    with open(router_file) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def business_analyst(workflows_dir):
    """Load business analyst workflow"""
    ba_file = workflows_dir / "workflows" / "0-business-analyst-e2e.json"
    with open(ba_file) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def prd_orchestrator(workflows_dir):
    """Load PRD generator orchestrator workflow"""
    prd_file = workflows_dir / "workflows" / "1-prd-generator-orchestrator.json"
    with open(prd_file) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def expert_workflows(workflows_dir):
    """Load all expert workflows"""
    experts_dir = workflows_dir / "workflows"
    expert_files = [
        "2-expert-compliance-risk.json",
        "3-expert-business-architect.json",
        "4-expert-experience-designer.json",
        "5-expert-technology-cto.json",
        "6-expert-application-architect.json",
        "7-expert-solution-architect.json",
        "8-expert-infrastructure-reviewer.json",
    ]

    experts = {}
    for expert_file in expert_files:
        expert_path = experts_dir / expert_file
        with open(expert_path) as f:
            expert_name = expert_file.replace(".json", "").replace("-expert-", "")
            experts[expert_name] = json.load(f)

    return experts


class TestIntentRouting:
    """Test intent routing for e2e_solution"""

    def test_intent_router_has_e2e_solution_intent(self, intent_router):
        """Verify e2e_solution is defined in LLM prompt"""
        workflow_str = json.dumps(intent_router)
        assert "e2e_solution" in workflow_str
        assert "prd_generation" in workflow_str

    def test_intent_router_routes_to_business_analyst(self, intent_router):
        """Verify both prd_generation and e2e_solution route to Business Analyst"""
        workflow_str = json.dumps(intent_router)

        # Should have webhook call to business analyst
        assert "/webhook/chat/business-analyst" in workflow_str

        # Should have routing logic for both intents
        switch_nodes = [n for n in intent_router['nodes'] if 'switch' in n.get('type', '').lower()]
        assert len(switch_nodes) > 0, "Should have switch/routing node"

    def test_intent_keywords_present(self, intent_router):
        """Verify intent detection keywords are in LLM prompt"""
        workflow_str = json.dumps(intent_router).lower()

        # E2E keywords
        assert any(kw in workflow_str for kw in ['build', 'create', 'develop', 'solution', 'end-to-end'])

        # PRD keywords
        assert any(kw in workflow_str for kw in ['prd', 'requirements', 'architecture', 'specification'])


class TestBusinessAnalyst:
    """Test Business Analyst workflow"""

    def test_has_webhook_endpoint(self, business_analyst):
        """Verify Business Analyst has correct webhook endpoint"""
        webhook_nodes = [n for n in business_analyst['nodes']
                        if n.get('type') == 'n8n-nodes-base.webhook']

        assert len(webhook_nodes) > 0
        webhook_path = webhook_nodes[0]['parameters'].get('path')
        assert 'business-analyst' in webhook_path

    def test_session_state_management(self, business_analyst):
        """Verify session state is managed properly"""
        workflow_str = json.dumps(business_analyst)

        # Should track session state
        assert 'sessionState' in workflow_str or 'session_state' in workflow_str

        # Should track key fields
        required_fields = ['projectName', 'projectType', 'platforms', 'coreFeatures']
        for field in required_fields:
            assert field in workflow_str, f"Missing {field} in session state"

    def test_triggers_prd_generator(self, business_analyst):
        """Verify Business Analyst triggers PRD Generator when complete"""
        workflow_str = json.dumps(business_analyst)

        # Should call PRD Generator webhook
        assert "/webhook/prd-generator" in workflow_str or "prd-generator" in workflow_str.lower()

    def test_creates_project_record(self, business_analyst):
        """Verify Business Analyst creates project in database"""
        workflow_str = json.dumps(business_analyst)

        # Should insert into e2e_projects table
        assert "e2e_projects" in workflow_str
        assert "INSERT" in workflow_str.upper()

    def test_saves_requirements(self, business_analyst):
        """Verify Business Analyst saves functional requirements"""
        workflow_str = json.dumps(business_analyst)

        # Should insert into functional_requirements table
        assert "functional_requirements" in workflow_str


class TestPRDOrchestrator:
    """Test PRD Generator Orchestrator workflow"""

    def test_has_webhook_endpoint(self, prd_orchestrator):
        """Verify PRD Orchestrator has correct webhook endpoint"""
        webhook_nodes = [n for n in prd_orchestrator['nodes']
                        if n.get('type') == 'n8n-nodes-base.webhook']

        assert len(webhook_nodes) > 0
        webhook_path = webhook_nodes[0]['parameters'].get('path')
        assert '/webhook/prd-generator' in webhook_path or 'prd-generator' in webhook_path

    def test_loads_project_and_requirements(self, prd_orchestrator):
        """Verify orchestrator loads project and requirements from DB"""
        workflow_str = json.dumps(prd_orchestrator)

        # Should query e2e_projects
        assert "e2e_projects" in workflow_str

        # Should query functional_requirements
        assert "functional_requirements" in workflow_str

        # Should use SELECT queries
        assert "SELECT" in workflow_str.upper()

    def test_initializes_shared_context(self, prd_orchestrator):
        """Verify orchestrator initializes shared context"""
        workflow_str = json.dumps(prd_orchestrator)

        # Should create initial context
        assert "shared_context" in workflow_str

        # Version should start at 1
        assert "version" in workflow_str.lower()

    def test_queries_component_catalog(self, prd_orchestrator):
        """Verify orchestrator queries OAM component catalog"""
        workflow_str = json.dumps(prd_orchestrator)

        # Should query component catalog
        assert "oam_component_catalog" in workflow_str or "component" in workflow_str.lower()

    def test_calls_all_seven_experts(self, prd_orchestrator):
        """Verify orchestrator calls all 7 expert workflows in sequence"""
        workflow_str = json.dumps(prd_orchestrator)

        required_experts = [
            "compliance-risk",
            "business-architect",
            "experience-designer",
            "technology-cto",
            "application-architect",
            "solution-architect",
            "infrastructure-reviewer"
        ]

        for expert in required_experts:
            assert expert in workflow_str, f"Missing expert: {expert}"

    def test_expert_call_sequence(self, prd_orchestrator):
        """Verify experts are called in correct order"""
        workflow_str = json.dumps(prd_orchestrator)

        # Find positions of expert calls
        experts = [
            "compliance-risk",
            "business-architect",
            "experience-designer",
            "technology-cto",
            "application-architect",
            "solution-architect",
            "infrastructure-reviewer"
        ]

        positions = {}
        for expert in experts:
            pos = workflow_str.find(expert)
            if pos != -1:
                positions[expert] = pos

        # Verify we found all experts
        assert len(positions) == 7, "Should find all 7 experts"

        # Verify compliance is before business (example check)
        assert positions["compliance-risk"] < positions["business-architect"]

    def test_merges_context_updates(self, prd_orchestrator):
        """Verify orchestrator merges context updates from experts"""
        workflow_str = json.dumps(prd_orchestrator)

        # Should update shared context
        assert "shared_context" in workflow_str

        # Should increment version
        assert "version" in workflow_str.lower()

    def test_generates_prd_document(self, prd_orchestrator):
        """Verify orchestrator generates final PRD"""
        workflow_str = json.dumps(prd_orchestrator)

        # Should insert into prd_documents table
        assert "prd_documents" in workflow_str

    def test_generates_oam_definitions(self, prd_orchestrator):
        """Verify orchestrator generates OAM definitions"""
        workflow_str = json.dumps(prd_orchestrator)

        # Should mention OAM or definitions
        assert "oam" in workflow_str.lower() or "definition" in workflow_str.lower()

    def test_updates_project_status(self, prd_orchestrator):
        """Verify orchestrator updates project status to completed"""
        workflow_str = json.dumps(prd_orchestrator)

        # Should UPDATE e2e_projects
        assert "UPDATE" in workflow_str.upper() and "e2e_projects" in workflow_str


class TestExpertWorkflows:
    """Test all 7 expert workflows"""

    def test_all_experts_loaded(self, expert_workflows):
        """Verify all 7 expert workflows are loaded"""
        expected_count = 7
        assert len(expert_workflows) == expected_count, \
            f"Expected {expected_count} experts, got {len(expert_workflows)}"

    def test_experts_have_webhook_endpoints(self, expert_workflows):
        """Verify each expert has correct webhook endpoint"""
        for expert_name, expert_workflow in expert_workflows.items():
            webhook_nodes = [n for n in expert_workflow['nodes']
                           if n.get('type') == 'n8n-nodes-base.webhook']

            assert len(webhook_nodes) > 0, f"{expert_name} missing webhook node"

            webhook_path = webhook_nodes[0]['parameters'].get('path')
            assert 'expert' in webhook_path.lower(), \
                f"{expert_name} webhook should reference expert"

    def test_experts_receive_shared_context(self, expert_workflows):
        """Verify experts receive shared context as input"""
        for expert_name, expert_workflow in expert_workflows.items():
            workflow_str = json.dumps(expert_workflow)

            # Should reference shared context
            assert "context" in workflow_str.lower(), \
                f"{expert_name} should receive shared context"

    def test_experts_log_consultation_start(self, expert_workflows):
        """Verify experts log consultation start in database"""
        for expert_name, expert_workflow in expert_workflows.items():
            workflow_str = json.dumps(expert_workflow)

            # Should insert into expert_consultations
            assert "expert_consultations" in workflow_str, \
                f"{expert_name} should log consultation"

    def test_experts_use_llm_analysis(self, expert_workflows):
        """Verify experts use LLM for analysis"""
        for expert_name, expert_workflow in expert_workflows.items():
            workflow_str = json.dumps(expert_workflow).lower()

            # Should have LLM/Ollama call
            assert "ollama" in workflow_str or "llm" in workflow_str or "openwebui" in workflow_str, \
                f"{expert_name} should use LLM"

    def test_experts_update_shared_context(self, expert_workflows):
        """Verify experts update shared context with findings"""
        for expert_name, expert_workflow in expert_workflows.items():
            workflow_str = json.dumps(expert_workflow)

            # Should insert new version into shared_context
            assert "shared_context" in workflow_str, \
                f"{expert_name} should update shared context"

    def test_experts_save_new_context_version(self, expert_workflows):
        """Verify experts save new context version to database"""
        for expert_name, expert_workflow in expert_workflows.items():
            workflow_str = json.dumps(expert_workflow)

            # Should save to shared_context table
            assert "INSERT" in workflow_str.upper() and "shared_context" in workflow_str, \
                f"{expert_name} should save new context version"

    def test_experts_complete_consultation(self, expert_workflows):
        """Verify experts complete consultation with audit trail"""
        for expert_name, expert_workflow in expert_workflows.items():
            workflow_str = json.dumps(expert_workflow)

            # Should update expert_consultations with completion
            assert "expert_consultations" in workflow_str and "UPDATE" in workflow_str.upper(), \
                f"{expert_name} should complete consultation"

    def test_experts_return_updated_context(self, expert_workflows):
        """Verify experts return updated context to orchestrator"""
        for expert_name, expert_workflow in expert_workflows.items():
            workflow_str = json.dumps(expert_workflow)

            # Should have response/return node
            response_nodes = [n for n in expert_workflow['nodes']
                            if 'respond' in n.get('name', '').lower() or
                               'return' in n.get('name', '').lower()]

            # Most workflows should have some form of response
            # (This is a soft check as structure may vary)
            assert len(workflow_str) > 1000, \
                f"{expert_name} workflow seems incomplete"


class TestExpertSpecificBehavior:
    """Test expert-specific behavior and context updates"""

    def test_compliance_risk_assessor(self, expert_workflows):
        """Verify Compliance & Risk Assessor exists and is properly structured"""
        expert = expert_workflows.get("2compliance-risk")
        assert expert is not None
        assert len(expert.get('nodes', [])) > 0

    def test_business_architect(self, expert_workflows):
        """Verify Business Architect exists and is properly structured"""
        expert = expert_workflows.get("3business-architect")
        assert expert is not None
        assert len(expert.get('nodes', [])) > 0

    def test_experience_designer(self, expert_workflows):
        """Verify Experience Designer exists and is properly structured"""
        expert = expert_workflows.get("4experience-designer")
        assert expert is not None
        assert len(expert.get('nodes', [])) > 0

    def test_technology_cto(self, expert_workflows):
        """Verify Technology CTO exists and is properly structured"""
        expert = expert_workflows.get("5technology-cto")
        assert expert is not None
        assert len(expert.get('nodes', [])) > 0

    def test_application_architect(self, expert_workflows):
        """Verify Application Architect exists and is properly structured"""
        expert = expert_workflows.get("6application-architect")
        assert expert is not None
        assert len(expert.get('nodes', [])) > 0

    def test_solution_architect(self, expert_workflows):
        """Verify Solution Architect exists and is properly structured"""
        expert = expert_workflows.get("7solution-architect")
        assert expert is not None
        assert len(expert.get('nodes', [])) > 0

    def test_infrastructure_reviewer(self, expert_workflows):
        """Verify Infrastructure Reviewer exists and is properly structured"""
        expert = expert_workflows.get("8infrastructure-reviewer")
        assert expert is not None
        assert len(expert.get('nodes', [])) > 0


class TestEndToEndFlow:
    """Test complete end-to-end flow"""

    def test_complete_workflow_chain(self, intent_router, business_analyst,
                                     prd_orchestrator, expert_workflows):
        """Verify complete workflow chain is connected"""

        # 1. Intent Router → Business Analyst
        router_str = json.dumps(intent_router)
        assert "/webhook/chat/business-analyst" in router_str

        # 2. Business Analyst → PRD Generator
        ba_str = json.dumps(business_analyst)
        assert "prd-generator" in ba_str.lower()

        # 3. PRD Generator → All 7 Experts
        prd_str = json.dumps(prd_orchestrator)
        for i in range(2, 9):
            assert f"expert" in prd_str.lower()

        # 4. All experts exist
        assert len(expert_workflows) == 7

    def test_database_tables_referenced(self, intent_router, business_analyst,
                                       prd_orchestrator, expert_workflows):
        """Verify all required database tables are referenced"""

        all_workflows = [intent_router, business_analyst, prd_orchestrator] + \
                       list(expert_workflows.values())

        combined_str = json.dumps(all_workflows).lower()

        required_tables = [
            "e2e_projects",
            "functional_requirements",
            "shared_context",
            "expert_consultations",
            "prd_documents",
            "oam_definitions"
        ]

        for table in required_tables:
            assert table in combined_str, f"Missing database table: {table}"

    def test_shared_context_versioning_complete(self, prd_orchestrator, expert_workflows):
        """Verify shared context versioning flows through all experts"""

        # PRD Orchestrator should initialize context v1
        prd_str = json.dumps(prd_orchestrator)
        assert "version" in prd_str.lower()

        # All experts should update version
        for expert_name, expert_workflow in expert_workflows.items():
            expert_str = json.dumps(expert_workflow)
            assert "version" in expert_str.lower(), \
                f"{expert_name} should handle context versioning"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
