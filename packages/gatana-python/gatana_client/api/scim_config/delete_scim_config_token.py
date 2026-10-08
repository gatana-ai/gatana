from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_scim_config_token_response_200 import DeleteScimConfigTokenResponse200
from ...types import Response


def _get_kwargs(
    token_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/scim-config/tokens/{token_id}".format(
            token_id=quote(str(token_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeleteScimConfigTokenResponse200 | None:
    if response.status_code == 200:
        response_200 = DeleteScimConfigTokenResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DeleteScimConfigTokenResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    token_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeleteScimConfigTokenResponse200]:
    """Delete a SCIM token and revoke access for every client that uses it. Requires permission to manage
    the organization

    Args:
        token_id (str): ID of the SCIM token

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteScimConfigTokenResponse200]
    """

    kwargs = _get_kwargs(
        token_id=token_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    token_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> DeleteScimConfigTokenResponse200 | None:
    """Delete a SCIM token and revoke access for every client that uses it. Requires permission to manage
    the organization

    Args:
        token_id (str): ID of the SCIM token

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteScimConfigTokenResponse200
    """

    return sync_detailed(
        token_id=token_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    token_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeleteScimConfigTokenResponse200]:
    """Delete a SCIM token and revoke access for every client that uses it. Requires permission to manage
    the organization

    Args:
        token_id (str): ID of the SCIM token

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteScimConfigTokenResponse200]
    """

    kwargs = _get_kwargs(
        token_id=token_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    token_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> DeleteScimConfigTokenResponse200 | None:
    """Delete a SCIM token and revoke access for every client that uses it. Requires permission to manage
    the organization

    Args:
        token_id (str): ID of the SCIM token

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteScimConfigTokenResponse200
    """

    return (
        await asyncio_detailed(
            token_id=token_id,
            client=client,
        )
    ).parsed
