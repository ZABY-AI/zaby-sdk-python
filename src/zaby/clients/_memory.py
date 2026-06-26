from __future__ import annotations

from typing import Any, Optional

from .._transport import ZabyCoreClient
from .._util import encode_path

AGENTS = "/api/v1/provisioning/agentic-os/agents"


class MemoryClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def list_items(self, query: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{AGENTS}/memory-items", query=query, **kwargs)

    async def get_item(self, memory_item_id: str, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{AGENTS}/memory-items/{encode_path(memory_item_id)}", **kwargs)

    async def retrieve(self, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{AGENTS}/memory-retrievals", json_body=input, **kwargs)

    async def list_candidates(self, query: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{AGENTS}/memory-candidates", query=query, **kwargs)

    async def approve_candidate(self, candidate_id: str, input: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{AGENTS}/memory-candidates/{encode_path(candidate_id)}/approve", json_body=input or {}, **kwargs)

    async def reject_candidate(self, candidate_id: str, input: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{AGENTS}/memory-candidates/{encode_path(candidate_id)}/reject", json_body=input or {}, **kwargs)

    async def disable_item(self, memory_item_id: str, input: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("PATCH", f"{AGENTS}/memory-items/{encode_path(memory_item_id)}/disable", json_body=input or {}, **kwargs)

    async def delete_item(self, memory_item_id: str, input: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("DELETE", f"{AGENTS}/memory-items/{encode_path(memory_item_id)}", json_body=input or {}, **kwargs)
