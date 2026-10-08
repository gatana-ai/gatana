from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.deployment_metrics_response import DeploymentMetricsResponse
from ...models.schema_204 import Schema204
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    server_slug: str | Unset = UNSET,
    sandbox_id: str | Unset = UNSET,
    range_: Schema204 | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["serverSlug"] = server_slug

    params["sandboxId"] = sandbox_id

    json_range_: str | Unset = UNSET
    if not isinstance(range_, Unset):
        json_range_ = range_.value

    params["range"] = json_range_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/deployments/metrics",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeploymentMetricsResponse | None:
    if response.status_code == 200:
        response_200 = DeploymentMetricsResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DeploymentMetricsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    server_slug: str | Unset = UNSET,
    sandbox_id: str | Unset = UNSET,
    range_: Schema204 | Unset = UNSET,
) -> Response[DeploymentMetricsResponse]:
    """Get historical CPU, memory and storage usage metrics for a deployment. Provide either serverSlug or
    sandboxId; requires read permission on the server

    Args:
        server_slug (str | Unset):
        sandbox_id (str | Unset):
        range_ (Schema204 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeploymentMetricsResponse]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        sandbox_id=sandbox_id,
        range_=range_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    server_slug: str | Unset = UNSET,
    sandbox_id: str | Unset = UNSET,
    range_: Schema204 | Unset = UNSET,
) -> DeploymentMetricsResponse | None:
    """Get historical CPU, memory and storage usage metrics for a deployment. Provide either serverSlug or
    sandboxId; requires read permission on the server

    Args:
        server_slug (str | Unset):
        sandbox_id (str | Unset):
        range_ (Schema204 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeploymentMetricsResponse
    """

    return sync_detailed(
        client=client,
        server_slug=server_slug,
        sandbox_id=sandbox_id,
        range_=range_,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    server_slug: str | Unset = UNSET,
    sandbox_id: str | Unset = UNSET,
    range_: Schema204 | Unset = UNSET,
) -> Response[DeploymentMetricsResponse]:
    """Get historical CPU, memory and storage usage metrics for a deployment. Provide either serverSlug or
    sandboxId; requires read permission on the server

    Args:
        server_slug (str | Unset):
        sandbox_id (str | Unset):
        range_ (Schema204 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeploymentMetricsResponse]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        sandbox_id=sandbox_id,
        range_=range_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    server_slug: str | Unset = UNSET,
    sandbox_id: str | Unset = UNSET,
    range_: Schema204 | Unset = UNSET,
) -> DeploymentMetricsResponse | None:
    """Get historical CPU, memory and storage usage metrics for a deployment. Provide either serverSlug or
    sandboxId; requires read permission on the server

    Args:
        server_slug (str | Unset):
        sandbox_id (str | Unset):
        range_ (Schema204 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeploymentMetricsResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            server_slug=server_slug,
            sandbox_id=sandbox_id,
            range_=range_,
        )
    ).parsed
