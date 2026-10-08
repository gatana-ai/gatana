from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.update_profile_body import UpdateProfileBody
from ...models.update_profile_response_200 import UpdateProfileResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    profile_id: str,
    *,
    body: UpdateProfileBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/profiles/{profile_id}".format(
            profile_id=quote(str(profile_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> UpdateProfileResponse200 | None:
    if response.status_code == 200:
        response_200 = UpdateProfileResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[UpdateProfileResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    profile_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateProfileBody | Unset = UNSET,
) -> Response[UpdateProfileResponse200]:
    """Update a profile. Closing a profile that was open to all users also removes it from all personal
    access tokens

    Args:
        profile_id (str):
        body (UpdateProfileBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateProfileResponse200]
    """

    kwargs = _get_kwargs(
        profile_id=profile_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    profile_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateProfileBody | Unset = UNSET,
) -> UpdateProfileResponse200 | None:
    """Update a profile. Closing a profile that was open to all users also removes it from all personal
    access tokens

    Args:
        profile_id (str):
        body (UpdateProfileBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateProfileResponse200
    """

    return sync_detailed(
        profile_id=profile_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    profile_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateProfileBody | Unset = UNSET,
) -> Response[UpdateProfileResponse200]:
    """Update a profile. Closing a profile that was open to all users also removes it from all personal
    access tokens

    Args:
        profile_id (str):
        body (UpdateProfileBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateProfileResponse200]
    """

    kwargs = _get_kwargs(
        profile_id=profile_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    profile_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateProfileBody | Unset = UNSET,
) -> UpdateProfileResponse200 | None:
    """Update a profile. Closing a profile that was open to all users also removes it from all personal
    access tokens

    Args:
        profile_id (str):
        body (UpdateProfileBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateProfileResponse200
    """

    return (
        await asyncio_detailed(
            profile_id=profile_id,
            client=client,
            body=body,
        )
    ).parsed
