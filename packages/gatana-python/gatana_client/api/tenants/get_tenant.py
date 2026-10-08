from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_tenant_response_200 import GetTenantResponse200
from ...types import Response


def _get_kwargs(
    tenant_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/tenants/{tenant_id}".format(
            tenant_id=quote(str(tenant_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetTenantResponse200 | None:
    if response.status_code == 200:
        response_200 = GetTenantResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetTenantResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    tenant_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[GetTenantResponse200]:
    """Get tenant details

    Args:
        tenant_id (str): ID of the tenant

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetTenantResponse200]
    """

    kwargs = _get_kwargs(
        tenant_id=tenant_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    tenant_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> GetTenantResponse200 | None:
    """Get tenant details

    Args:
        tenant_id (str): ID of the tenant

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetTenantResponse200
    """

    return sync_detailed(
        tenant_id=tenant_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    tenant_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[GetTenantResponse200]:
    """Get tenant details

    Args:
        tenant_id (str): ID of the tenant

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetTenantResponse200]
    """

    kwargs = _get_kwargs(
        tenant_id=tenant_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    tenant_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> GetTenantResponse200 | None:
    """Get tenant details

    Args:
        tenant_id (str): ID of the tenant

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetTenantResponse200
    """

    return (
        await asyncio_detailed(
            tenant_id=tenant_id,
            client=client,
        )
    ).parsed
