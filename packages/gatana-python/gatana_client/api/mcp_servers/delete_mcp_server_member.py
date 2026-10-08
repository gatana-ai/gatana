from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_mcp_server_member_response_200 import DeleteMcpServerMemberResponse200
from ...models.schema_175 import Schema175
from ...types import Response


def _get_kwargs(
    server_slug: str,
    member_type: Schema175,
    member_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/mcp-servers/{server_slug}/members/{member_type}/{member_id}".format(
            server_slug=quote(str(server_slug), safe=""),
            member_type=quote(str(member_type), safe=""),
            member_id=quote(str(member_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeleteMcpServerMemberResponse200 | None:
    if response.status_code == 200:
        response_200 = DeleteMcpServerMemberResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DeleteMcpServerMemberResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    server_slug: str,
    member_type: Schema175,
    member_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeleteMcpServerMemberResponse200]:
    """Remove a user or a team from the members of an MCP server

    Args:
        server_slug (str):
        member_type (Schema175):
        member_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteMcpServerMemberResponse200]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        member_type=member_type,
        member_id=member_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    server_slug: str,
    member_type: Schema175,
    member_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> DeleteMcpServerMemberResponse200 | None:
    """Remove a user or a team from the members of an MCP server

    Args:
        server_slug (str):
        member_type (Schema175):
        member_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteMcpServerMemberResponse200
    """

    return sync_detailed(
        server_slug=server_slug,
        member_type=member_type,
        member_id=member_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    server_slug: str,
    member_type: Schema175,
    member_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeleteMcpServerMemberResponse200]:
    """Remove a user or a team from the members of an MCP server

    Args:
        server_slug (str):
        member_type (Schema175):
        member_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteMcpServerMemberResponse200]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        member_type=member_type,
        member_id=member_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    server_slug: str,
    member_type: Schema175,
    member_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> DeleteMcpServerMemberResponse200 | None:
    """Remove a user or a team from the members of an MCP server

    Args:
        server_slug (str):
        member_type (Schema175):
        member_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteMcpServerMemberResponse200
    """

    return (
        await asyncio_detailed(
            server_slug=server_slug,
            member_type=member_type,
            member_id=member_id,
            client=client,
        )
    ).parsed
