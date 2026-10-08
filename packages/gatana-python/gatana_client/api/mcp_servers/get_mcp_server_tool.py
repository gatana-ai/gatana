from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.server_tool_dto import ServerToolDto
from ...types import Response


def _get_kwargs(
    server_slug: str,
    tool_name: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/mcp-servers/{server_slug}/tools/{tool_name}".format(
            server_slug=quote(str(server_slug), safe=""),
            tool_name=quote(str(tool_name), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ServerToolDto | None:
    if response.status_code == 200:
        response_200 = ServerToolDto.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ServerToolDto]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    server_slug: str,
    tool_name: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ServerToolDto]:
    """Get a single tool of an MCP server

    Args:
        server_slug (str):
        tool_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ServerToolDto]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        tool_name=tool_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    server_slug: str,
    tool_name: str,
    *,
    client: AuthenticatedClient | Client,
) -> ServerToolDto | None:
    """Get a single tool of an MCP server

    Args:
        server_slug (str):
        tool_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ServerToolDto
    """

    return sync_detailed(
        server_slug=server_slug,
        tool_name=tool_name,
        client=client,
    ).parsed


async def asyncio_detailed(
    server_slug: str,
    tool_name: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ServerToolDto]:
    """Get a single tool of an MCP server

    Args:
        server_slug (str):
        tool_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ServerToolDto]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        tool_name=tool_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    server_slug: str,
    tool_name: str,
    *,
    client: AuthenticatedClient | Client,
) -> ServerToolDto | None:
    """Get a single tool of an MCP server

    Args:
        server_slug (str):
        tool_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ServerToolDto
    """

    return (
        await asyncio_detailed(
            server_slug=server_slug,
            tool_name=tool_name,
            client=client,
        )
    ).parsed
