from __future__ import annotations

from typing import Any, AsyncIterator, Optional

from ._transport import TransportRequest, TransportResponse, ZabyTransport


class MockResponse:
    def __init__(
        self,
        method: str,
        path: str,
        status: int = 200,
        json_body: Any = None,
        body: Optional[str] = None,
        headers: Optional[dict[str, str]] = None,
    ):
        self.method = method
        self.path = path
        self.status = status
        self.json_body = json_body
        self.body = body
        self.headers = headers or {}
        self._path_clean = path.split("?")[0]


class MockTransport(ZabyTransport):
    def __init__(self, responses: Optional[list[MockResponse]] = None):
        self.responses: list[MockResponse] = responses or []
        self.requests: list[TransportRequest] = []
        self._cursor = 0

    async def send(self, request: TransportRequest) -> TransportResponse:
        req_headers = request.headers or {}
        self.requests.append(
            TransportRequest(
                method=request.method,
                url=request.url,
                path=request.path,
                headers=self._normalize_headers(req_headers),
                json_body=request.json_body,
                signal=request.signal,
                stream=request.stream,
            )
        )

        if self._cursor >= len(self.responses):
            raise RuntimeError(f"No mock response configured for {request.method} {request.path}")

        response = self.responses[self._cursor]
        request_clean = request.path.split("?")[0]
        response_clean = response._path_clean

        if response.method != request.method or response_clean != request_clean:
            raise RuntimeError(
                f"Expected {response.method} {response.path}, "
                f"received {request.method} {request.path}"
            )

        self._cursor += 1

        import json

        body_text: str | None = None
        if response.json_body is not None:
            body_text = json.dumps(response.json_body)
        if response.body is not None:
            body_text = response.body

        body_stream = None
        if request.stream and body_text is not None:
            async def _stream():
                yield body_text.encode("utf-8")
            body_stream = _stream()

        return TransportResponse(
            status=response.status,
            headers=self._normalize_headers(response.headers or {}),
            body=body_text,
            body_stream=body_stream,
            json_body=response.json_body,
        )

    @staticmethod
    def _normalize_headers(headers: dict[str, str]) -> dict[str, str]:
        return {k.lower(): v for k, v in headers.items()}
