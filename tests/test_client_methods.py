import pytest
from zaby import Zaby, ZabyRuntime
from zaby._testing import MockTransport, MockResponse
from zaby._config import configure_zaby, reset_zaby_config_for_tests, ZabyGlobalConfig


def R(method, path, status=200, json_body=None, **kw):
    return MockResponse(method, path, status=status, json_body=json_body, **kw)


def setup_function():
    reset_zaby_config_for_tests()


class TestDynamicTokenProviders:
    async def test_api_key_from_callable(self):
        transport = MockTransport([R("GET", "/api/v1/tenant/agents/usage", json_body={})])
        zaby = Zaby(api_key=lambda: "key_from_fn", transport=transport)
        await zaby.usage.get_agent_usage()
        assert transport.requests[0].headers["x-zaby-api-key"] == "key_from_fn"

    async def test_access_token_from_callable(self):
        transport = MockTransport([R("GET", "/api/v1/tenant/agents/usage", json_body={})])
        zaby = Zaby(api_key="test", access_token=lambda: "tok_from_fn", transport=transport)
        await zaby.usage.get_agent_usage()
        assert transport.requests[0].headers["authorization"] == "Bearer tok_from_fn"

    async def test_runtime_token_from_callable(self):
        transport = MockTransport([R("POST", "/api/v1/agent-runtime/runs", status=201, json_body={"runId": "r1"})])
        runtime = ZabyRuntime(token=lambda: "rt_from_fn", transport=transport)
        await runtime.runs.start(input={})
        assert transport.requests[0].headers["authorization"] == "Bearer rt_from_fn"

    async def test_api_key_from_async_callable(self):
        async def async_key():
            return "async_key"
        transport = MockTransport([R("GET", "/api/v1/tenant/agents/usage", json_body={})])
        zaby = Zaby(api_key=async_key, transport=transport)
        await zaby.usage.get_agent_usage()
        assert transport.requests[0].headers["x-zaby-api-key"] == "async_key"


class TestZabyAuthHeaders:
    async def test_sends_api_key(self):
        transport = MockTransport([R("GET", "/api/v1/tenant/agents/usage", json_body={})])
        zaby = Zaby(api_key="zaby_pk_test", transport=transport)
        await zaby.usage.get_agent_usage()
        assert transport.requests[0].headers["x-zaby-api-key"] == "zaby_pk_test"

    async def test_sends_bearer_token(self):
        transport = MockTransport([R("GET", "/api/v1/tenant/agents/usage", json_body={})])
        zaby = Zaby(api_key="test", access_token="tenant_token", transport=transport)
        await zaby.usage.get_agent_usage()
        assert transport.requests[0].headers["authorization"] == "Bearer tenant_token"


class TestZabyRuntimeAuth:
    async def test_sends_authorization_bearer(self):
        transport = MockTransport([R("POST", "/api/v1/agent-runtime/runs", status=201, json_body={"runId": "r1"})])
        runtime = ZabyRuntime(token="my_token", transport=transport)
        await runtime.runs.start(input={})
        assert transport.requests[0].headers["authorization"] == "Bearer my_token"


class TestClientRoutes:
    async def test_agents_create(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/agents", status=201, json_body={"id": "a1"})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.agents.create({"name": "test"})
        assert transport.requests[0].path == "/api/v1/tenant/agents"
        assert transport.requests[0].method == "POST"

    async def test_agents_attach_mcp_tool(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/agents/a1/mcp-tools", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.agents.attach_mcp_tool("a1", {})
        assert "/mcp-tools" in transport.requests[0].path

    async def test_agents_attach_knowledge_base(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/agents/a1/knowledge-bases", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.agents.attach_knowledge_base("a1", {})
        assert "/knowledge-bases" in transport.requests[0].path

    async def test_agents_publish(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/agents/a1/publish", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.agents.publish("a1")
        assert "/publish" in transport.requests[0].path

    async def test_agents_start_run(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/agents/a1/runs", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.agents.start_run("a1", {})
        assert "/runs" in transport.requests[0].path

    async def test_runtime_tokens_create(self):
        transport = MockTransport([R("POST",
            "/api/v1/provisioning/managed-agents/external-apps/app_1/runtime-tokens",
            status=201, json_body={"token": "tok", "tokenType": "Bearer"})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.runtime_tokens.create(external_app_id="app_1", deployment_id="dep_1", ttl_seconds=600)
        body = transport.requests[0].json_body
        assert "external_app_id" not in body
        assert body["deployment_id"] == "dep_1"
        assert body["ttl_seconds"] == 600

    async def test_mcp_list_catalog(self):
        transport = MockTransport([R("GET", "/api/v1/tenant/mcp/catalog", json_body=[])])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.mcp.list_catalog()
        assert transport.requests[0].path == "/api/v1/tenant/mcp/catalog"

    async def test_knowledge_bases_retrieve(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/knowledge-bases/kb1/retrieve", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.knowledge_bases.retrieve("kb1", {"query": "q"})
        assert transport.requests[0].path == "/api/v1/tenant/knowledge-bases/kb1/retrieve"

    async def test_memory_retrieve(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/agents/memory-retrievals", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.memory.retrieve({"text": "hello"})
        assert transport.requests[0].path == "/api/v1/tenant/agents/memory-retrievals"

    async def test_usage_get_agent_usage(self):
        transport = MockTransport([R("GET", "/api/v1/tenant/agents/usage?agentId=a1", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.usage.get_agent_usage(query={"agentId": "a1"})
        assert "agentId=a1" in transport.requests[0].path

    async def test_approvals_list(self):
        transport = MockTransport([R("GET", "/api/v1/tenant/agents/approvals", json_body=[])])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.approvals.list()
        assert transport.requests[0].path == "/api/v1/tenant/agents/approvals"


class TestRuntimeStream:
    async def test_runtime_stream_parses_sse(self):
        stream_body = 'data: {"event":"thinking","content":"..."}\n\ndata: {"event":"result","content":"done"}\n\n'
        transport = MockTransport([R("GET", "/api/v1/agent-runtime/runs/r1/aiui", body=stream_body)])
        runtime = ZabyRuntime(token="rt", transport=transport)
        events = []
        async for event in runtime.runs.stream("r1"):
            events.append(event)
        assert len(events) == 2
        assert events[0].data == {"event": "thinking", "content": "..."}


class TestExtendedClientRoutes:
    async def test_runtime_tokens_record_feedback(self):
        transport = MockTransport([R("POST", "/api/v1/provisioning/managed-agents/runs/r1/feedback", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.runtime_tokens.record_feedback("r1", {"rating": 5})
        assert transport.requests[0].path == "/api/v1/provisioning/managed-agents/runs/r1/feedback"

    async def test_deployments_create(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/agents/a1/deployments", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.deployments.create("a1", {"type": "managed"})
        assert "/deployments" in transport.requests[0].path

    async def test_deployments_get_provisioning(self):
        transport = MockTransport([R("GET", "/api/v1/tenant/agents/deployments/d1/provisioning", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.deployments.get_provisioning("d1")
        assert "/provisioning" in transport.requests[0].path

    async def test_intelligence_list_signals(self):
        transport = MockTransport([R("GET", "/api/v1/tenant/agents/intelligence/signals", json_body=[])])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.intelligence.list_signals(query={})
        assert "/intelligence/signals" in transport.requests[0].path

    async def test_intelligence_list_rollups(self):
        transport = MockTransport([R("GET", "/api/v1/tenant/agents/intelligence/rollups", json_body=[])])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.intelligence.list_rollups()
        assert "/intelligence/rollups" in transport.requests[0].path

    async def test_intelligence_list_improvements(self):
        transport = MockTransport([R("GET", "/api/v1/tenant/agents/intelligence/improvements", json_body=[])])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.intelligence.list_improvements()
        assert "/intelligence/improvements" in transport.requests[0].path

    async def test_intelligence_approve_improvement(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/agents/intelligence/improvements/c1/approve", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.intelligence.approve_improvement("c1")
        assert "/approve" in transport.requests[0].path

    async def test_memory_list_items(self):
        transport = MockTransport([R("GET", "/api/v1/tenant/agents/memory-items", json_body=[])])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.memory.list_items()
        assert "/memory-items" in transport.requests[0].path

    async def test_memory_get_item(self):
        transport = MockTransport([R("GET", "/api/v1/tenant/agents/memory-items/m1", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.memory.get_item("m1")
        assert transport.requests[0].path.endswith("/m1")

    async def test_memory_list_candidates(self):
        transport = MockTransport([R("GET", "/api/v1/tenant/agents/memory-candidates", json_body=[])])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.memory.list_candidates()
        assert "/memory-candidates" in transport.requests[0].path

    async def test_memory_approve_candidate(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/agents/memory-candidates/c1/approve", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.memory.approve_candidate("c1")
        assert "/approve" in transport.requests[0].path

    async def test_memory_disable_item(self):
        transport = MockTransport([R("PATCH", "/api/v1/tenant/agents/memory-items/m1/disable", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.memory.disable_item("m1")
        assert "/disable" in transport.requests[0].path

    async def test_memory_delete_item(self):
        transport = MockTransport([R("DELETE", "/api/v1/tenant/agents/memory-items/m1", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.memory.delete_item("m1")
        assert transport.requests[0].method == "DELETE"

    async def test_mcp_create_server(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/mcp/servers", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.mcp.create_server({"name": "s1"})
        assert "/mcp/servers" in transport.requests[0].path

    async def test_mcp_install_server(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/mcp/installations", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.mcp.install_server({"serverId": "s1"})
        assert "/mcp/installations" in transport.requests[0].path

    async def test_mcp_discover_tools(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/mcp/servers/s1/discover-tools", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.mcp.discover_tools("s1")
        assert "/discover-tools" in transport.requests[0].path

    async def test_knowledge_bases_create(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/knowledge-bases", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.knowledge_bases.create({"name": "KB"})
        assert transport.requests[0].path == "/api/v1/tenant/knowledge-bases"

    async def test_knowledge_bases_upload_text(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/knowledge-bases/kb1/documents/text", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.knowledge_bases.upload_text_document("kb1", {"content": "text"})
        assert "/documents/text" in transport.requests[0].path

    async def test_knowledge_bases_provisional_answer(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/knowledge-bases/kb1/provisional-answer", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.knowledge_bases.provisional_answer("kb1", {"query": "q"})
        assert "/provisional-answer" in transport.requests[0].path

    async def test_approvals_reject(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/agents/runs/r1/approvals/a1/reject", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.approvals.reject("r1", "a1")
        assert "/reject" in transport.requests[0].path

    async def test_runtime_approvals_reject(self):
        transport = MockTransport([R("POST", "/api/v1/agent-runtime/runs/r1/approvals/a1/reject", json_body={})])
        runtime = ZabyRuntime(token="test", transport=transport)
        await runtime.approvals.reject("r1", "a1")
        assert "/reject" in transport.requests[0].path

    async def test_runtime_runs_events(self):
        transport = MockTransport([R("GET", "/api/v1/agent-runtime/runs/r1/events", json_body=[])])
        runtime = ZabyRuntime(token="test", transport=transport)
        await runtime.runs.events("r1")
        assert "/runs/r1/events" in transport.requests[0].path

    async def test_agents_deploy(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/agents/a1/deployments", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.agents.deploy("a1", {"type": "managed"})
        assert "/deployments" in transport.requests[0].path

    async def test_agents_get_run_progress(self):
        transport = MockTransport([R("GET", "/api/v1/tenant/agents/runs/r1/progress", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.agents.get_run_progress("r1")
        assert "/progress" in transport.requests[0].path

    async def test_agents_list_run_events(self):
        transport = MockTransport([R("GET", "/api/v1/tenant/agents/runs/r1/events", json_body=[])])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.agents.list_run_events("r1")
        assert "/runs/r1/events" in transport.requests[0].path

    async def test_agents_attach_skill(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/agents/a1/skills", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.agents.attach_skill("a1", {"skill": "s1"})
        assert "/skills" in transport.requests[0].path

    async def test_external_apps_list(self):
        transport = MockTransport([R("GET", "/api/v1/tenant/agents/external-apps", json_body=[])])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.external_apps.list()
        assert "/external-apps" in transport.requests[0].path

    async def test_external_apps_get(self):
        transport = MockTransport([R("GET", "/api/v1/tenant/agents/external-apps/app1", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.external_apps.get("app1")
        assert transport.requests[0].path.endswith("/app1")

    async def test_external_apps_update(self):
        transport = MockTransport([R("PATCH", "/api/v1/tenant/agents/external-apps/app1", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.external_apps.update("app1", {"name": "new"})
        assert transport.requests[0].method == "PATCH"

    async def test_external_apps_bind_deployment(self):
        transport = MockTransport([R("POST", "/api/v1/tenant/agents/external-apps/app1/deployments", json_body={})])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.external_apps.bind_deployment("app1", {"deploymentId": "d1"})
        assert "/deployments" in transport.requests[0].path

    async def test_knowledge_bases_source_groups(self):
        transport = MockTransport([
            R("GET", "/api/v1/tenant/knowledge-bases/kb1/source-groups", json_body=[]),
            R("POST", "/api/v1/tenant/knowledge-bases/kb1/source-groups", json_body={}),
            R("PATCH", "/api/v1/tenant/knowledge-bases/kb1/source-groups/sg1", json_body={}),
        ])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.knowledge_bases.list_source_groups("kb1")
        await zaby.knowledge_bases.create_source_group("kb1", {"name": "sg"})
        await zaby.knowledge_bases.update_source_group("kb1", "sg1", {"name": "new"})
        assert "/source-groups" in transport.requests[0].path

    async def test_knowledge_bases_sources_crud(self):
        transport = MockTransport([
            R("POST", "/api/v1/tenant/knowledge-bases/kb1/sources", json_body={}),
            R("POST", "/api/v1/tenant/knowledge-bases/kb1/sources/s1/reprocess", json_body={}),
        ])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.knowledge_bases.create_source("kb1", {"url": "https://example.com"})
        await zaby.knowledge_bases.reprocess_source("kb1", "s1")
        assert transport.requests[0].method == "POST"

    async def test_knowledge_bases_ingestion_policies(self):
        transport = MockTransport([
            R("GET", "/api/v1/tenant/knowledge-bases/kb1/ingestion-policies", json_body=[]),
            R("POST", "/api/v1/tenant/knowledge-bases/kb1/ingestion-policies", json_body={}),
        ])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.knowledge_bases.list_ingestion_policies("kb1")
        await zaby.knowledge_bases.create_ingestion_policy("kb1", {"schedule": "daily"})
        assert "/ingestion-policies" in transport.requests[1].path

    async def test_knowledge_bases_profiles(self):
        transport = MockTransport([R("GET", "/api/v1/tenant/knowledge-bases/kb1/profiles", json_body=[])])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.knowledge_bases.list_profiles("kb1")
        assert "/profiles" in transport.requests[0].path

    async def test_knowledge_bases_jobs(self):
        transport = MockTransport([
            R("GET", "/api/v1/tenant/knowledge-bases/kb1/idocs-jobs", json_body=[]),
            R("GET", "/api/v1/tenant/knowledge-bases/kb1/idocs-jobs/j1", json_body={}),
            R("POST", "/api/v1/tenant/knowledge-bases/kb1/idocs-jobs/j1/cancel", json_body={}),
        ])
        zaby = Zaby(api_key="test", transport=transport)
        await zaby.knowledge_bases.list_jobs("kb1")
        await zaby.knowledge_bases.get_job("kb1", "j1")
        await zaby.knowledge_bases.cancel_job("kb1", "j1")
        assert "/idocs-jobs" in transport.requests[0].path
        assert transport.requests[1].path.endswith("/j1")
        assert "/cancel" in transport.requests[2].path

    async def test_client_surface_no_extra_methods(self):
        transport = MockTransport()
        zaby = Zaby(api_key="pk_test", transport=transport)
        assert not hasattr(zaby.deployments, "list")
        assert not hasattr(zaby.runtime_tokens, "list")
        assert not hasattr(zaby.memory, "query")
        assert not hasattr(zaby.intelligence, "query")
        runtime = ZabyRuntime(token="rt_test", transport=transport)
        assert not hasattr(runtime.approvals, "list")


class TestRuntimeClientRoutes:
    async def test_runtime_runs_start(self):
        transport = MockTransport([R("POST", "/api/v1/agent-runtime/runs", status=201, json_body={"runId": "r1"})])
        runtime = ZabyRuntime(token="test", transport=transport)
        await runtime.runs.start(input={})
        assert transport.requests[0].path == "/api/v1/agent-runtime/runs"

    async def test_runtime_feedback_create(self):
        transport = MockTransport([R("POST", "/api/v1/agent-runtime/runs/r1/feedback", json_body={})])
        runtime = ZabyRuntime(token="test", transport=transport)
        await runtime.feedback.create("r1", {"rating": 5})
        assert "/feedback" in transport.requests[0].path

    async def test_runtime_approvals_approve(self):
        transport = MockTransport([R("POST", "/api/v1/agent-runtime/runs/r1/approvals/a1/approve", json_body={})])
        runtime = ZabyRuntime(token="test", transport=transport)
        await runtime.approvals.approve("r1", "a1")
        assert "/approve" in transport.requests[0].path


class TestPublicExports:
    def test_all_expected_symbols(self):
        from zaby import (
            configure_zaby, reset_zaby_config_for_tests,
            DEFAULT_ZABY_API_ORIGIN, LOCAL_ZABY_API_ORIGIN,
            Zaby, ZabyRuntime,
            ZabyApiError, ZabyAuthError, ZabyPermissionError,
            ZabyRateLimitError, ZabyRuntimeTokenExhaustedError,
            ZabyRuntimeTokenExpiredError, ZabyStreamError, ZabyValidationError,
            create_zaby_api_error, MockTransport, MockResponse,
        )
        assert callable(configure_zaby)
        assert callable(Zaby)
        assert callable(ZabyRuntime)
        assert DEFAULT_ZABY_API_ORIGIN == "https://genapi.zaby.io"
        assert LOCAL_ZABY_API_ORIGIN == "http://localhost:9080"


class TestIntegration:
    async def test_client_surface(self):
        transport = MockTransport()
        zaby = Zaby(api_key="pk_test", transport=transport)
        assert hasattr(zaby, "health")
        assert hasattr(zaby, "agents")
        assert hasattr(zaby, "deployments")
        assert hasattr(zaby, "external_apps")
        assert hasattr(zaby, "runtime_tokens")
        assert hasattr(zaby, "knowledge_bases")
        assert hasattr(zaby, "mcp")
        assert hasattr(zaby, "memory")
        assert hasattr(zaby, "intelligence")
        assert hasattr(zaby, "approvals")
        assert hasattr(zaby, "usage")

    async def test_runtime_client_surface(self):
        transport = MockTransport()
        runtime = ZabyRuntime(token="rt_test", transport=transport)
        assert hasattr(runtime, "runs")
        assert hasattr(runtime, "approvals")
        assert hasattr(runtime, "feedback")

    async def test_health_check_sends_request_id(self):
        transport = MockTransport([R("GET", "/health", json_body={"status": "ok"})])
        zaby = Zaby(api_key="pk", transport=transport)
        await zaby.health.check(request_id="req_abc")
        assert transport.requests[0].headers["x-request-id"] == "req_abc"
