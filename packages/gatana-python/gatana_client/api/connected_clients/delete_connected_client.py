from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_connected_client_response_200 import DeleteConnectedClientResponse200
from ...types import Response


def _get_kwargs(
    client_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/connected-clients/{client_id}".format(
            client_id=quote(str(client_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeleteConnectedClientResponse200 | None:
    if response.status_code == 200:
        response_200 = DeleteConnectedClientResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DeleteConnectedClientResponse200]:
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
) -> Response[DeleteConnectedClientResponse200]:
    """Disconnect a client, revoking its grants and every token issued under them

    Args:
        client_id (str): OAuth client ID of the connection

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteConnectedClientResponse200]
    """

    kwargs = _get_kwargs(
        client_id=client_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    client_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> DeleteConnectedClientResponse200 | None:
    """Disconnect a client, revoking its grants and every token issued under them

    Args:
        client_id (str): OAuth client ID of the connection

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteConnectedClientResponse200
    """

    return sync_detailed(
        client_id=client_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    client_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeleteConnectedClientResponse200]:
    """Disconnect a client, revoking its grants and every token issued under them

    Args:
        client_id (str): OAuth client ID of the connection

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteConnectedClientResponse200]
    """

    kwargs = _get_kwargs(
        client_id=client_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    client_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> DeleteConnectedClientResponse200 | None:
    """Disconnect a client, revoking its grants and every token issued under them

    Args:
        client_id (str): OAuth client ID of the connection

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteConnectedClientResponse200
    """

    return (
        await asyncio_detailed(
            client_id=client_id,
            client=client,
        )
    ).parsed
