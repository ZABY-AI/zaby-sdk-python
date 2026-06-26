from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable, Optional, Union

from ._types import RetryPolicy


DEFAULT_ZABY_API_ORIGIN = "http://192.168.68.61:9080"
LOCAL_ZABY_API_ORIGIN = "http://localhost:9080"

Environment = str


class FetchLike:
    async def __call__(self, url: str, **kwargs: object) -> object: ...


@dataclass
class ZabyGlobalConfig:
    environment: Optional[Environment] = None
    api_origin: Optional[str] = None
    timeout_ms: Optional[int] = None
    retries: Optional[Union[int, RetryPolicy]] = None
    fetch: Optional[FetchLike] = None
    user_agent: Optional[str] = None


@dataclass
class ResolvedZabyConfig:
    environment: Environment
    api_origin: str
    timeout_ms: int
    retries: RetryPolicy
    fetch: FetchLike
    user_agent: Optional[str] = None


_global_config: ZabyGlobalConfig = ZabyGlobalConfig()


def configure_zaby(config: ZabyGlobalConfig) -> None:
    _global_config.environment = config.environment if config.environment is not None else _global_config.environment
    _global_config.api_origin = config.api_origin if config.api_origin is not None else _global_config.api_origin
    _global_config.timeout_ms = config.timeout_ms if config.timeout_ms is not None else _global_config.timeout_ms
    _global_config.retries = config.retries if config.retries is not None else _global_config.retries
    _global_config.fetch = config.fetch if config.fetch is not None else _global_config.fetch
    _global_config.user_agent = config.user_agent if config.user_agent is not None else _global_config.user_agent


def reset_zaby_config_for_tests() -> None:
    global _global_config
    _global_config = ZabyGlobalConfig()


def resolve_zaby_config(overrides: Optional[ZabyGlobalConfig] = None) -> ResolvedZabyConfig:
    environment = (
        overrides.environment if overrides and overrides.environment is not None
        else _global_config.environment if _global_config.environment is not None
        else _read_env("ZABY_ENVIRONMENT")
    )
    api_origin = (
        overrides.api_origin if overrides and overrides.api_origin is not None
        else _global_config.api_origin if _global_config.api_origin is not None
        else _read_env("ZABY_API_ORIGIN")
    )
    if environment is None:
        environment = "production"
    if api_origin is None:
        api_origin = _origin_for_environment(environment)
    api_origin = _normalize_api_origin(api_origin)

    fetch_impl = (
        overrides.fetch if overrides and overrides.fetch is not None
        else _global_config.fetch if _global_config.fetch is not None
        else None
    )

    merged_timeout = (
        overrides.timeout_ms if overrides and overrides.timeout_ms is not None
        else _global_config.timeout_ms if _global_config.timeout_ms is not None
        else 30_000
    )

    merged_retries = (
        overrides.retries if overrides and overrides.retries is not None
        else _global_config.retries if _global_config.retries is not None
        else None
    )

    merged_user_agent = (
        overrides.user_agent if overrides and overrides.user_agent is not None
        else _global_config.user_agent if _global_config.user_agent is not None
        else None
    )

    return ResolvedZabyConfig(
        environment=environment,
        api_origin=api_origin,
        timeout_ms=merged_timeout,
        retries=_normalize_retry_policy(merged_retries),
        fetch=fetch_impl,
        user_agent=merged_user_agent,
    )


def _origin_for_environment(environment: Environment) -> str:
    if environment == "local":
        return LOCAL_ZABY_API_ORIGIN
    return DEFAULT_ZABY_API_ORIGIN


def _normalize_api_origin(value: str) -> str:
    return value.rstrip("/")


def _normalize_retry_policy(value: Optional[Union[int, RetryPolicy]]) -> RetryPolicy:
    if value is None:
        return RetryPolicy(attempts=0, retry_methods=[], retry_statuses=[])
    if isinstance(value, int):
        return RetryPolicy(
            attempts=max(0, value),
            retry_methods=["GET", "HEAD", "OPTIONS"],
            retry_statuses=[408, 429, 500, 502, 503, 504],
            backoff_ms=lambda attempt: min(100 * 2 ** attempt, 1000),
        )
    return RetryPolicy(
        attempts=value.attempts,
        retry_methods=value.retry_methods if value.retry_methods else ["GET", "HEAD", "OPTIONS"],
        retry_statuses=value.retry_statuses if value.retry_statuses else [408, 429, 500, 502, 503, 504],
        backoff_ms=value.backoff_ms or (lambda attempt: min(100 * 2 ** attempt, 1000)),
    )


def _read_env(key: str) -> Optional[str]:
    return os.environ.get(key)
