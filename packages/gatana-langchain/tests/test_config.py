"""Tests for the config loading module (gatana_client.config)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from gatana_client.config import (
    ConfigLoader,
    EnvConfigStrategy,
    FileConfigStrategy,
    GatanaFileConfig,
    OptionsConfigStrategy,
    OrganizationConfig,
    read_config,
    write_config,
)

# ---------------------------------------------------------------------------
# OptionsConfigStrategy
# ---------------------------------------------------------------------------


class TestOptionsConfigStrategy:
    def test_returns_config_with_api_key_and_org_id(self) -> None:
        strategy = OptionsConfigStrategy(api_key="sk-abc", org_id="my-org")
        config = strategy.get_config()
        assert config is not None
        assert config.token == "sk-abc"
        assert config.base_url == "https://my-org.gatana.ai/api/v1"

    def test_returns_config_with_api_key_and_base_url(self) -> None:
        strategy = OptionsConfigStrategy(
            api_key="sk-abc", base_url="https://custom.example.com/api/v1"
        )
        config = strategy.get_config()
        assert config is not None
        assert config.token == "sk-abc"
        assert config.base_url == "https://custom.example.com/api/v1"

    def test_base_url_takes_precedence_over_org_id(self) -> None:
        strategy = OptionsConfigStrategy(
            api_key="sk-abc",
            org_id="my-org",
            base_url="https://override.example.com",
        )
        config = strategy.get_config()
        assert config is not None
        assert config.base_url == "https://override.example.com"

    def test_returns_none_without_api_key(self) -> None:
        assert OptionsConfigStrategy(org_id="my-org").get_config() is None

    def test_returns_none_without_org_id_or_base_url(self) -> None:
        assert OptionsConfigStrategy(api_key="sk-abc").get_config() is None

    def test_returns_none_with_empty_api_key(self) -> None:
        assert OptionsConfigStrategy(api_key="", org_id="my-org").get_config() is None

    def test_returns_none_with_no_args(self) -> None:
        assert OptionsConfigStrategy().get_config() is None


# ---------------------------------------------------------------------------
# EnvConfigStrategy
# ---------------------------------------------------------------------------


class TestEnvConfigStrategy:
    def test_returns_config_from_env(self) -> None:
        env = {"GATANA_API_KEY": "sk-env", "GATANA_ORG_ID": "env-org"}
        with patch.dict(os.environ, env, clear=False):
            config = EnvConfigStrategy().get_config()
        assert config is not None
        assert config.token == "sk-env"
        assert config.base_url == "https://env-org.gatana.ai/api/v1"

    def test_base_url_env_takes_precedence(self) -> None:
        env = {
            "GATANA_API_KEY": "sk-env",
            "GATANA_ORG_ID": "env-org",
            "GATANA_BASE_URL": "https://override.example.com",
        }
        with patch.dict(os.environ, env, clear=False):
            config = EnvConfigStrategy().get_config()
        assert config is not None
        assert config.base_url == "https://override.example.com"

    def test_returns_none_without_api_key(self) -> None:
        env = {"GATANA_ORG_ID": "env-org"}
        with patch.dict(os.environ, env, clear=False):
            # Make sure GATANA_API_KEY is not set
            os.environ.pop("GATANA_API_KEY", None)
            config = EnvConfigStrategy().get_config()
        assert config is None

    def test_returns_none_without_org_id_or_base_url(self) -> None:
        env = {"GATANA_API_KEY": "sk-env"}
        with patch.dict(os.environ, env, clear=False):
            os.environ.pop("GATANA_ORG_ID", None)
            os.environ.pop("GATANA_BASE_URL", None)
            config = EnvConfigStrategy().get_config()
        assert config is None


# ---------------------------------------------------------------------------
# FileConfigStrategy
# ---------------------------------------------------------------------------


class TestFileConfigStrategy:
    def _write_config_file(self, tmp_path: Path, data: dict) -> Path:
        config_path = tmp_path / ".gatana.config"
        config_path.write_text(json.dumps(data), encoding="utf-8")
        return config_path

    def test_reads_api_key_from_file(self, tmp_path: Path) -> None:
        config_path = self._write_config_file(
            tmp_path,
            {
                "orgs": {
                    "my-org": {
                        "baseUrl": "https://my-org.gatana.ai",
                        "apiKey": "sk-file",
                    }
                },
                "defaultOrgId": "my-org",
            },
        )
        strategy = FileConfigStrategy(config_path=config_path)
        config = strategy.get_config()
        assert config is not None
        assert config.token == "sk-file"
        assert config.base_url == "https://my-org.gatana.ai"

    def test_reads_access_token_from_file(self, tmp_path: Path) -> None:
        config_path = self._write_config_file(
            tmp_path,
            {
                "orgs": {
                    "my-org": {
                        "baseUrl": "https://my-org.gatana.ai",
                        "tokens": {"access_token": "at-123"},
                    }
                },
                "defaultOrgId": "my-org",
            },
        )
        strategy = FileConfigStrategy(config_path=config_path)
        config = strategy.get_config()
        assert config is not None
        assert config.token == "at-123"

    def test_api_key_takes_precedence_over_access_token(self, tmp_path: Path) -> None:
        config_path = self._write_config_file(
            tmp_path,
            {
                "orgs": {
                    "my-org": {
                        "baseUrl": "https://my-org.gatana.ai",
                        "apiKey": "sk-file",
                        "tokens": {"access_token": "at-123"},
                    }
                },
                "defaultOrgId": "my-org",
            },
        )
        strategy = FileConfigStrategy(config_path=config_path)
        config = strategy.get_config()
        assert config is not None
        assert config.token == "sk-file"

    def test_explicit_org_id_overrides_default(self, tmp_path: Path) -> None:
        config_path = self._write_config_file(
            tmp_path,
            {
                "orgs": {
                    "default-org": {
                        "baseUrl": "https://default-org.gatana.ai",
                        "apiKey": "sk-default",
                    },
                    "other-org": {
                        "baseUrl": "https://other-org.gatana.ai",
                        "apiKey": "sk-other",
                    },
                },
                "defaultOrgId": "default-org",
            },
        )
        strategy = FileConfigStrategy(org_id="other-org", config_path=config_path)
        config = strategy.get_config()
        assert config is not None
        assert config.token == "sk-other"
        assert config.base_url == "https://other-org.gatana.ai"

    def test_env_org_id_used_when_no_explicit(self, tmp_path: Path) -> None:
        config_path = self._write_config_file(
            tmp_path,
            {
                "orgs": {
                    "env-org": {
                        "baseUrl": "https://env-org.gatana.ai",
                        "apiKey": "sk-env-org",
                    }
                },
            },
        )
        with patch.dict(os.environ, {"GATANA_ORG_ID": "env-org"}, clear=False):
            strategy = FileConfigStrategy(config_path=config_path)
            config = strategy.get_config()
        assert config is not None
        assert config.token == "sk-env-org"

    def test_returns_none_for_missing_org(self, tmp_path: Path) -> None:
        config_path = self._write_config_file(
            tmp_path,
            {
                "orgs": {
                    "my-org": {"baseUrl": "https://my-org.gatana.ai", "apiKey": "sk-x"}
                },
                "defaultOrgId": "my-org",
            },
        )
        strategy = FileConfigStrategy(org_id="nonexistent", config_path=config_path)
        assert strategy.get_config() is None

    def test_returns_none_for_missing_file(self, tmp_path: Path) -> None:
        config_path = tmp_path / ".gatana.config"
        strategy = FileConfigStrategy(org_id="my-org", config_path=config_path)
        assert strategy.get_config() is None

    def test_returns_none_when_no_org_id_and_no_default(self, tmp_path: Path) -> None:
        config_path = self._write_config_file(
            tmp_path,
            {
                "orgs": {
                    "my-org": {"baseUrl": "https://my-org.gatana.ai", "apiKey": "sk-x"}
                }
            },
        )
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GATANA_ORG_ID", None)
            strategy = FileConfigStrategy(config_path=config_path)
            assert strategy.get_config() is None

    def test_legacy_flat_config_migration(self, tmp_path: Path) -> None:
        config_path = self._write_config_file(
            tmp_path,
            {
                "orgId": "legacy-org",
                "apiKey": "sk-legacy",
                "baseUrl": "https://legacy-org.gatana.ai",
            },
        )
        strategy = FileConfigStrategy(config_path=config_path)
        config = strategy.get_config()
        assert config is not None
        assert config.token == "sk-legacy"
        assert config.base_url == "https://legacy-org.gatana.ai"

    def test_derives_base_url_from_org_id(self, tmp_path: Path) -> None:
        """When baseUrl is missing in the org entry, derive it from the org key."""
        config_path = self._write_config_file(
            tmp_path,
            {
                "orgs": {"auto-org": {"apiKey": "sk-auto"}},
                "defaultOrgId": "auto-org",
            },
        )
        strategy = FileConfigStrategy(config_path=config_path)
        config = strategy.get_config()
        assert config is not None
        assert config.base_url == "https://auto-org.gatana.ai"


# ---------------------------------------------------------------------------
# read_config / write_config round-trip
# ---------------------------------------------------------------------------


class TestReadWriteConfig:
    def test_round_trip(self, tmp_path: Path) -> None:
        config_path = tmp_path / ".gatana.config"
        original = GatanaFileConfig(
            orgs={
                "org-a": OrganizationConfig(
                    base_url="https://org-a.gatana.ai",
                    api_key="sk-a",
                ),
                "org-b": OrganizationConfig(
                    base_url="https://org-b.gatana.ai",
                    access_token="at-b",
                    refresh_token="rt-b",
                    expires_at=1700000000,
                ),
            },
            default_org_id="org-a",
        )
        write_config(original, path=config_path)
        loaded = read_config(path=config_path)

        assert loaded.default_org_id == "org-a"
        assert loaded.orgs["org-a"].api_key == "sk-a"
        assert loaded.orgs["org-b"].access_token == "at-b"
        assert loaded.orgs["org-b"].refresh_token == "rt-b"
        assert loaded.orgs["org-b"].expires_at == 1700000000

    def test_read_empty_when_file_missing(self, tmp_path: Path) -> None:
        config_path = tmp_path / "nonexistent"
        config = read_config(path=config_path)
        assert config.orgs == {}
        assert config.default_org_id is None

    def test_read_empty_on_malformed_json(self, tmp_path: Path) -> None:
        config_path = tmp_path / ".gatana.config"
        config_path.write_text("not valid json {{{", encoding="utf-8")
        config = read_config(path=config_path)
        assert config.orgs == {}


# ---------------------------------------------------------------------------
# ConfigLoader
# ---------------------------------------------------------------------------


class TestConfigLoader:
    def test_returns_first_successful_strategy(self) -> None:
        loader = ConfigLoader(
            [
                OptionsConfigStrategy(),  # returns None
                OptionsConfigStrategy(api_key="sk-second", org_id="org-2"),
                OptionsConfigStrategy(api_key="sk-third", org_id="org-3"),
            ]
        )
        config = loader.get_config()
        assert config.token == "sk-second"

    def test_raises_when_no_strategy_succeeds(self) -> None:
        loader = ConfigLoader(
            [
                OptionsConfigStrategy(),
                OptionsConfigStrategy(api_key="sk-no-org"),
            ]
        )
        with pytest.raises(ValueError, match="No valid configuration found"):
            loader.get_config()

    def test_options_take_precedence_over_env(self) -> None:
        env = {"GATANA_API_KEY": "sk-env", "GATANA_ORG_ID": "env-org"}
        with patch.dict(os.environ, env, clear=False):
            loader = ConfigLoader(
                [
                    OptionsConfigStrategy(api_key="sk-opts", org_id="opts-org"),
                    EnvConfigStrategy(),
                ]
            )
            config = loader.get_config()
        assert config.token == "sk-opts"

    def test_env_used_when_options_fail(self) -> None:
        env = {"GATANA_API_KEY": "sk-env", "GATANA_ORG_ID": "env-org"}
        with patch.dict(os.environ, env, clear=False):
            loader = ConfigLoader(
                [
                    OptionsConfigStrategy(),  # no api_key → None
                    EnvConfigStrategy(),
                ]
            )
            config = loader.get_config()
        assert config.token == "sk-env"

    def test_file_used_as_last_resort(self, tmp_path: Path) -> None:
        config_path = tmp_path / ".gatana.config"
        config_path.write_text(
            json.dumps(
                {
                    "orgs": {
                        "file-org": {
                            "baseUrl": "https://file-org.gatana.ai",
                            "apiKey": "sk-file",
                        }
                    },
                    "defaultOrgId": "file-org",
                }
            ),
            encoding="utf-8",
        )
        # Clear env vars so EnvConfigStrategy returns None
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GATANA_API_KEY", None)
            os.environ.pop("GATANA_ORG_ID", None)
            os.environ.pop("GATANA_BASE_URL", None)
            loader = ConfigLoader(
                [
                    OptionsConfigStrategy(),
                    EnvConfigStrategy(),
                    FileConfigStrategy(config_path=config_path),
                ]
            )
            config = loader.get_config()
        assert config.token == "sk-file"


# ---------------------------------------------------------------------------
# GatanaClient() integration
# ---------------------------------------------------------------------------


class TestGatanaClientConfigLoading:
    """Integration tests: GatanaClient() with the config loading chain."""

    def test_explicit_token_and_org_id(self) -> None:
        """Backward-compatible: explicit token + org_id still works."""
        from gatana_client import GatanaClient

        client = GatanaClient(token="sk-explicit", org_id="my-org")
        assert client.token == "sk-explicit"

    def test_explicit_token_and_base_url(self) -> None:
        from gatana_client import GatanaClient

        client = GatanaClient(
            token="sk-explicit", base_url="https://custom.example.com/api/v1"
        )
        assert client.token == "sk-explicit"

    def test_resolves_from_env_vars(self) -> None:
        from gatana_client import GatanaClient

        env = {"GATANA_API_KEY": "sk-from-env", "GATANA_ORG_ID": "env-org"}
        with patch.dict(os.environ, env, clear=False):
            client = GatanaClient()
        assert client.token == "sk-from-env"

    def test_resolves_from_config_file(self, tmp_path: Path) -> None:
        from gatana_client import ConfigLoader, FileConfigStrategy, GatanaClient

        config_path = tmp_path / ".gatana.config"
        config_path.write_text(
            json.dumps(
                {
                    "orgs": {
                        "file-org": {
                            "baseUrl": "https://file-org.gatana.ai/api/v1",
                            "apiKey": "sk-from-file",
                        }
                    },
                    "defaultOrgId": "file-org",
                }
            ),
            encoding="utf-8",
        )
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GATANA_API_KEY", None)
            os.environ.pop("GATANA_ORG_ID", None)
            os.environ.pop("GATANA_BASE_URL", None)
            loader = ConfigLoader([FileConfigStrategy(config_path=config_path)])
            client = GatanaClient(config_loader=loader)
        assert client.token == "sk-from-file"

    def test_raises_when_nothing_configured(self) -> None:
        from gatana_client import GatanaClient

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("GATANA_API_KEY", None)
            os.environ.pop("GATANA_ORG_ID", None)
            os.environ.pop("GATANA_BASE_URL", None)
            # Point to a non-existent file so FileConfigStrategy also fails
            with (
                patch(
                    "gatana_client.config.get_config_file_path",
                    return_value=Path("/tmp/nonexistent_gatana_config"),
                ),
                pytest.raises(ValueError, match="No valid configuration found"),
            ):
                GatanaClient()
