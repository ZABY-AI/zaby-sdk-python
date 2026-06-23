from __future__ import annotations

from typing import Any, Optional

from .._transport import ZabyCoreClient
from .._util import encode_path

INTELLIGENCE = "/api/v1/tenant/agents/intelligence"


class IntelligenceClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def list_signals(self, query: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{INTELLIGENCE}/signals", query=query, **kwargs)

    async def list_rollups(self, query: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{INTELLIGENCE}/rollups", query=query, **kwargs)

    async def list_improvements(self, query: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{INTELLIGENCE}/improvements", query=query, **kwargs)

    async def approve_improvement(self, candidate_id: str, input: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{INTELLIGENCE}/improvements/{encode_path(candidate_id)}/approve", json_body=input or {}, **kwargs)

    async def reject_improvement(self, candidate_id: str, input: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{INTELLIGENCE}/improvements/{encode_path(candidate_id)}/reject", json_body=input or {}, **kwargs)
