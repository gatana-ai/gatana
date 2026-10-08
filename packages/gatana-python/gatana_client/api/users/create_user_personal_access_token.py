from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_personal_access_token_request import CreatePersonalAccessTokenRequest
from ...models.create_user_personal_access_token_response_200 import CreateUserPersonalAccessTokenResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    user_id: str,
    *,
    body: CreatePersonalAccessTokenRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/users/{user_id}/personal-access-tokens".format(
            user_id=quote(str(user_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CreateUserPersonalAccessTokenResponse200 | None:
    if response.status_code == 200:
        response_200 = CreateUserPersonalAccessTokenResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CreateUserPersonalAccessTokenResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreatePersonalAccessTokenRequest | Unset = UNSET,
) -> Response[CreateUserPersonalAccessTokenResponse200]:
    """Create a personal access token for the user and return its API key

    Args:
        user_id (str): ID of the user
        body (CreatePersonalAccessTokenRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateUserPersonalAccessTokenResponse200]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreatePersonalAccessTokenRequest | Unset = UNSET,
) -> CreateUserPersonalAccessTokenResponse200 | None:
    """Create a personal access token for the user and return its API key

    Args:
        user_id (str): ID of the user
        body (CreatePersonalAccessTokenRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateUserPersonalAccessTokenResponse200
    """

    return sync_detailed(
        user_id=user_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreatePersonalAccessTokenRequest | Unset = UNSET,
) -> Response[CreateUserPersonalAccessTokenResponse200]:
    """Create a personal access token for the user and return its API key

    Args:
        user_id (str): ID of the user
        body (CreatePersonalAccessTokenRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateUserPersonalAccessTokenResponse200]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreatePersonalAccessTokenRequest | Unset = UNSET,
) -> CreateUserPersonalAccessTokenResponse200 | None:
    """Create a personal access token for the user and return its API key

    Args:
        user_id (str): ID of the user
        body (CreatePersonalAccessTokenRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateUserPersonalAccessTokenResponse200
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            client=client,
            body=body,
        )
    ).parsed
