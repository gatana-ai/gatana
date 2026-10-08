"""Gatana API client with configuration loading.

This module is hand-written and **not** overwritten by ``just generate``.
The generated ``Client`` and ``AuthenticatedClient`` classes live in
``_base_client.py`` and are re-exported here so that the generated API
modules (which import ``from ...client import …``) continue to work.
"""

from __future__ import annotations

from typing import Any

from ._base_client import AuthenticatedClient, Client  # noqa: F401 — re-export
from .config import (
    ConfigLoader,
    EnvConfigStrategy,
    FileConfigStrategy,
    GatanaConfig,
    OptionsConfigStrategy,
)


def GatanaClient(
    *,
    token: str | None = None,
    org_id: str | None = None,
    base_url: str | None = None,
    config_loader: ConfigLoader | None = None,
    **kwargs: Any,
) -> AuthenticatedClient:
    """Create an authenticated Gatana API client.

    Configuration is resolved in the following priority order:

    1. **Explicit parameters** — ``token`` + (``org_id`` or ``base_url``)
    2. **Environment variables** — ``GATANA_API_KEY`` + ``GATANA_ORG_ID`` / ``GATANA_BASE_URL``
    3. **Config file** — ``~/.gatana.config`` (same format as the JS SDK)

    You can also supply a custom *config_loader* to override the strategy chain.

    All extra keyword arguments are forwarded to :class:`AuthenticatedClient`.

    Examples::

        # Explicit (unchanged from previous API)
        client = GatanaClient(token="sk-...", org_id="my-org")

        # Zero-config — resolved from env vars or ~/.gatana.config
        client = GatanaClient()

        # Custom loader
        loader = ConfigLoader([OptionsConfigStrategy(api_key="sk-...", org_id="my-org")])
        client = GatanaClient(config_loader=loader)
    """
    # Fast path: fully explicit arguments (backward-compatible)
    if token is not None and (org_id is not None or base_url is not None):
        resolved_url = base_url if base_url is not None else f"https://{org_id}.gatana.ai/api/v1"
        return AuthenticatedClient(base_url=resolved_url, token=token, **kwargs)

    # Use the provided config loader, or build the default chain
    if config_loader is None:
        config_loader = ConfigLoader(
            [
                OptionsConfigStrategy(api_key=token, org_id=org_id, base_url=base_url),
                EnvConfigStrategy(),
                FileConfigStrategy(),
            ]
        )

    config: GatanaConfig = config_loader.get_config()
    return AuthenticatedClient(base_url=config.base_url, token=config.token, **kwargs)
