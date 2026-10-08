"""Configuration loading for the Gatana Python SDK.

Resolves authentication in priority order:

1. **Explicit options** — ``api_key`` + ``org_id`` or ``base_url`` passed directly
2. **Environment variables** — ``GATANA_API_KEY`` + ``GATANA_ORG_ID`` (or ``GATANA_BASE_URL``)
3. **Config file** ``~/.gatana.config`` — API key or access token per organization

This mirrors the behaviour of the JavaScript SDK (``gatana-sdk``).
"""

from __future__ import annotations

import json
import logging
import os
from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("gatana")

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

CONFIG_FILE_NAME = ".gatana.config"


@dataclass(frozen=True)
class GatanaConfig:
    """Resolved configuration needed to create an authenticated client."""

    base_url: str
    token: str


@dataclass
class OrganizationConfig:
    """Per-organization entry stored in ``~/.gatana.config``."""

    base_url: str
    api_key: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    expires_at: int | None = None


@dataclass
class GatanaFileConfig:
    """Root structure of ``~/.gatana.config``."""

    orgs: dict[str, OrganizationConfig]
    default_org_id: str | None = None


# ---------------------------------------------------------------------------
# Config-file helpers
# ---------------------------------------------------------------------------


def get_config_file_path() -> Path:
    """Return the canonical path of the Gatana config file."""
    return Path.home() / CONFIG_FILE_NAME


def read_config(path: Path | None = None) -> GatanaFileConfig:
    """Read and parse ``~/.gatana.config``, returning an empty config on any error."""
    config_path = path or get_config_file_path()
    try:
        if not config_path.exists():
            return GatanaFileConfig(orgs={})

        raw = json.loads(config_path.read_text(encoding="utf-8"))

        # Migrate legacy flat config → new ``orgs`` structure (matches JS SDK)
        if "orgId" in raw and "orgs" not in raw:
            org_id: str = raw["orgId"]
            base_url = raw.get("baseUrl") or f"https://{org_id}.gatana.ai"
            raw["orgs"] = {
                org_id: {
                    "baseUrl": base_url,
                    "apiKey": raw.get("apiKey"),
                },
            }
            raw["defaultOrgId"] = org_id

        orgs: dict[str, OrganizationConfig] = {}
        for key, value in (raw.get("orgs") or {}).items():
            tokens = value.get("tokens") or {}
            orgs[key] = OrganizationConfig(
                base_url=value.get("baseUrl", f"https://{key}.gatana.ai"),
                api_key=value.get("apiKey"),
                access_token=tokens.get("access_token"),
                refresh_token=tokens.get("refresh_token"),
                expires_at=tokens.get("expires_at"),
            )

        return GatanaFileConfig(
            orgs=orgs,
            default_org_id=raw.get("defaultOrgId"),
        )
    except Exception:
        logger.debug("Failed to read config file at %s", config_path, exc_info=True)
        return GatanaFileConfig(orgs={})


def write_config(config: GatanaFileConfig, path: Path | None = None) -> None:
    """Serialize *config* to ``~/.gatana.config``."""
    config_path = path or get_config_file_path()
    raw: dict = {"orgs": {}}

    for key, org in config.orgs.items():
        entry: dict = {"baseUrl": org.base_url}
        if org.api_key:
            entry["apiKey"] = org.api_key
        if org.access_token or org.refresh_token:
            entry["tokens"] = {}
            if org.access_token:
                entry["tokens"]["access_token"] = org.access_token
            if org.refresh_token:
                entry["tokens"]["refresh_token"] = org.refresh_token
            if org.expires_at is not None:
                entry["tokens"]["expires_at"] = org.expires_at
        raw["orgs"][key] = entry

    if config.default_org_id:
        raw["defaultOrgId"] = config.default_org_id

    config_path.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Strategy pattern
# ---------------------------------------------------------------------------


class ConfigStrategy(ABC):
    """Abstract base for a single configuration source."""

    @abstractmethod
    def get_config(self) -> GatanaConfig | None:
        """Return resolved config, or ``None`` if this strategy cannot provide one."""


class OptionsConfigStrategy(ConfigStrategy):
    """Resolve config from explicitly passed options.

    Parameters
    ----------
    api_key:
        API key (token) for authentication.
    org_id:
        Organization ID — derives ``https://{org_id}.gatana.ai/api/v1``.
    base_url:
        Explicit base URL.  Takes precedence over *org_id*.
    """

    def __init__(
        self,
        api_key: str | None = None,
        org_id: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self._api_key = api_key
        self._org_id = org_id
        self._base_url = base_url

    def get_config(self) -> GatanaConfig | None:
        if not self._api_key:
            return None
        if not self._org_id and not self._base_url:
            return None
        base_url = self._base_url or f"https://{self._org_id}.gatana.ai/api/v1"
        return GatanaConfig(base_url=base_url, token=self._api_key)


class EnvConfigStrategy(ConfigStrategy):
    """Resolve config from environment variables.

    Recognised variables (same as the JavaScript SDK):

    * ``GATANA_API_KEY`` — API key for authentication
    * ``GATANA_ORG_ID`` — organization ID (derives ``https://<org_id>.gatana.ai/api/v1``)
    * ``GATANA_BASE_URL`` — override the base URL directly
    """

    def get_config(self) -> GatanaConfig | None:
        api_key = os.environ.get("GATANA_API_KEY")
        org_id = os.environ.get("GATANA_ORG_ID")
        base_url = os.environ.get("GATANA_BASE_URL")

        if not api_key:
            return None
        if not org_id and not base_url:
            return None

        resolved_url = base_url or f"https://{org_id}.gatana.ai/api/v1"
        return GatanaConfig(base_url=resolved_url, token=api_key)


class FileConfigStrategy(ConfigStrategy):
    """Resolve config from the ``~/.gatana.config`` JSON file.

    The org to use is selected in this order:

    1. Explicit *org_id* passed to the constructor.
    2. ``GATANA_ORG_ID`` environment variable.
    3. ``defaultOrgId`` field in the config file.

    Within an organization entry the strategy looks for ``apiKey`` first,
    then ``tokens.access_token``.

    .. note::

       Unlike the JavaScript SDK, token refresh via OIDC is **not**
       performed here.  Pre-refreshed tokens (or API keys) are expected.
    """

    def __init__(self, org_id: str | None = None, config_path: Path | None = None) -> None:
        self._org_id = org_id
        self._config_path = config_path

    def get_config(self) -> GatanaConfig | None:
        org_id = self._org_id or os.environ.get("GATANA_ORG_ID")

        file_config = read_config(self._config_path)

        if not org_id:
            org_id = file_config.default_org_id
        if not org_id:
            return None

        logger.debug("FileConfigStrategy loading config for org_id=%s", org_id)

        org = file_config.orgs.get(org_id)
        if org is None:
            return None

        token: str | None = org.api_key or org.access_token
        if not token:
            return None

        return GatanaConfig(base_url=org.base_url, token=token)


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------


class ConfigLoader:
    """Chain multiple :class:`ConfigStrategy` instances in priority order.

    Iterates through strategies and returns the first successful config.

    Example::

        loader = ConfigLoader([
            OptionsConfigStrategy(api_key="sk-...", org_id="my-org"),
            EnvConfigStrategy(),
            FileConfigStrategy(),
        ])
        config = loader.get_config()
    """

    def __init__(self, strategies: Sequence[ConfigStrategy]) -> None:
        self._strategies = list(strategies)

    def get_config(self) -> GatanaConfig:
        """Return the first resolved config, or raise :class:`ValueError`."""
        for strategy in self._strategies:
            config = strategy.get_config()
            if config is not None:
                return config
        raise ValueError(
            "No valid configuration found from any strategy. "
            "Provide api_key + org_id/base_url explicitly, set GATANA_API_KEY + "
            "GATANA_ORG_ID environment variables, or create a ~/.gatana.config file."
        )
