from __future__ import annotations

from typing import Any, Optional

from .._transport import ZabyCoreClient
from .._util import encode_path

AGENTS = "/api/v1/tenant/agents"


class AgentsClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def create(self, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", AGENTS, json_body=input, **kwargs)

    async def attach_mcp_tool(self, agent_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{AGENTS}/{encode_path(agent_id)}/mcp-tools", json_body=input, **kwargs)

    async def attach_knowledge_base(self, agent_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{AGENTS}/{encode_path(agent_id)}/knowledge-bases", json_body=input, **kwargs)

    async def attach_skill(self, agent_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{AGENTS}/{encode_path(agent_id)}/skills", json_body=input, **kwargs)

    async def publish(self, agent_id: str, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{AGENTS}/{encode_path(agent_id)}/publish", **kwargs)

    async def deploy(self, agent_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{AGENTS}/{encode_path(agent_id)}/deployments", json_body=input, **kwargs)

    async def test_run(self, agent_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{AGENTS}/{encode_path(agent_id)}/test-runs", json_body=input, **kwargs)

    async def start_run(self, agent_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{AGENTS}/{encode_path(agent_id)}/runs", json_body=input, **kwargs)

    async def get_run_progress(self, run_id: str, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{AGENTS}/runs/{encode_path(run_id)}/progress", **kwargs)

    async def list_run_events(self, run_id: str, query: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{AGENTS}/runs/{encode_path(run_id)}/events", query=query, **kwargs)


class DeploymentsClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def create(self, agent_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{AGENTS}/{encode_path(agent_id)}/deployments", json_body=input, **kwargs)

    async def get_provisioning(self, deployment_id: str, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{AGENTS}/deployments/{encode_path(deployment_id)}/provisioning", **kwargs)


class ExternalAppsClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def list(self, query: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{AGENTS}/external-apps", query=query, **kwargs)

    async def create(self, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{AGENTS}/external-apps", json_body=input, **kwargs)

    async def get(self, external_app_id: str, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{AGENTS}/external-apps/{encode_path(external_app_id)}", **kwargs)

    async def update(self, external_app_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("PATCH", f"{AGENTS}/external-apps/{encode_path(external_app_id)}", json_body=input, **kwargs)

    async def bind_deployment(self, external_app_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{AGENTS}/external-apps/{encode_path(external_app_id)}/deployments", json_body=input, **kwargs)


class RuntimeTokensClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def create(self, external_app_id: str, **kwargs: Any) -> Any:
        body = {k: v for k, v in kwargs.items() if k != "external_app_id"}
        return await self._core.request("POST",
            f"/api/v1/provisioning/managed-agents/external-apps/{encode_path(external_app_id)}/runtime-tokens",
            json_body=body,
        )

    async def record_feedback(self, run_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST",
            f"/api/v1/provisioning/managed-agents/runs/{encode_path(run_id)}/feedback",
            json_body=input,
            **kwargs,
        )


class ApprovalsClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def list(self, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{AGENTS}/approvals", **kwargs)

    async def approve(self, run_id: str, approval_id: str, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{AGENTS}/runs/{encode_path(run_id)}/approvals/{encode_path(approval_id)}/approve", **kwargs)

    async def reject(self, run_id: str, approval_id: str, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{AGENTS}/runs/{encode_path(run_id)}/approvals/{encode_path(approval_id)}/reject", **kwargs)


class UsageClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def get_agent_usage(self, query: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{AGENTS}/usage", query=query, **kwargs)
