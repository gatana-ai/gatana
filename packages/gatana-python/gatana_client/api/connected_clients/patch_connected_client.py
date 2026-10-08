from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.update_connected_client_request import UpdateConnectedClientRequest
from ...models.update_connected_client_response import UpdateConnectedClientResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    client_id: str,
    *,
    body: UpdateConnectedClientRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/connected-clients/{client_id}".format(
            client_id=quote(str(client_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> UpdateConnectedClientResponse | None:
    if response.status_code == 200:
        response_200 = UpdateConnectedClientResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[UpdateConnectedClientResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    client_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateConnectedClientRequest | Unset = UNSET,
) -> Response[UpdateConnectedClientResponse]:
    """Update the name or the attached profiles of a connected client

    Args:
        client_id (str): OAuth client ID of the connection
        body (UpdateConnectedClientRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateConnectedClientResponse]
    """

    kwargs = _get_kwargs(
        client_id=client_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    client_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateConnectedClientRequest | Unset = UNSET,
) -> UpdateConnectedClientResponse | None:
    """Update the name or the attached profiles of a connected client

    Args:
        client_id (str): OAuth client ID of the connection
        body (UpdateConnectedClientRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateConnectedClientResponse
    """

    return sync_detailed(
        client_id=client_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    client_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateConnectedClientRequest | Unset = UNSET,
) -> Response[UpdateConnectedClientResponse]:
    """Update the name or the attached profiles of a connected client

    Args:
        client_id (str): OAuth client ID of the connection
        body (UpdateConnectedClientRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateConnectedClientResponse]
    """

    kwargs = _get_kwargs(
        client_id=client_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    client_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateConnectedClientRequest | Unset = UNSET,
) -> UpdateConnectedClientResponse | None:
    """Update the name or the attached profiles of a connected client

    Args:
        client_id (str): OAuth client ID of the connection
        body (UpdateConnectedClientRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateConnectedClientResponse
    """

    return (
        await asyncio_detailed(
            client_id=client_id,
            client=client,
            body=body,
        )
    ).parsed
