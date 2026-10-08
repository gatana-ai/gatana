from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.schema_607 import Schema607
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    search: str | Unset = UNSET,
    schemas: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["search"] = search

    params["schemas"] = schemas

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/tools",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Schema607 | None:
    if response.status_code == 200:
        response_200 = Schema607.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Schema607]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    search: str | Unset = UNSET,
    schemas: str | Unset = UNSET,
) -> Response[Schema607]:
    """List all cached tools of every MCP server the caller has access to, including the disabled ones

    Args:
        search (str | Unset):
        schemas (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Schema607]
    """

    kwargs = _get_kwargs(
        search=search,
        schemas=schemas,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    search: str | Unset = UNSET,
    schemas: str | Unset = UNSET,
) -> Schema607 | None:
    """List all cached tools of every MCP server the caller has access to, including the disabled ones

    Args:
        search (str | Unset):
        schemas (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Schema607
    """

    return sync_detailed(
        client=client,
        search=search,
        schemas=schemas,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    search: str | Unset = UNSET,
    schemas: str | Unset = UNSET,
) -> Response[Schema607]:
    """List all cached tools of every MCP server the caller has access to, including the disabled ones

    Args:
        search (str | Unset):
        schemas (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Schema607]
    """

    kwargs = _get_kwargs(
        search=search,
        schemas=schemas,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    search: str | Unset = UNSET,
    schemas: str | Unset = UNSET,
) -> Schema607 | None:
    """List all cached tools of every MCP server the caller has access to, including the disabled ones

    Args:
        search (str | Unset):
        schemas (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Schema607
    """

    return (
        await asyncio_detailed(
            client=client,
            search=search,
            schemas=schemas,
        )
    ).parsed
