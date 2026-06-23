import pytest
import logging

from zaby._testing import MockTransport, MockResponse
from zaby._transport import ZabyCoreClient, _parse_json_body, _create_error_from_response, TransportResponse
from zaby._config import resolve_zaby_config, ZabyGlobalConfig
from zaby._errors import ZabyAuthError, ZabyRateLimitError, ZabyValidationError, ZabyPermissionError, ZabyApiError


@pytest.fixture
def config():
    return resolve_zaby_config()


@pytest.fixture
def core(config):
    transport = MockTransport()
    return ZabyCoreClient(config, lambda: {"authorization": "Bearer test"}, transport)


class TestTransportRequestMethod:
    async def test_get_returns_parsed_json(self, config):
        transport = MockTransport([MockResponse("GET", "/test", json_body={"ok": True})])
        core = ZabyCoreClient(config, lambda: {"authorization": "Bearer test"}, transport)
        result = await core.request("GET", "/test")
        assert result == {"ok": True}

    async def test_includes_query_params(self, config):
        transport = MockTransport([MockResponse("GET", "/test?foo=bar&num=42", json_body={"ok": True})])
        core = ZabyCoreClient(config, lambda: {"authorization": "Bearer test"}, transport)
        await core.request("GET", "/test", query={"foo": "bar", "num": 42})
        assert "foo=bar" in transport.requests[0].path
        assert "num=42" in transport.requests[0].path

    async def test_sends_json_body(self, config):
        transport = MockTransport([MockResponse("POST", "/test", status=201)])
        core = ZabyCoreClient(config, lambda: {"authorization": "Bearer test"}, transport)
        await core.request("POST", "/test", json_body={"name": "test"})
        assert transport.requests[0].json_body == {"name": "test"}

    async def test_sets_content_type(self, config):
        transport = MockTransport([MockResponse("POST", "/test", status=201)])
        core = ZabyCoreClient(config, lambda: {"authorization": "Bearer test"}, transport)
        await core.request("POST", "/test", json_body={})
        assert transport.requests[0].headers["content-type"] == "application/json"


class TestTransportErrorHandling:
    async def test_throws_auth_on_401(self, config):
        transport = MockTransport([MockResponse("GET", "/test", status=401, json_body={"message": "Unauthorized"})])
        core = ZabyCoreClient(config, lambda: {"authorization": "Bearer bad"}, transport)
        with pytest.raises(ZabyAuthError, match="Unauthorized"):
            await core.request("GET", "/test")

    async def test_throws_rate_limit_on_429(self, config):
        transport = MockTransport([MockResponse("GET", "/test", status=429,
            json_body={"message": "Rate limited", "code": "TOO_MANY"},
            headers={"retry-after": "5", "x-request-id": "req_abc"})])
        core = ZabyCoreClient(config, lambda: {"authorization": "Bearer test"}, transport)
        with pytest.raises(ZabyRateLimitError) as exc:
            await core.request("GET", "/test")
        assert exc.value.status == 429
        assert exc.value.code == "TOO_MANY"
        assert exc.value.request_id == "req_abc"
        assert exc.value.retry_after == 5

    async def test_throws_validation_on_400(self, config):
        transport = MockTransport([MockResponse("POST", "/test", status=400, json_body={"message": "Bad request"})])
        core = ZabyCoreClient(config, lambda: {"authorization": "Bearer test"}, transport)
        with pytest.raises(ZabyValidationError):
            await core.request("POST", "/test", json_body={})

    async def test_throws_permission_on_403(self, config):
        transport = MockTransport([MockResponse("GET", "/test", status=403, json_body={"message": "Forbidden"})])
        core = ZabyCoreClient(config, lambda: {"authorization": "Bearer test"}, transport)
        with pytest.raises(ZabyPermissionError):
            await core.request("GET", "/test")

    async def test_generic_error_on_unknown(self, config):
        transport = MockTransport([MockResponse("GET", "/test", status=500, json_body={"message": "Server error"})])
        core = ZabyCoreClient(config, lambda: {"authorization": "Bearer test"}, transport)
        with pytest.raises(ZabyApiError):
            await core.request("GET", "/test")

    async def test_non_json_error(self, config):
        transport = MockTransport([MockResponse("GET", "/test", status=500, body="Internal Server Error")])
        core = ZabyCoreClient(config, lambda: {"authorization": "Bearer test"}, transport)
        with pytest.raises(ZabyApiError):
            await core.request("GET", "/test")


class TestTransportUserAgent:
    async def test_sends_user_agent_when_configured(self, config):
        transport = MockTransport([MockResponse("GET", "/test", json_body={})])
        cfg = resolve_zaby_config(ZabyGlobalConfig(
            api_origin="https://example.com",
            user_agent="zaby-sdk-test/1.0",
        ))
        core = ZabyCoreClient(cfg, lambda: {"authorization": "Bearer test"}, transport)
        await core.request("GET", "/test")
        assert transport.requests[0].headers["user-agent"] == "zaby-sdk-test/1.0"

    async def test_does_not_send_user_agent_when_not_configured(self, config):
        transport = MockTransport([MockResponse("GET", "/test", json_body={})])
        core = ZabyCoreClient(config, lambda: {"authorization": "Bearer test"}, transport)
        await core.request("GET", "/test")
        assert "user-agent" not in transport.requests[0].headers


class TestTransportParseJsonBody:
    def test_empty_body_returns_none(self):
        assert _parse_json_body("") is None
        assert _parse_json_body(None) is None  # type: ignore[arg-type]

    def test_malformed_json_returns_none(self, caplog):
        caplog.set_level(logging.WARNING)
        result = _parse_json_body("not json at all")
        assert result is None
        assert "Failed to parse response body as JSON" in caplog.text

    def test_valid_json_returns_parsed(self):
        assert _parse_json_body('{"key": "val"}') == {"key": "val"}
        assert _parse_json_body("[1, 2, 3]") == [1, 2, 3]


class TestTransportErrorSubclasses:
    async def test_422_returns_validation_error(self, config):
        transport = MockTransport([MockResponse("POST", "/test", status=422, json_body={"message": "Unprocessable"})])
        core = ZabyCoreClient(config, lambda: {"authorization": "Bearer test"}, transport)
        with pytest.raises(ZabyValidationError):
            await core.request("POST", "/test", json_body={})

    async def test_error_includes_request_id(self, config):
        transport = MockTransport([MockResponse("GET", "/test", status=429,
            json_body={"message": "Rate limited"}, headers={"x-request-id": "req_xyz"})])
        core = ZabyCoreClient(config, lambda: {"authorization": "Bearer test"}, transport)
        with pytest.raises(ZabyRateLimitError) as exc:
            await core.request("GET", "/test")
        assert exc.value.request_id == "req_xyz"


class TestTransportRetry:
    async def test_retries_on_number_shorthand(self):
        config = resolve_zaby_config(ZabyGlobalConfig(
            retries=__import__('zaby._types', fromlist=['RetryPolicy']).RetryPolicy(
                attempts=3,
                retry_methods=["GET"],
                retry_statuses=[500],
                backoff_ms=lambda a: 1,
            ),
        ))
        call_count = 0
        class FailTransport:
            async def send(self, request):
                nonlocal call_count
                call_count += 1
                return TransportResponse(status=500, headers={}, json_body={"message": "Fail"})
        core = ZabyCoreClient(config, lambda: {"authorization": "Bearer test"}, FailTransport())
        with pytest.raises(ZabyApiError):
            await core.raw("GET", "/test")
        assert call_count == 4  # 1 initial + 3 retries

    async def test_does_not_retry_on_method_not_in_retry_methods(self):
        call_count = 0
        class FailTransport:
            async def send(self, request):
                nonlocal call_count
                call_count += 1
                return TransportResponse(status=500, headers={}, json_body={"message": "Fail"})
        from zaby._types import RetryPolicy
        cfg = resolve_zaby_config(ZabyGlobalConfig(
            retries=RetryPolicy(attempts=2, retry_methods=["POST"], retry_statuses=[500]),
        ))
        core = ZabyCoreClient(cfg, lambda: {"authorization": "Bearer test"}, FailTransport())
        with pytest.raises(ZabyApiError):
            await core.raw("GET", "/test")
        assert call_count == 1

    async def test_does_not_retry_on_non_retry_status(self, config):
        call_count = 0
        class FailTransport:
            async def send(self, request):
                nonlocal call_count
                call_count += 1
                return TransportResponse(status=400, headers={}, json_body={"message": "Bad"})
        from zaby._types import RetryPolicy
        cfg = resolve_zaby_config(ZabyGlobalConfig(
            retries=RetryPolicy(attempts=2, retry_methods=["GET"], retry_statuses=[500]),
        ))
        core = ZabyCoreClient(cfg, lambda: {"authorization": "Bearer test"}, FailTransport())
        with pytest.raises(ZabyApiError):
            await core.raw("GET", "/test")
        assert call_count == 1
