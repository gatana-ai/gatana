from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.list_users_response_200 import ListUsersResponse200
from ...models.schema_12 import Schema12
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    type_: Schema12 | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_type_: str | Unset = UNSET
    if not isinstance(type_, Unset):
        json_type_ = type_.value

    params["type"] = json_type_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/users",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ListUsersResponse200 | None:
    if response.status_code == 200:
        response_200 = ListUsersResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListUsersResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    type_: Schema12 | Unset = UNSET,
) -> Response[ListUsersResponse200]:
    """List the users and service accounts the caller can read, optionally filtered by type

    Args:
        type_ (Schema12 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListUsersResponse200]
    """

    kwargs = _get_kwargs(
        type_=type_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    type_: Schema12 | Unset = UNSET,
) -> ListUsersResponse200 | None:
    """List the users and service accounts the caller can read, optionally filtered by type

    Args:
        type_ (Schema12 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListUsersResponse200
    """

    return sync_detailed(
        client=client,
        type_=type_,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    type_: Schema12 | Unset = UNSET,
) -> Response[ListUsersResponse200]:
    """List the users and service accounts the caller can read, optionally filtered by type

    Args:
        type_ (Schema12 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListUsersResponse200]
    """

    kwargs = _get_kwargs(
        type_=type_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    type_: Schema12 | Unset = UNSET,
) -> ListUsersResponse200 | None:
    """List the users and service accounts the caller can read, optionally filtered by type

    Args:
        type_ (Schema12 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListUsersResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            type_=type_,
        )
    ).parsed
