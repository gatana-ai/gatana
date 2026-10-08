from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_tools_search_response_200 import GetToolsSearchResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    server_id: str | Unset = UNSET,
    server_slug: str | Unset = UNSET,
    search: str | Unset = UNSET,
    page: str | Unset = UNSET,
    limit: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["serverId"] = server_id

    params["serverSlug"] = server_slug

    params["search"] = search

    params["page"] = page

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/tools/search",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetToolsSearchResponse200 | None:
    if response.status_code == 200:
        response_200 = GetToolsSearchResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetToolsSearchResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    server_id: str | Unset = UNSET,
    server_slug: str | Unset = UNSET,
    search: str | Unset = UNSET,
    page: str | Unset = UNSET,
    limit: str | Unset = UNSET,
) -> Response[GetToolsSearchResponse200]:
    """Search the cached tools of every MCP server the caller has access to, page by page, including the
    disabled ones. Returns a list of tools paginated.

    Args:
        server_id (str | Unset):
        server_slug (str | Unset):
        search (str | Unset):
        page (str | Unset):
        limit (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetToolsSearchResponse200]
    """

    kwargs = _get_kwargs(
        server_id=server_id,
        server_slug=server_slug,
        search=search,
        page=page,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    server_id: str | Unset = UNSET,
    server_slug: str | Unset = UNSET,
    search: str | Unset = UNSET,
    page: str | Unset = UNSET,
    limit: str | Unset = UNSET,
) -> GetToolsSearchResponse200 | None:
    """Search the cached tools of every MCP server the caller has access to, page by page, including the
    disabled ones. Returns a list of tools paginated.

    Args:
        server_id (str | Unset):
        server_slug (str | Unset):
        search (str | Unset):
        page (str | Unset):
        limit (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetToolsSearchResponse200
    """

    return sync_detailed(
        client=client,
        server_id=server_id,
        server_slug=server_slug,
        search=search,
        page=page,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    server_id: str | Unset = UNSET,
    server_slug: str | Unset = UNSET,
    search: str | Unset = UNSET,
    page: str | Unset = UNSET,
    limit: str | Unset = UNSET,
) -> Response[GetToolsSearchResponse200]:
    """Search the cached tools of every MCP server the caller has access to, page by page, including the
    disabled ones. Returns a list of tools paginated.

    Args:
        server_id (str | Unset):
        server_slug (str | Unset):
        search (str | Unset):
        page (str | Unset):
        limit (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetToolsSearchResponse200]
    """

    kwargs = _get_kwargs(
        server_id=server_id,
        server_slug=server_slug,
        search=search,
        page=page,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    server_id: str | Unset = UNSET,
    server_slug: str | Unset = UNSET,
    search: str | Unset = UNSET,
    page: str | Unset = UNSET,
    limit: str | Unset = UNSET,
) -> GetToolsSearchResponse200 | None:
    """Search the cached tools of every MCP server the caller has access to, page by page, including the
    disabled ones. Returns a list of tools paginated.

    Args:
        server_id (str | Unset):
        server_slug (str | Unset):
        search (str | Unset):
        page (str | Unset):
        limit (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetToolsSearchResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            server_id=server_id,
            server_slug=server_slug,
            search=search,
            page=page,
            limit=limit,
        )
    ).parsed
