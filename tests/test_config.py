import pytest
from zaby._config import (
    configure_zaby,
    DEFAULT_ZABY_API_ORIGIN,
    LOCAL_ZABY_API_ORIGIN,
    reset_zaby_config_for_tests,
    resolve_zaby_config,
    ZabyGlobalConfig,
)
from zaby._types import RetryPolicy


@pytest.fixture(autouse=True)
def reset_config():
    reset_zaby_config_for_tests()
    yield


class TestConfigEnvironmentResolution:
    def test_defaults_to_production(self):
        config = resolve_zaby_config()
        assert config.environment == "production"
        assert config.api_origin == DEFAULT_ZABY_API_ORIGIN

    def test_local_environment(self):
        config = resolve_zaby_config(ZabyGlobalConfig(environment="local"))
        assert config.api_origin == LOCAL_ZABY_API_ORIGIN

    def test_staging_uses_prod_origin(self):
        config = resolve_zaby_config(ZabyGlobalConfig(environment="staging"))
        assert config.api_origin == DEFAULT_ZABY_API_ORIGIN

    def test_explicit_api_origin_overrides_environment(self):
        config = resolve_zaby_config(ZabyGlobalConfig(
            environment="production",
            api_origin="https://custom.example.com/",
        ))
        assert config.api_origin == "https://custom.example.com"

    def test_strips_trailing_slashes(self):
        config = resolve_zaby_config(ZabyGlobalConfig(api_origin="https://example.com///"))
        assert config.api_origin == "https://example.com"

    def test_global_config_via_configure_zaby(self):
        configure_zaby(ZabyGlobalConfig(api_origin="https://global.example.com"))
        config = resolve_zaby_config()
        assert config.api_origin == "https://global.example.com"

    def test_instance_overrides_global(self):
        configure_zaby(ZabyGlobalConfig(api_origin="https://global.example.com"))
        config = resolve_zaby_config(ZabyGlobalConfig(api_origin="https://override.example.com"))
        assert config.api_origin == "https://override.example.com"

    def test_default_timeout(self):
        config = resolve_zaby_config()
        assert config.timeout_ms == 30_000

    def test_custom_timeout(self):
        config = resolve_zaby_config(ZabyGlobalConfig(timeout_ms=5000))
        assert config.timeout_ms == 5000


class TestConfigRetryPolicy:
    def test_retries_undefined_means_zero(self):
        config = resolve_zaby_config()
        assert config.retries.attempts == 0
        assert config.retries.retry_methods == []
        assert config.retries.retry_statuses == []

    def test_default_backoff_function(self):
        config = resolve_zaby_config(ZabyGlobalConfig(retries=RetryPolicy(attempts=3)))
        assert config.retries.backoff_ms is not None
        assert config.retries.backoff_ms(0) == 100
        assert config.retries.backoff_ms(4) == 1000

    def test_retries_only_attempts_gets_defaults(self):
        config = resolve_zaby_config(ZabyGlobalConfig(retries=RetryPolicy(attempts=3)))
        assert config.retries.attempts == 3
        assert config.retries.retry_methods == ["GET", "HEAD", "OPTIONS"]
        assert config.retries.retry_statuses == [408, 429, 500, 502, 503, 504]

    def test_retries_object_defaults(self):
        config = resolve_zaby_config(ZabyGlobalConfig(
            retries=RetryPolicy(attempts=5, retry_methods=["GET"], retry_statuses=[500])
        ))
        assert config.retries.attempts == 5
        assert config.retries.retry_methods == ["GET"]
        assert config.retries.retry_statuses == [500]

    def test_retries_negative_clamped(self):
        config = resolve_zaby_config(ZabyGlobalConfig(
            retries=RetryPolicy(attempts=0)
        ))
        assert config.retries.attempts == 0


class TestConfigEnvVars:
    def test_reads_environment_from_env(self, monkeypatch):
        monkeypatch.setenv("ZABY_ENVIRONMENT", "staging")
        config = resolve_zaby_config()
        assert config.environment == "staging"

    def test_reads_api_origin_from_env(self, monkeypatch):
        monkeypatch.setenv("ZABY_API_ORIGIN", "https://custom.api.com")
        config = resolve_zaby_config()
        assert config.api_origin == "https://custom.api.com"

    def test_global_overrides_env(self, monkeypatch):
        monkeypatch.setenv("ZABY_API_ORIGIN", "https://from-env.com")
        configure_zaby(ZabyGlobalConfig(api_origin="https://from-global.com"))
        config = resolve_zaby_config()
        assert config.api_origin == "https://from-global.com"
