from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_mcp_server_daily_usage_response_200 import GetMcpServerDailyUsageResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    server_slug: str,
    *,
    days: str | Unset = UNSET,
    time_zone: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["days"] = days

    params["timeZone"] = time_zone

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/mcp-servers/{server_slug}/daily-usage".format(
            server_slug=quote(str(server_slug), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetMcpServerDailyUsageResponse200 | None:
    if response.status_code == 200:
        response_200 = GetMcpServerDailyUsageResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetMcpServerDailyUsageResponse200]:
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
    days: str | Unset = UNSET,
    time_zone: str | Unset = UNSET,
) -> Response[GetMcpServerDailyUsageResponse200]:
    """Count the tool calls made to an MCP server on each day of a recent window, across all users

    Args:
        server_slug (str):
        days (str | Unset):
        time_zone (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetMcpServerDailyUsageResponse200]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        days=days,
        time_zone=time_zone,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    days: str | Unset = UNSET,
    time_zone: str | Unset = UNSET,
) -> GetMcpServerDailyUsageResponse200 | None:
    """Count the tool calls made to an MCP server on each day of a recent window, across all users

    Args:
        server_slug (str):
        days (str | Unset):
        time_zone (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetMcpServerDailyUsageResponse200
    """

    return sync_detailed(
        server_slug=server_slug,
        client=client,
        days=days,
        time_zone=time_zone,
    ).parsed


async def asyncio_detailed(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    days: str | Unset = UNSET,
    time_zone: str | Unset = UNSET,
) -> Response[GetMcpServerDailyUsageResponse200]:
    """Count the tool calls made to an MCP server on each day of a recent window, across all users

    Args:
        server_slug (str):
        days (str | Unset):
        time_zone (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetMcpServerDailyUsageResponse200]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        days=days,
        time_zone=time_zone,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    days: str | Unset = UNSET,
    time_zone: str | Unset = UNSET,
) -> GetMcpServerDailyUsageResponse200 | None:
    """Count the tool calls made to an MCP server on each day of a recent window, across all users

    Args:
        server_slug (str):
        days (str | Unset):
        time_zone (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetMcpServerDailyUsageResponse200
    """

    return (
        await asyncio_detailed(
            server_slug=server_slug,
            client=client,
            days=days,
            time_zone=time_zone,
        )
    ).parsed
