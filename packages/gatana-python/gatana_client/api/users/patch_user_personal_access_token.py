from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.patch_user_personal_access_token_response_200 import PatchUserPersonalAccessTokenResponse200
from ...models.update_personal_access_token_request import UpdatePersonalAccessTokenRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    user_id: str,
    pat_id: str,
    *,
    body: UpdatePersonalAccessTokenRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/users/{user_id}/personal-access-tokens/{pat_id}".format(
            user_id=quote(str(user_id), safe=""),
            pat_id=quote(str(pat_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PatchUserPersonalAccessTokenResponse200 | None:
    if response.status_code == 200:
        response_200 = PatchUserPersonalAccessTokenResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PatchUserPersonalAccessTokenResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    user_id: str,
    pat_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdatePersonalAccessTokenRequest | Unset = UNSET,
) -> Response[PatchUserPersonalAccessTokenResponse200]:
    """Update the name or the assigned profiles of a personal access token

    Args:
        user_id (str): ID of the user
        pat_id (str): ID of the personal access token
        body (UpdatePersonalAccessTokenRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PatchUserPersonalAccessTokenResponse200]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        pat_id=pat_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    user_id: str,
    pat_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdatePersonalAccessTokenRequest | Unset = UNSET,
) -> PatchUserPersonalAccessTokenResponse200 | None:
    """Update the name or the assigned profiles of a personal access token

    Args:
        user_id (str): ID of the user
        pat_id (str): ID of the personal access token
        body (UpdatePersonalAccessTokenRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PatchUserPersonalAccessTokenResponse200
    """

    return sync_detailed(
        user_id=user_id,
        pat_id=pat_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    pat_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdatePersonalAccessTokenRequest | Unset = UNSET,
) -> Response[PatchUserPersonalAccessTokenResponse200]:
    """Update the name or the assigned profiles of a personal access token

    Args:
        user_id (str): ID of the user
        pat_id (str): ID of the personal access token
        body (UpdatePersonalAccessTokenRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PatchUserPersonalAccessTokenResponse200]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        pat_id=pat_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    pat_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdatePersonalAccessTokenRequest | Unset = UNSET,
) -> PatchUserPersonalAccessTokenResponse200 | None:
    """Update the name or the assigned profiles of a personal access token

    Args:
        user_id (str): ID of the user
        pat_id (str): ID of the personal access token
        body (UpdatePersonalAccessTokenRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PatchUserPersonalAccessTokenResponse200
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            pat_id=pat_id,
            client=client,
            body=body,
        )
    ).parsed
