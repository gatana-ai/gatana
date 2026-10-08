from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.schema_172 import Schema172
from ...models.schema_626 import Schema626
from ...types import UNSET, Response, Unset


def _get_kwargs(
    server_slug: str,
    tool_name: str,
    *,
    body: Schema172 | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/mcp-servers/{server_slug}/tools/{tool_name}/isEnabled".format(
            server_slug=quote(str(server_slug), safe=""),
            tool_name=quote(str(tool_name), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Schema626 | None:
    if response.status_code == 200:
        response_200 = Schema626.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Schema626]:
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
    body: Schema172 | Unset = UNSET,
) -> Response[Schema626]:
    """Enable or disable a single tool of an MCP server. Tells the connected MCP clients that the tool list
    changed

    Args:
        server_slug (str):
        tool_name (str):
        body (Schema172 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Schema626]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        tool_name=tool_name,
        body=body,
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
    body: Schema172 | Unset = UNSET,
) -> Schema626 | None:
    """Enable or disable a single tool of an MCP server. Tells the connected MCP clients that the tool list
    changed

    Args:
        server_slug (str):
        tool_name (str):
        body (Schema172 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Schema626
    """

    return sync_detailed(
        server_slug=server_slug,
        tool_name=tool_name,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    server_slug: str,
    tool_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: Schema172 | Unset = UNSET,
) -> Response[Schema626]:
    """Enable or disable a single tool of an MCP server. Tells the connected MCP clients that the tool list
    changed

    Args:
        server_slug (str):
        tool_name (str):
        body (Schema172 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Schema626]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        tool_name=tool_name,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    server_slug: str,
    tool_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: Schema172 | Unset = UNSET,
) -> Schema626 | None:
    """Enable or disable a single tool of an MCP server. Tells the connected MCP clients that the tool list
    changed

    Args:
        server_slug (str):
        tool_name (str):
        body (Schema172 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Schema626
    """

    return (
        await asyncio_detailed(
            server_slug=server_slug,
            tool_name=tool_name,
            client=client,
            body=body,
        )
    ).parsed
