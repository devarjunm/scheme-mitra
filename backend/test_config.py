from __future__ import annotations

import pytest

from backend import config


def _set_production(monkeypatch):
    monkeypatch.setattr(config, "IS_PRODUCTION", True)
    monkeypatch.setattr(config, "APP_ENV", "production")
    monkeypatch.setattr(config, "DATABASE_URL", "postgresql+psycopg://user:pass@db.example.com/scheme?sslmode=verify-full")
    monkeypatch.setattr(config, "JWT_SECRET", "a-unique-production-secret-that-is-longer-than-32-characters")
    monkeypatch.setattr(config, "DEMO_MODE", False)
    monkeypatch.setattr(config, "SEED_SCHEMES", False)
    monkeypatch.setattr(config, "COOKIE_SECURE", True)
    monkeypatch.setattr(config, "RATE_LIMIT_REDIS_URL", "rediss://:redis-secret@redis.example.com:6379/0")
    monkeypatch.setattr(config, "TRUSTED_HOSTS", ["scheme.example.com"])
    monkeypatch.setattr(config, "FORWARDED_ALLOW_IPS", "10.0.0.10")
    monkeypatch.setattr(config, "CORS_ORIGINS", [])
    monkeypatch.setattr(config, "ADMIN_EMAIL", "")
    monkeypatch.setattr(config, "ADMIN_PASSWORD", "")


def test_explicit_secure_production_config_passes(monkeypatch):
    _set_production(monkeypatch)
    config.validate_runtime_config()


def test_wildcard_host_and_non_tls_stores_fail_closed(monkeypatch):
    _set_production(monkeypatch)
    monkeypatch.setattr(config, "TRUSTED_HOSTS", ["*"])
    with pytest.raises(RuntimeError, match="TRUSTED_HOSTS"):
        config.validate_runtime_config()

    _set_production(monkeypatch)
    monkeypatch.setattr(config, "RATE_LIMIT_REDIS_URL", "redis://redis.example.com:6379/0")
    with pytest.raises(RuntimeError, match="TLS"):
        config.validate_runtime_config()

    _set_production(monkeypatch)
    monkeypatch.setattr(config, "DATABASE_URL", "postgresql+psycopg://user:pass@db.example.com/scheme")
    with pytest.raises(RuntimeError, match="sslmode"):
        config.validate_runtime_config()
