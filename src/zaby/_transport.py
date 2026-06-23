from __future__ import annotations

import json
import logging
import asyncio
from typing import Any, AsyncIterator, Callable, Optional, Sequence

import httpx

from ._config import ResolvedZabyConfig
from ._errors import ZabyApiErrorInput, create_zaby_api_error
from ._util import append_query

logger = logging.getLogger("zaby")

HttpMethod = str

HEADER_ACCEPT_JSON = "application/json"
HEADER_CONTENT_TYPE_JSON = "application/json"


class TransportRequest:
    def __init__(
        self,
        method: HttpMethod,
        url: str,
        path: str,
        headers: dict[str, str],
        json_body: Any = None,
        signal: Any = None,
        stream: bool = False,
    ):
        self.method = method
        self.url = url
        self.path = path
        self.headers = headers
        self.json_body = json_body
        self.signal = signal
        self.stream = stream


class TransportResponse:
    def __init__(
        self,
        status: int,
        headers: dict[str, str],
        json_body: Any = None,
        body: Optional[str] = None,
        body_stream: Optional[AsyncIterator[bytes]] = None,
    ):
        self.status = status
        self.headers = headers
        self.json_body = json_body
        self.body = body
        self.body_stream = body_stream


class ZabyTransport:
    async def send(self, request: TransportRequest) -> TransportResponse:
        ...


AuthHeaderProvider = Callable[[], Any]


class HttpTransport(ZabyTransport):
    def __init__(self, config: ResolvedZabyConfig):
        self._config = config
        self._client = httpx.AsyncClient(timeout=httpx.Timeout(config.timeout_ms / 1000))

    async def send(self, request: TransportRequest) -> TransportResponse:
        kwargs: dict[str, Any] = {
            "method": request.method,
            "url": request.url,
            "headers": request.headers,
        }
        if request.json_body is not None:
            kwargs["content"] = json.dumps(request.json_body)
            kwargs["headers"]["content-type"] = "application/json"

        if request.signal is not None:
            kwargs["timeout"] = httpx.Timeout(self._config.timeout_ms / 1000)

        response = await self._client.request(**kwargs)

        headers = {k.lower(): v for k, v in response.headers.items()}

        if request.stream:
            return TransportResponse(
                status=response.status_code,
                headers=headers,
                body_stream=response.aiter_bytes(),
            )

        body = await response.aread()
        body_text = body.decode("utf-8", errors="replace")
        return TransportResponse(
            status=response.status_code,
            headers=headers,
            body=body_text,
            json_body=_parse_json_body(body_text),
        )

    async def close(self) -> None:
        await self._client.aclose()


class ZabyCoreClient:
    def __init__(
        self,
        config: ResolvedZabyConfig,
        auth_headers: AuthHeaderProvider,
        transport: Optional[ZabyTransport] = None,
    ):
        self._config = config
        self._auth_headers = auth_headers
        self._transport = transport or HttpTransport(config)

    async def request(
        self,
        method: HttpMethod,
        path: str,
        *,
        query: Any = None,
        json_body: Any = None,
        request_id: Optional[str] = None,
        signal: Any = None,
        stream: bool = False,
    ) -> Any:
        response = await self.raw(method, path, query=query, json_body=json_body, request_id=request_id, signal=signal, stream=stream)
        if response.status >= 400:
            raise _create_error_from_response(response)
        return response.json_body

    async def raw(
        self,
        method: HttpMethod,
        path: str,
        *,
        query: Any = None,
        json_body: Any = None,
        request_id: Optional[str] = None,
        signal: Any = None,
        stream: bool = False,
    ) -> TransportResponse:
        path_with_query = append_query(path, query)
        auth_headers = await self._resolve_auth_headers()

        headers: dict[str, str] = {
            "accept": HEADER_ACCEPT_JSON,
            **auth_headers,
        }
        if json_body is not None:
            headers["content-type"] = HEADER_CONTENT_TYPE_JSON
        if request_id:
            headers["x-request-id"] = request_id
        if self._config.user_agent:
            headers["user-agent"] = self._config.user_agent

        request = TransportRequest(
            method=method,
            url=f"{self._config.api_origin}{path_with_query}",
            path=path_with_query,
            headers=headers,
            json_body=json_body,
            signal=signal,
            stream=stream,
        )

        response = await self._send_with_retry(request)
        if response.status >= 400:
            captured = await _capture_stream_error_body(response)
            raise _create_error_from_response(captured)
        return response

    async def _send_with_retry(self, request: TransportRequest) -> TransportResponse:
        policy = self._config.retries
        attempts = policy.attempts
        retry_methods = policy.retry_methods
        retry_statuses = policy.retry_statuses
        last_response: Optional[TransportResponse] = None

        for attempt in range(attempts + 1):
            response = await self._transport.send(request)
            last_response = response
            should_retry = (
                attempt < attempts
                and request.method in retry_methods
                and response.status in retry_statuses
            )
            if not should_retry:
                return response
            backoff = (policy.backoff_ms or (lambda a: 100 * 2 ** a))(attempt) / 1000
            await asyncio.sleep(backoff)

        return last_response

    async def _resolve_auth_headers(self) -> dict[str, str]:
        result = self._auth_headers()
        if asyncio.iscoroutine(result):
            result = await result
        return result if isinstance(result, dict) else {}


def _create_error_from_response(response: TransportResponse) -> ZabyApiError:
    body = {}
    if isinstance(response.json_body, dict):
        body = response.json_body
    error_input = ZabyApiErrorInput(
        status=response.status,
        message=body.get("message") or f"Zaby API request failed with status {response.status}.",
        details=body,
    )
    code = body.get("code") or body.get("errorCode")
    if isinstance(code, str):
        error_input.code = code
    request_id = response.headers.get("x-request-id")
    if request_id:
        error_input.request_id = request_id
    retry_after = _parse_retry_after(response.headers.get("retry-after"))
    if retry_after is not None:
        error_input.retry_after = retry_after
    return create_zaby_api_error(error_input)


def _parse_json_body(body: str) -> Any:
    if not body:
        return None
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        logger.warning("Zaby SDK: Failed to parse response body as JSON — returning None")
        return None


def _parse_retry_after(value: Optional[str]) -> Optional[int]:
    if not value:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


async def _capture_stream_error_body(response: TransportResponse) -> TransportResponse:
    if not response.body_stream or response.json_body is not None:
        return response
    try:
        chunks: list[bytes] = []
        async for chunk in response.body_stream:
            chunks.append(chunk)
        text = b"".join(chunks).decode("utf-8", errors="replace")
        parsed = _parse_json_body(text)
        if parsed:
            return TransportResponse(
                status=response.status,
                headers=response.headers,
                json_body=parsed,
                body=text,
            )
    except Exception:
        pass
    return response
