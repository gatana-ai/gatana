from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_profile_maintainer_response_200 import DeleteProfileMaintainerResponse200
from ...types import Response


def _get_kwargs(
    profile_id: str,
    user_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/profiles/{profile_id}/maintainers/{user_id}".format(
            profile_id=quote(str(profile_id), safe=""),
            user_id=quote(str(user_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeleteProfileMaintainerResponse200 | None:
    if response.status_code == 200:
        response_200 = DeleteProfileMaintainerResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DeleteProfileMaintainerResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    profile_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeleteProfileMaintainerResponse200]:
    """Remove a maintainer from the profile. The last remaining maintainer cannot be removed

    Args:
        profile_id (str):
        user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteProfileMaintainerResponse200]
    """

    kwargs = _get_kwargs(
        profile_id=profile_id,
        user_id=user_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    profile_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> DeleteProfileMaintainerResponse200 | None:
    """Remove a maintainer from the profile. The last remaining maintainer cannot be removed

    Args:
        profile_id (str):
        user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteProfileMaintainerResponse200
    """

    return sync_detailed(
        profile_id=profile_id,
        user_id=user_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    profile_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeleteProfileMaintainerResponse200]:
    """Remove a maintainer from the profile. The last remaining maintainer cannot be removed

    Args:
        profile_id (str):
        user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteProfileMaintainerResponse200]
    """

    kwargs = _get_kwargs(
        profile_id=profile_id,
        user_id=user_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    profile_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> DeleteProfileMaintainerResponse200 | None:
    """Remove a maintainer from the profile. The last remaining maintainer cannot be removed

    Args:
        profile_id (str):
        user_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteProfileMaintainerResponse200
    """

    return (
        await asyncio_detailed(
            profile_id=profile_id,
            user_id=user_id,
            client=client,
        )
    ).parsed
