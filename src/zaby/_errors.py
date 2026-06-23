from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ZabyApiErrorInput:
    status: int
    message: str
    code: Optional[str] = None
    request_id: Optional[str] = None
    retry_after: Optional[int] = None
    details: Optional[Any] = None


class ZabyApiError(Exception):
    def __init__(self, input: ZabyApiErrorInput):
        super().__init__(input.message)
        self.status = input.status
        self.code = input.code
        self.request_id = input.request_id
        self.retry_after = input.retry_after
        self.details = input.details

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        return f"{cls}(status={self.status}, message={self.args[0]!r}, code={self.code!r})"


class ZabyAuthError(ZabyApiError):
    pass


class ZabyPermissionError(ZabyApiError):
    pass


class ZabyValidationError(ZabyApiError):
    pass


class ZabyRateLimitError(ZabyApiError):
    pass


class ZabyRuntimeTokenExpiredError(ZabyAuthError):
    pass


class ZabyRuntimeTokenExhaustedError(ZabyPermissionError):
    pass


class ZabyStreamError(ZabyApiError):
    pass


_ERROR_CODE_MAP: dict[str, type[ZabyApiError]] = {
    "MANAGED_AGENT_RUNTIME_TOKEN_EXPIRED": ZabyRuntimeTokenExpiredError,
    "MANAGED_AGENT_RUNTIME_TOKEN_GRANT_MAX_USES_EXCEEDED": ZabyRuntimeTokenExhaustedError,
}

_ERROR_STATUS_MAP: dict[int, type[ZabyApiError]] = {
    429: ZabyRateLimitError,
    401: ZabyAuthError,
    403: ZabyPermissionError,
}


def create_zaby_api_error(input: ZabyApiErrorInput) -> ZabyApiError:
    if input.code in _ERROR_CODE_MAP:
        return _ERROR_CODE_MAP[input.code](input)
    if input.status in _ERROR_STATUS_MAP:
        return _ERROR_STATUS_MAP[input.status](input)
    if input.status in (400, 422):
        return ZabyValidationError(input)
    return ZabyApiError(input)
