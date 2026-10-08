from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.schema_175 import Schema175
from ...models.update_mcp_server_member_body import UpdateMcpServerMemberBody
from ...models.update_mcp_server_member_response_200 import UpdateMcpServerMemberResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    server_slug: str,
    member_type: Schema175,
    member_id: str,
    *,
    body: UpdateMcpServerMemberBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/mcp-servers/{server_slug}/members/{member_type}/{member_id}".format(
            server_slug=quote(str(server_slug), safe=""),
            member_type=quote(str(member_type), safe=""),
            member_id=quote(str(member_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> UpdateMcpServerMemberResponse200 | None:
    if response.status_code == 200:
        response_200 = UpdateMcpServerMemberResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[UpdateMcpServerMemberResponse200]:
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
    body: UpdateMcpServerMemberBody | Unset = UNSET,
) -> Response[UpdateMcpServerMemberResponse200]:
    """Add a user or a team as a member of an MCP server, or change the role of an existing member

    Args:
        server_slug (str):
        member_type (Schema175):
        member_id (str):
        body (UpdateMcpServerMemberBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateMcpServerMemberResponse200]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        member_type=member_type,
        member_id=member_id,
        body=body,
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
    body: UpdateMcpServerMemberBody | Unset = UNSET,
) -> UpdateMcpServerMemberResponse200 | None:
    """Add a user or a team as a member of an MCP server, or change the role of an existing member

    Args:
        server_slug (str):
        member_type (Schema175):
        member_id (str):
        body (UpdateMcpServerMemberBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateMcpServerMemberResponse200
    """

    return sync_detailed(
        server_slug=server_slug,
        member_type=member_type,
        member_id=member_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    server_slug: str,
    member_type: Schema175,
    member_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateMcpServerMemberBody | Unset = UNSET,
) -> Response[UpdateMcpServerMemberResponse200]:
    """Add a user or a team as a member of an MCP server, or change the role of an existing member

    Args:
        server_slug (str):
        member_type (Schema175):
        member_id (str):
        body (UpdateMcpServerMemberBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateMcpServerMemberResponse200]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        member_type=member_type,
        member_id=member_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    server_slug: str,
    member_type: Schema175,
    member_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateMcpServerMemberBody | Unset = UNSET,
) -> UpdateMcpServerMemberResponse200 | None:
    """Add a user or a team as a member of an MCP server, or change the role of an existing member

    Args:
        server_slug (str):
        member_type (Schema175):
        member_id (str):
        body (UpdateMcpServerMemberBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateMcpServerMemberResponse200
    """

    return (
        await asyncio_detailed(
            server_slug=server_slug,
            member_type=member_type,
            member_id=member_id,
            client=client,
            body=body,
        )
    ).parsed
