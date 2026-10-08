from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.list_profiles_response_200 import ListProfilesResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    server_slug: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["serverSlug"] = server_slug

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/profiles",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListProfilesResponse200 | None:
    if response.status_code == 200:
        response_200 = ListProfilesResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListProfilesResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    server_slug: str | Unset = UNSET,
) -> Response[ListProfilesResponse200]:
    """List the profiles the caller can read, optionally filtered to one MCP server

    Args:
        server_slug (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListProfilesResponse200]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    server_slug: str | Unset = UNSET,
) -> ListProfilesResponse200 | None:
    """List the profiles the caller can read, optionally filtered to one MCP server

    Args:
        server_slug (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListProfilesResponse200
    """

    return sync_detailed(
        client=client,
        server_slug=server_slug,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    server_slug: str | Unset = UNSET,
) -> Response[ListProfilesResponse200]:
    """List the profiles the caller can read, optionally filtered to one MCP server

    Args:
        server_slug (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListProfilesResponse200]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    server_slug: str | Unset = UNSET,
) -> ListProfilesResponse200 | None:
    """List the profiles the caller can read, optionally filtered to one MCP server

    Args:
        server_slug (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListProfilesResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            server_slug=server_slug,
        )
    ).parsed
