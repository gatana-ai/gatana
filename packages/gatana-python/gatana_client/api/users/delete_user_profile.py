from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_user_profile_response_200 import DeleteUserProfileResponse200
from ...types import Response


def _get_kwargs(
    user_id: str,
    profile_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/users/{user_id}/profiles/{profile_id}".format(
            user_id=quote(str(user_id), safe=""),
            profile_id=quote(str(profile_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeleteUserProfileResponse200 | None:
    if response.status_code == 200:
        response_200 = DeleteUserProfileResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DeleteUserProfileResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: str,
    profile_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeleteUserProfileResponse200]:
    """Remove a profile assignment; only organization owners can remove locked assignments

    Args:
        user_id (str): ID of the user
        profile_id (str): ID of the profile

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteUserProfileResponse200]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        profile_id=profile_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: str,
    profile_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> DeleteUserProfileResponse200 | None:
    """Remove a profile assignment; only organization owners can remove locked assignments

    Args:
        user_id (str): ID of the user
        profile_id (str): ID of the profile

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteUserProfileResponse200
    """

    return sync_detailed(
        user_id=user_id,
        profile_id=profile_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    profile_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeleteUserProfileResponse200]:
    """Remove a profile assignment; only organization owners can remove locked assignments

    Args:
        user_id (str): ID of the user
        profile_id (str): ID of the profile

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteUserProfileResponse200]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        profile_id=profile_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    profile_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> DeleteUserProfileResponse200 | None:
    """Remove a profile assignment; only organization owners can remove locked assignments

    Args:
        user_id (str): ID of the user
        profile_id (str): ID of the profile

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteUserProfileResponse200
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            profile_id=profile_id,
            client=client,
        )
    ).parsed
