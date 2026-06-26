from __future__ import annotations

from typing import Any, Optional

from .._transport import ZabyCoreClient
from .._util import encode_path

AGENTS = "/api/v1/provisioning/agentic-os/agents"
PROVISIONING = "/api/v1/provisioning"


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

    async def playground_runtime_tokens(self, agent_id: str, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{AGENTS}/{encode_path(agent_id)}/playground/runtime-tokens", **kwargs)

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
        return await self._core.request("GET", f"{PROVISIONING}/managed-agents/deployments/{encode_path(deployment_id)}/provisioning", **kwargs)


class ExternalAppsClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def list(self, query: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{PROVISIONING}/managed-agents/external-apps", query=query, **kwargs)

    async def create(self, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{PROVISIONING}/managed-agents/external-apps", json_body=input, **kwargs)

    async def get(self, external_app_id: str, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{PROVISIONING}/managed-agents/external-apps/{encode_path(external_app_id)}", **kwargs)

    async def update(self, external_app_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("PATCH", f"{PROVISIONING}/managed-agents/external-apps/{encode_path(external_app_id)}", json_body=input, **kwargs)

    async def bind_deployment(self, external_app_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{PROVISIONING}/managed-agents/external-apps/{encode_path(external_app_id)}/deployments", json_body=input, **kwargs)


class RuntimeTokensClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def create(self, input: Any, **kwargs: Any) -> Any:
        body = {k: v for k, v in input.items() if k != "externalAppId"}
        external_app_id = input.get("externalAppId")
        return await self._core.request("POST",
            f"/api/v1/provisioning/managed-agents/external-apps/{encode_path(external_app_id)}/runtime-tokens",
            json_body=body,
            **kwargs,
        )

    async def record_feedback(self, run_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST",
            f"/api/v1/provisioning/managed-agents/runs/{encode_path(run_id)}/feedback",
            json_body=input,
            **kwargs,
        )

    async def rotate(self, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST",
            "/api/v1/provisioning/managed-agents/runtime-tokens/rotate",
            json_body=input,
            **kwargs,
        )

    async def rotate_by_unique_id(self, input: Any, **kwargs: Any) -> Any:
        body = {k: v for k, v in input.items() if k != "externalAppId"}
        external_app_id = input.get("externalAppId")
        return await self._core.request("POST",
            f"/api/v1/provisioning/managed-agents/external-apps/{encode_path(external_app_id)}/runtime-tokens/rotate",
            json_body=body,
            **kwargs,
        )

    async def revoke_family(self, token_family_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST",
            f"/api/v1/provisioning/managed-agents/runtime-token-families/{encode_path(token_family_id)}/revoke",
            json_body=input,
            **kwargs,
        )


class RuntimeTokenFamiliesClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def list(self, query: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{PROVISIONING}/managed-agents/runtime-token-families", query=query, **kwargs)

    async def revoke(self, family_id: str, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{PROVISIONING}/managed-agents/runtime-token-families/{encode_path(family_id)}/revoke", **kwargs)


class RuntimeTokenPoliciesClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def list(self, query: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{PROVISIONING}/managed-agents/runtime-token-policies", query=query, **kwargs)

    async def create(self, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{PROVISIONING}/managed-agents/runtime-token-policies", json_body=input, **kwargs)

    async def get(self, policy_id: str, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{PROVISIONING}/managed-agents/runtime-token-policies/{encode_path(policy_id)}", **kwargs)

    async def update(self, policy_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("PATCH", f"{PROVISIONING}/managed-agents/runtime-token-policies/{encode_path(policy_id)}", json_body=input, **kwargs)


class RuntimeTokenGrantsClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def revoke(self, grant_id: str, input: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{PROVISIONING}/managed-agents/runtime-token-grants/{encode_path(grant_id)}/revoke", json_body=input, **kwargs)


class RuntimeTokenUsageClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def get(self, query: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{PROVISIONING}/managed-agents/runtime-token-usage", query=query, **kwargs)


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
