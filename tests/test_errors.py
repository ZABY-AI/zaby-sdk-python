import pytest
from zaby._errors import (
    ZabyApiError,
    ZabyApiErrorInput,
    ZabyAuthError,
    ZabyPermissionError,
    ZabyRateLimitError,
    ZabyRuntimeTokenExhaustedError,
    ZabyRuntimeTokenExpiredError,
    ZabyStreamError,
    ZabyValidationError,
    create_zaby_api_error,
)


class TestErrorFactory:
    def test_rate_limit_for_429(self):
        err = create_zaby_api_error(ZabyApiErrorInput(status=429, message="Too many"))
        assert isinstance(err, ZabyRateLimitError)

    def test_auth_for_401(self):
        err = create_zaby_api_error(ZabyApiErrorInput(status=401, message="Unauthorized"))
        assert isinstance(err, ZabyAuthError)

    def test_permission_for_403(self):
        err = create_zaby_api_error(ZabyApiErrorInput(status=403, message="Forbidden"))
        assert isinstance(err, ZabyPermissionError)

    def test_validation_for_400(self):
        err = create_zaby_api_error(ZabyApiErrorInput(status=400, message="Bad"))
        assert isinstance(err, ZabyValidationError)

    def test_validation_for_422(self):
        err = create_zaby_api_error(ZabyApiErrorInput(status=422, message="Unprocessable"))
        assert isinstance(err, ZabyValidationError)

    def test_token_expired_code(self):
        err = create_zaby_api_error(ZabyApiErrorInput(
            status=401, message="Token expired",
            code="MANAGED_AGENT_RUNTIME_TOKEN_EXPIRED",
        ))
        assert isinstance(err, ZabyRuntimeTokenExpiredError)

    def test_token_exhausted_code(self):
        err = create_zaby_api_error(ZabyApiErrorInput(
            status=403, message="Max uses",
            code="MANAGED_AGENT_RUNTIME_TOKEN_GRANT_MAX_USES_EXCEEDED",
        ))
        assert isinstance(err, ZabyRuntimeTokenExhaustedError)

    def test_generic_for_unknown_status(self):
        err = create_zaby_api_error(ZabyApiErrorInput(status=503, message="Down"))
        assert isinstance(err, ZabyApiError)


class TestErrorProperties:
    def test_all_properties(self):
        err = ZabyApiError(ZabyApiErrorInput(
            status=429,
            message="Rate limited",
            code="LIMIT_EXCEEDED",
            request_id="req_1",
            retry_after=10,
            details={"quota": 100},
        ))
        assert err.status == 429
        assert err.args[0] == "Rate limited"
        assert err.code == "LIMIT_EXCEEDED"
        assert err.request_id == "req_1"
        assert err.retry_after == 10
        assert err.details == {"quota": 100}

    def test_optional_fields_omitted(self):
        err = ZabyApiError(ZabyApiErrorInput(status=500, message="fail"))
        assert err.code is None
        assert err.request_id is None
        assert err.retry_after is None
        assert err.details is None


class TestErrorInheritance:
    def test_auth_is_instance_of_api_error(self):
        assert isinstance(ZabyAuthError(ZabyApiErrorInput(status=401, message="")), ZabyApiError)

    def test_rate_limit_is_api_error(self):
        assert isinstance(ZabyRateLimitError(ZabyApiErrorInput(status=429, message="")), ZabyApiError)

    def test_token_expired_is_auth_and_api(self):
        err = ZabyRuntimeTokenExpiredError(ZabyApiErrorInput(
            status=401, message="",
            code="MANAGED_AGENT_RUNTIME_TOKEN_EXPIRED",
        ))
        assert isinstance(err, ZabyAuthError)
        assert isinstance(err, ZabyApiError)


class TestErrorRepr:
    def test_repr_includes_class_name(self):
        err = ZabyApiError(ZabyApiErrorInput(status=500, message="fail", code="ERR"))
        r = repr(err)
        assert "ZabyApiError" in r
        assert "500" in r
        assert "ERR" in r

    def test_subclass_repr(self):
        err = ZabyRateLimitError(ZabyApiErrorInput(status=429, message="too fast"))
        r = repr(err)
        assert "ZabyRateLimitError" in r


class TestErrorEdgeCases:
    def test_status_zero_is_generic_api_error(self):
        err = create_zaby_api_error(ZabyApiErrorInput(status=0, message="Network failure"))
        assert isinstance(err, ZabyApiError)
        assert err.status == 0

    def test_code_precedence_over_status(self):
        err = create_zaby_api_error(ZabyApiErrorInput(
            status=429, message="",
            code="MANAGED_AGENT_RUNTIME_TOKEN_EXPIRED",
        ))
        assert isinstance(err, ZabyRuntimeTokenExpiredError)
        assert err.status == 429
