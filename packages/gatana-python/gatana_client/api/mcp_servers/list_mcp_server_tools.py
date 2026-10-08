from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.schema_607 import Schema607
from ...types import UNSET, Response, Unset


def _get_kwargs(
    server_slug: str,
    *,
    schemas: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["schemas"] = schemas

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/mcp-servers/{server_slug}/tools".format(
            server_slug=quote(str(server_slug), safe=""),
        ),
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
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    schemas: str | Unset = UNSET,
) -> Response[Schema607]:
    """List all cached tools of an MCP server, including the disabled ones

    Args:
        server_slug (str):
        schemas (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Schema607]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        schemas=schemas,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    schemas: str | Unset = UNSET,
) -> Schema607 | None:
    """List all cached tools of an MCP server, including the disabled ones

    Args:
        server_slug (str):
        schemas (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Schema607
    """

    return sync_detailed(
        server_slug=server_slug,
        client=client,
        schemas=schemas,
    ).parsed


async def asyncio_detailed(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    schemas: str | Unset = UNSET,
) -> Response[Schema607]:
    """List all cached tools of an MCP server, including the disabled ones

    Args:
        server_slug (str):
        schemas (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Schema607]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        schemas=schemas,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    schemas: str | Unset = UNSET,
) -> Schema607 | None:
    """List all cached tools of an MCP server, including the disabled ones

    Args:
        server_slug (str):
        schemas (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Schema607
    """

    return (
        await asyncio_detailed(
            server_slug=server_slug,
            client=client,
            schemas=schemas,
        )
    ).parsed
