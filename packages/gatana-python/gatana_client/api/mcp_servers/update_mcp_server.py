from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.schema_578 import Schema578
from ...models.update_server_request import UpdateServerRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    server_slug: str,
    *,
    body: UpdateServerRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/mcp-servers/{server_slug}".format(
            server_slug=quote(str(server_slug), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Schema578 | None:
    if response.status_code == 200:
        response_200 = Schema578.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Schema578]:
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
    body: UpdateServerRequest | Unset = UNSET,
) -> Response[Schema578]:
    """Update an MCP server. The slug can be changed, which also changes the URL of the server

    Args:
        server_slug (str):
        body (UpdateServerRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Schema578]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateServerRequest | Unset = UNSET,
) -> Schema578 | None:
    """Update an MCP server. The slug can be changed, which also changes the URL of the server

    Args:
        server_slug (str):
        body (UpdateServerRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Schema578
    """

    return sync_detailed(
        server_slug=server_slug,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateServerRequest | Unset = UNSET,
) -> Response[Schema578]:
    """Update an MCP server. The slug can be changed, which also changes the URL of the server

    Args:
        server_slug (str):
        body (UpdateServerRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Schema578]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateServerRequest | Unset = UNSET,
) -> Schema578 | None:
    """Update an MCP server. The slug can be changed, which also changes the URL of the server

    Args:
        server_slug (str):
        body (UpdateServerRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Schema578
    """

    return (
        await asyncio_detailed(
            server_slug=server_slug,
            client=client,
            body=body,
        )
    ).parsed
