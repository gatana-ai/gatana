from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.deployment_status_response import DeploymentStatusResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    sandbox_id: str | Unset = UNSET,
    server_slug: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["sandboxId"] = sandbox_id

    params["serverSlug"] = server_slug

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/deployments/status",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeploymentStatusResponse | None:
    if response.status_code == 200:
        response_200 = DeploymentStatusResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DeploymentStatusResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    sandbox_id: str | Unset = UNSET,
    server_slug: str | Unset = UNSET,
) -> Response[DeploymentStatusResponse]:
    """Get the deployment status of an MCP server or a sandbox. Provide either serverSlug or sandboxId;
    requires read permission on the server

    Args:
        sandbox_id (str | Unset):
        server_slug (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeploymentStatusResponse]
    """

    kwargs = _get_kwargs(
        sandbox_id=sandbox_id,
        server_slug=server_slug,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    sandbox_id: str | Unset = UNSET,
    server_slug: str | Unset = UNSET,
) -> DeploymentStatusResponse | None:
    """Get the deployment status of an MCP server or a sandbox. Provide either serverSlug or sandboxId;
    requires read permission on the server

    Args:
        sandbox_id (str | Unset):
        server_slug (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeploymentStatusResponse
    """

    return sync_detailed(
        client=client,
        sandbox_id=sandbox_id,
        server_slug=server_slug,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    sandbox_id: str | Unset = UNSET,
    server_slug: str | Unset = UNSET,
) -> Response[DeploymentStatusResponse]:
    """Get the deployment status of an MCP server or a sandbox. Provide either serverSlug or sandboxId;
    requires read permission on the server

    Args:
        sandbox_id (str | Unset):
        server_slug (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeploymentStatusResponse]
    """

    kwargs = _get_kwargs(
        sandbox_id=sandbox_id,
        server_slug=server_slug,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    sandbox_id: str | Unset = UNSET,
    server_slug: str | Unset = UNSET,
) -> DeploymentStatusResponse | None:
    """Get the deployment status of an MCP server or a sandbox. Provide either serverSlug or sandboxId;
    requires read permission on the server

    Args:
        sandbox_id (str | Unset):
        server_slug (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeploymentStatusResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            sandbox_id=sandbox_id,
            server_slug=server_slug,
        )
    ).parsed
