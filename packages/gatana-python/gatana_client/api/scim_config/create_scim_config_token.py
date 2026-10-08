from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_scim_token_request import CreateScimTokenRequest
from ...models.create_scim_token_response import CreateScimTokenResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: CreateScimTokenRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/scim-config/tokens",
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CreateScimTokenResponse | None:
    if response.status_code == 200:
        response_200 = CreateScimTokenResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CreateScimTokenResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateScimTokenRequest | Unset = UNSET,
) -> Response[CreateScimTokenResponse]:
    """Create a SCIM token for identity provider provisioning. The raw token is returned in the response.
    Requires permission to manage the organization

    Args:
        body (CreateScimTokenRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateScimTokenResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: CreateScimTokenRequest | Unset = UNSET,
) -> CreateScimTokenResponse | None:
    """Create a SCIM token for identity provider provisioning. The raw token is returned in the response.
    Requires permission to manage the organization

    Args:
        body (CreateScimTokenRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateScimTokenResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateScimTokenRequest | Unset = UNSET,
) -> Response[CreateScimTokenResponse]:
    """Create a SCIM token for identity provider provisioning. The raw token is returned in the response.
    Requires permission to manage the organization

    Args:
        body (CreateScimTokenRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateScimTokenResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: CreateScimTokenRequest | Unset = UNSET,
) -> CreateScimTokenResponse | None:
    """Create a SCIM token for identity provider provisioning. The raw token is returned in the response.
    Requires permission to manage the organization

    Args:
        body (CreateScimTokenRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateScimTokenResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
