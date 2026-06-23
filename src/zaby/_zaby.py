from __future__ import annotations

from typing import Any, Callable, Optional, Union

from ._config import ZabyGlobalConfig, resolve_zaby_config
from ._transport import ZabyCoreClient, ZabyTransport
from ._types import AccessTokenProvider, ApiKeyProvider, RuntimeTokenProvider
from .clients._agents import (
    AgentsClient,
    ApprovalsClient,
    DeploymentsClient,
    ExternalAppsClient,
    RuntimeTokensClient,
    UsageClient,
)
from .clients._intelligence import IntelligenceClient
from .clients._knowledge_bases import KnowledgeBasesClient
from .clients._mcp import McpClient
from .clients._memory import MemoryClient
from .clients._runtime import RuntimeApprovalsClient, RuntimeFeedbackClient, RuntimeRunsClient


class Zaby:
    def __init__(
        self,
        api_key: Union[str, ApiKeyProvider],
        access_token: Optional[Union[str, AccessTokenProvider]] = None,
        transport: Optional[ZabyTransport] = None,
        config: Optional[ZabyGlobalConfig] = None,
    ):
        resolved = resolve_zaby_config(config)
        self._api_key = api_key
        self._access_token = access_token

        async def auth_headers() -> dict[str, str]:
            headers: dict[str, str] = {
                "x-zaby-api-key": await _resolve_provider(api_key),
            }
            if access_token is not None:
                headers["authorization"] = f"Bearer {await _resolve_provider(access_token)}"
            return headers

        core = ZabyCoreClient(resolved, auth_headers, transport)

        self.health = _HealthClient(core)
        self.agents = AgentsClient(core)
        self.deployments = DeploymentsClient(core)
        self.external_apps = ExternalAppsClient(core)
        self.runtime_tokens = RuntimeTokensClient(core)
        self.knowledge_bases = KnowledgeBasesClient(core)
        self.mcp = McpClient(core)
        self.memory = MemoryClient(core)
        self.intelligence = IntelligenceClient(core)
        self.approvals = ApprovalsClient(core)
        self.usage = UsageClient(core)


class ZabyRuntime:
    def __init__(
        self,
        token: Union[str, RuntimeTokenProvider],
        transport: Optional[ZabyTransport] = None,
        config: Optional[ZabyGlobalConfig] = None,
    ):
        resolved = resolve_zaby_config(config)

        async def auth_headers() -> dict[str, str]:
            return {"authorization": f"Bearer {await _resolve_provider(token)}"}

        core = ZabyCoreClient(resolved, auth_headers, transport)

        self.runs = RuntimeRunsClient(core)
        self.approvals = RuntimeApprovalsClient(core)
        self.feedback = RuntimeFeedbackClient(core)


class _HealthClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def check(self, **kwargs: Any) -> Any:
        return await self._core.request("GET", "/health", **kwargs)


async def _resolve_provider(provider: Union[str, Callable[..., Any]]) -> str:
    if callable(provider):
        result = provider()
        if hasattr(result, "__await__"):
            result = await result
        return str(result)
    return str(provider)
