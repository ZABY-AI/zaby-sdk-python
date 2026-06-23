from __future__ import annotations

from typing import Any, AsyncIterator, Optional

from .._sse import parse_sse_response
from .._transport import ZabyCoreClient
from .._types import SseEvent
from .._util import encode_path

RUNTIME = "/api/v1/agent-runtime"


class RuntimeRunsClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def start(self, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{RUNTIME}/runs", json_body=input, **kwargs)

    async def events(self, run_id: str, query: Any = None, **kwargs: Any) -> Any:
        return await self._core.request("GET", f"{RUNTIME}/runs/{encode_path(run_id)}/events", query=query, **kwargs)

    async def stream(self, run_id: str, query: Any = None, **kwargs: Any) -> AsyncIterator[SseEvent]:
        response = await self._core.raw(
            "GET",
            f"{RUNTIME}/runs/{encode_path(run_id)}/aiui",
            query=query,
            stream=True,
            **kwargs,
        )
        async for event in parse_sse_response(body_stream=response.body_stream):
            yield event


class RuntimeApprovalsClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def approve(self, run_id: str, approval_id: str, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{RUNTIME}/runs/{encode_path(run_id)}/approvals/{encode_path(approval_id)}/approve", **kwargs)

    async def reject(self, run_id: str, approval_id: str, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{RUNTIME}/runs/{encode_path(run_id)}/approvals/{encode_path(approval_id)}/reject", **kwargs)


class RuntimeFeedbackClient:
    def __init__(self, core: ZabyCoreClient):
        self._core = core

    async def create(self, run_id: str, input: Any, **kwargs: Any) -> Any:
        return await self._core.request("POST", f"{RUNTIME}/runs/{encode_path(run_id)}/feedback", json_body=input, **kwargs)
