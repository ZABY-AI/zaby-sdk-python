import pytest
from zaby._testing import MockTransport, MockResponse
from zaby._transport import TransportRequest


class TestMockTransport:
    async def test_returns_configured_response(self):
        transport = MockTransport([MockResponse("GET", "/health", json_body={"status": "ok"})])
        result = await transport.send(TransportRequest("GET", "https://example.com/health", "/health", {}))
        assert result.json_body == {"status": "ok"}
        assert result.status == 200

    async def test_throws_on_no_responses(self):
        transport = MockTransport([MockResponse("GET", "/health", json_body={"status": "ok"})])
        await transport.send(TransportRequest("GET", "https://example.com/health", "/health", {}))
        with pytest.raises(RuntimeError, match="No mock response"):
            await transport.send(TransportRequest("GET", "https://example.com/health", "/health", {}))

    async def test_throws_on_method_mismatch(self):
        transport = MockTransport([MockResponse("POST", "/health", json_body={"status": "ok"})])
        with pytest.raises(RuntimeError, match="Expected POST"):
            await transport.send(TransportRequest("GET", "https://example.com/health", "/health", {}))

    async def test_records_request_history(self):
        transport = MockTransport([
            MockResponse("GET", "/a", json_body={}),
            MockResponse("POST", "/b", json_body={}),
        ])
        await transport.send(TransportRequest("GET", "https://example.com/a", "/a", {}))
        await transport.send(TransportRequest("POST", "https://example.com/b", "/b", {}, json_body={"data": 1}))
        assert len(transport.requests) == 2
        assert transport.requests[0].method == "GET"
        assert transport.requests[0].path == "/a"
        assert transport.requests[1].method == "POST"
        assert transport.requests[1].json_body == {"data": 1}

    async def test_returns_configured_status(self):
        transport = MockTransport([MockResponse("POST", "/create", status=201, json_body={"id": "1"})])
        result = await transport.send(TransportRequest("POST", "https://example.com/create", "/create", {}))
        assert result.status == 201

    async def test_returns_configured_headers(self):
        transport = MockTransport([MockResponse("GET", "/test", json_body={}, headers={"x-custom": "val"})])
        result = await transport.send(TransportRequest("GET", "https://example.com/test", "/test", {}))
        assert result.headers["x-custom"] == "val"


class TestMockTransportCursorFix:
    async def test_cursor_does_not_advance_on_mismatch(self):
        transport = MockTransport([
            MockResponse("GET", "/first", json_body={"data": 1}),
            MockResponse("GET", "/second", json_body={"data": 2}),
        ])
        with pytest.raises(RuntimeError):
            await transport.send(TransportRequest("POST", "https://example.com/first", "/first", {}))
        result = await transport.send(TransportRequest("GET", "https://example.com/first", "/first", {}))
        assert result.json_body == {"data": 1}

    async def test_query_params_stripped_before_match(self):
        transport = MockTransport([MockResponse("GET", "/items", json_body={"items": []})])
        result = await transport.send(TransportRequest("GET", "https://example.com/items?limit=10", "/items?limit=10", {}))
        assert result.json_body == {"items": []}


class TestMockTransportEdgeCases:
    async def test_empty_headers(self):
        transport = MockTransport([MockResponse("GET", "/test", json_body={})])
        result = await transport.send(TransportRequest("GET", "https://example.com/test", "/test", {}))
        assert result.headers is not None

    async def test_null_json_body(self):
        transport = MockTransport([MockResponse("POST", "/test", json_body={"received": True})])
        result = await transport.send(TransportRequest("POST", "https://example.com/test", "/test", {}, json_body=None))
        assert result.json_body == {"received": True}
