from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.server_running_status_response import ServerRunningStatusResponse
from ...types import Response


def _get_kwargs(
    server_slug: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/mcp-servers/{server_slug}/running-status".format(
            server_slug=quote(str(server_slug), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ServerRunningStatusResponse | None:
    if response.status_code == 200:
        response_200 = ServerRunningStatusResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ServerRunningStatusResponse]:
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
) -> Response[ServerRunningStatusResponse]:
    r"""Get the running status of an MCP server. Servers with transport type \"stdio\" or \"hosted\" report
    the status of their containers. All other servers always report as running

    Args:
        server_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ServerRunningStatusResponse]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
) -> ServerRunningStatusResponse | None:
    r"""Get the running status of an MCP server. Servers with transport type \"stdio\" or \"hosted\" report
    the status of their containers. All other servers always report as running

    Args:
        server_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ServerRunningStatusResponse
    """

    return sync_detailed(
        server_slug=server_slug,
        client=client,
    ).parsed


async def asyncio_detailed(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ServerRunningStatusResponse]:
    r"""Get the running status of an MCP server. Servers with transport type \"stdio\" or \"hosted\" report
    the status of their containers. All other servers always report as running

    Args:
        server_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ServerRunningStatusResponse]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
) -> ServerRunningStatusResponse | None:
    r"""Get the running status of an MCP server. Servers with transport type \"stdio\" or \"hosted\" report
    the status of their containers. All other servers always report as running

    Args:
        server_slug (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ServerRunningStatusResponse
    """

    return (
        await asyncio_detailed(
            server_slug=server_slug,
            client=client,
        )
    ).parsed
