from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_mcp_servers_access_preview_response_200 import GetMcpServersAccessPreviewResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    user_id: str | Unset = UNSET,
    team_id: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["userId"] = user_id

    params["teamId"] = team_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/mcp-servers/access-preview",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetMcpServersAccessPreviewResponse200 | None:
    if response.status_code == 200:
        response_200 = GetMcpServersAccessPreviewResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetMcpServersAccessPreviewResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    user_id: str | Unset = UNSET,
    team_id: str | Unset = UNSET,
) -> Response[GetMcpServersAccessPreviewResponse200]:
    """Preview which servers a specific user or team can access

    Args:
        user_id (str | Unset):
        team_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetMcpServersAccessPreviewResponse200]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        team_id=team_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    user_id: str | Unset = UNSET,
    team_id: str | Unset = UNSET,
) -> GetMcpServersAccessPreviewResponse200 | None:
    """Preview which servers a specific user or team can access

    Args:
        user_id (str | Unset):
        team_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetMcpServersAccessPreviewResponse200
    """

    return sync_detailed(
        client=client,
        user_id=user_id,
        team_id=team_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    user_id: str | Unset = UNSET,
    team_id: str | Unset = UNSET,
) -> Response[GetMcpServersAccessPreviewResponse200]:
    """Preview which servers a specific user or team can access

    Args:
        user_id (str | Unset):
        team_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetMcpServersAccessPreviewResponse200]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        team_id=team_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    user_id: str | Unset = UNSET,
    team_id: str | Unset = UNSET,
) -> GetMcpServersAccessPreviewResponse200 | None:
    """Preview which servers a specific user or team can access

    Args:
        user_id (str | Unset):
        team_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetMcpServersAccessPreviewResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            user_id=user_id,
            team_id=team_id,
        )
    ).parsed
