from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.schema_447 import Schema447
from ...models.update_user_profile_assignment_request import UpdateUserProfileAssignmentRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    user_id: str,
    profile_id: str,
    *,
    body: UpdateUserProfileAssignmentRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/users/{user_id}/profiles/{profile_id}".format(
            user_id=quote(str(user_id), safe=""),
            profile_id=quote(str(profile_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Schema447 | None:
    if response.status_code == 200:
        response_200 = Schema447.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Schema447]:
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
    body: UpdateUserProfileAssignmentRequest | Unset = UNSET,
) -> Response[Schema447]:
    """Change the lock status of a profile assignment; organization owners only

    Args:
        user_id (str): ID of the user
        profile_id (str): ID of the profile
        body (UpdateUserProfileAssignmentRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Schema447]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        profile_id=profile_id,
        body=body,
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
    body: UpdateUserProfileAssignmentRequest | Unset = UNSET,
) -> Schema447 | None:
    """Change the lock status of a profile assignment; organization owners only

    Args:
        user_id (str): ID of the user
        profile_id (str): ID of the profile
        body (UpdateUserProfileAssignmentRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Schema447
    """

    return sync_detailed(
        user_id=user_id,
        profile_id=profile_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    profile_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateUserProfileAssignmentRequest | Unset = UNSET,
) -> Response[Schema447]:
    """Change the lock status of a profile assignment; organization owners only

    Args:
        user_id (str): ID of the user
        profile_id (str): ID of the profile
        body (UpdateUserProfileAssignmentRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Schema447]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        profile_id=profile_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    profile_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateUserProfileAssignmentRequest | Unset = UNSET,
) -> Schema447 | None:
    """Change the lock status of a profile assignment; organization owners only

    Args:
        user_id (str): ID of the user
        profile_id (str): ID of the profile
        body (UpdateUserProfileAssignmentRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Schema447
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            profile_id=profile_id,
            client=client,
            body=body,
        )
    ).parsed
