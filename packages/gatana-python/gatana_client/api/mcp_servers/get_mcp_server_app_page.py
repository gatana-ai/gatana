from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_mcp_server_app_page_response import GetMcpServerAppPageResponse
from ...types import UNSET, Response


def _get_kwargs(
    server_slug: str,
    *,
    uri: str,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["uri"] = uri

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/mcp-servers/{server_slug}/app-pages".format(
            server_slug=quote(str(server_slug), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetMcpServerAppPageResponse | None:
    if response.status_code == 200:
        response_200 = GetMcpServerAppPageResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetMcpServerAppPageResponse]:
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
    uri: str,
) -> Response[GetMcpServerAppPageResponse]:
    """Read an MCP App page with the caller's credentials and record the read in the audit log

    Args:
        server_slug (str):
        uri (str): Page URI published by the MCP server

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetMcpServerAppPageResponse]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        uri=uri,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    uri: str,
) -> GetMcpServerAppPageResponse | None:
    """Read an MCP App page with the caller's credentials and record the read in the audit log

    Args:
        server_slug (str):
        uri (str): Page URI published by the MCP server

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetMcpServerAppPageResponse
    """

    return sync_detailed(
        server_slug=server_slug,
        client=client,
        uri=uri,
    ).parsed


async def asyncio_detailed(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    uri: str,
) -> Response[GetMcpServerAppPageResponse]:
    """Read an MCP App page with the caller's credentials and record the read in the audit log

    Args:
        server_slug (str):
        uri (str): Page URI published by the MCP server

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetMcpServerAppPageResponse]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        uri=uri,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    uri: str,
) -> GetMcpServerAppPageResponse | None:
    """Read an MCP App page with the caller's credentials and record the read in the audit log

    Args:
        server_slug (str):
        uri (str): Page URI published by the MCP server

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetMcpServerAppPageResponse
    """

    return (
        await asyncio_detailed(
            server_slug=server_slug,
            client=client,
            uri=uri,
        )
    ).parsed
