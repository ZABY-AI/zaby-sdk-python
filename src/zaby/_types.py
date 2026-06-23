from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, List, Mapping, Optional, Protocol, Sequence, Union


JsonPrimitive = Union[str, int, float, bool, None]
JsonObject = Mapping[str, Any]
JsonValue = Union[JsonPrimitive, JsonObject, List[Any]]


class SseEvent:
    def __init__(self, data: Any, id: Optional[str] = None, event: Optional[str] = None):
        self.id = id
        self.event = event
        self.data = data

    def __repr__(self) -> str:
        return f"SseEvent(id={self.id!r}, event={self.event!r}, data={self.data!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SseEvent):
            return NotImplemented
        return self.id == other.id and self.event == other.event and self.data == other.data


class RequestOptions:
    def __init__(self, request_id: Optional[str] = None, signal: Optional[Any] = None):
        self.request_id = request_id
        self.signal = signal


QueryValue = Union[str, int, float, bool, None]
Query = Mapping[str, Union[QueryValue, Sequence[Union[str, int, float, bool]]]]

RetryBackoffFn = Callable[[int], float]


@dataclass
class RetryPolicy:
    attempts: int = 0
    retry_methods: List[str] = field(default_factory=list)
    retry_statuses: List[int] = field(default_factory=list)
    backoff_ms: Optional[RetryBackoffFn] = None


@dataclass
class RuntimeTokenResponse:
    token: str
    token_type: str = "Bearer"
    expires_at: Optional[str] = None
    scopes: Optional[List[str]] = None
    grant_id: Optional[str] = None
    agent_session_id: Optional[str] = None
    external_app_id: Optional[str] = None
    deployment_id: Optional[str] = None


@dataclass
class ListResponse:
    items: List[Any] = field(default_factory=list)
    page: Optional[int] = None
    limit: Optional[int] = None
    total: Optional[int] = None


class ApiKeyProvider(Protocol):
    def __call__(self) -> Union[str, Awaitable[str]]: ...


class AccessTokenProvider(Protocol):
    def __call__(self) -> Union[str, Awaitable[str]]: ...


class RuntimeTokenProvider(Protocol):
    def __call__(self) -> Union[str, Awaitable[str]]: ...
