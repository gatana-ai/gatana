from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_scim_token_secret_response import GetScimTokenSecretResponse
from ...types import Response


def _get_kwargs(
    token_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/scim-config/tokens/{token_id}/secret".format(
            token_id=quote(str(token_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetScimTokenSecretResponse | None:
    if response.status_code == 200:
        response_200 = GetScimTokenSecretResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetScimTokenSecretResponse]:
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
) -> Response[GetScimTokenSecretResponse]:
    """Reveal the raw secret of a SCIM token. Requires permission to manage the organization

    Args:
        token_id (str): ID of the SCIM token

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetScimTokenSecretResponse]
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
) -> GetScimTokenSecretResponse | None:
    """Reveal the raw secret of a SCIM token. Requires permission to manage the organization

    Args:
        token_id (str): ID of the SCIM token

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetScimTokenSecretResponse
    """

    return sync_detailed(
        token_id=token_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    token_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[GetScimTokenSecretResponse]:
    """Reveal the raw secret of a SCIM token. Requires permission to manage the organization

    Args:
        token_id (str): ID of the SCIM token

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetScimTokenSecretResponse]
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
) -> GetScimTokenSecretResponse | None:
    """Reveal the raw secret of a SCIM token. Requires permission to manage the organization

    Args:
        token_id (str): ID of the SCIM token

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetScimTokenSecretResponse
    """

    return (
        await asyncio_detailed(
            token_id=token_id,
            client=client,
        )
    ).parsed
