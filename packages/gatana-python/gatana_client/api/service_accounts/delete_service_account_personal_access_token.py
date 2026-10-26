from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_service_account_personal_access_token_response_200 import (
    DeleteServiceAccountPersonalAccessTokenResponse200,
)
from ...types import Response


def _get_kwargs(
    user_id: str,
    pat_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/service-accounts/{user_id}/personal-access-tokens/{pat_id}".format(
            user_id=quote(str(user_id), safe=""),
            pat_id=quote(str(pat_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeleteServiceAccountPersonalAccessTokenResponse200 | None:
    if response.status_code == 200:
        response_200 = DeleteServiceAccountPersonalAccessTokenResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DeleteServiceAccountPersonalAccessTokenResponse200]:
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
) -> Response[DeleteServiceAccountPersonalAccessTokenResponse200]:
    """Delete a personal access token of a service account you may update, from a browser session or a
    token

    Args:
        user_id (str): ID of the user
        pat_id (str): ID of the personal access token

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteServiceAccountPersonalAccessTokenResponse200]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        pat_id=pat_id,
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
) -> DeleteServiceAccountPersonalAccessTokenResponse200 | None:
    """Delete a personal access token of a service account you may update, from a browser session or a
    token

    Args:
        user_id (str): ID of the user
        pat_id (str): ID of the personal access token

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteServiceAccountPersonalAccessTokenResponse200
    """

    return sync_detailed(
        user_id=user_id,
        pat_id=pat_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    user_id: str,
    pat_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeleteServiceAccountPersonalAccessTokenResponse200]:
    """Delete a personal access token of a service account you may update, from a browser session or a
    token

    Args:
        user_id (str): ID of the user
        pat_id (str): ID of the personal access token

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteServiceAccountPersonalAccessTokenResponse200]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        pat_id=pat_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    user_id: str,
    pat_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> DeleteServiceAccountPersonalAccessTokenResponse200 | None:
    """Delete a personal access token of a service account you may update, from a browser session or a
    token

    Args:
        user_id (str): ID of the user
        pat_id (str): ID of the personal access token

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteServiceAccountPersonalAccessTokenResponse200
    """

    return (
        await asyncio_detailed(
            user_id=user_id,
            pat_id=pat_id,
            client=client,
        )
    ).parsed
