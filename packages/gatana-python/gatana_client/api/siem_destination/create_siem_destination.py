from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_siem_destination_input import CreateSiemDestinationInput
from ...models.create_siem_destination_response import CreateSiemDestinationResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: CreateSiemDestinationInput | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/siem-destination",
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CreateSiemDestinationResponse | None:
    if response.status_code == 200:
        response_200 = CreateSiemDestinationResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CreateSiemDestinationResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateSiemDestinationInput | Unset = UNSET,
) -> Response[CreateSiemDestinationResponse]:
    """Configure SIEM streaming. The signing secret is returned once and cannot be retrieved later

    Args:
        body (CreateSiemDestinationInput | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateSiemDestinationResponse]
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
    body: CreateSiemDestinationInput | Unset = UNSET,
) -> CreateSiemDestinationResponse | None:
    """Configure SIEM streaming. The signing secret is returned once and cannot be retrieved later

    Args:
        body (CreateSiemDestinationInput | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateSiemDestinationResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateSiemDestinationInput | Unset = UNSET,
) -> Response[CreateSiemDestinationResponse]:
    """Configure SIEM streaming. The signing secret is returned once and cannot be retrieved later

    Args:
        body (CreateSiemDestinationInput | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateSiemDestinationResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: CreateSiemDestinationInput | Unset = UNSET,
) -> CreateSiemDestinationResponse | None:
    """Configure SIEM streaming. The signing secret is returned once and cannot be retrieved later

    Args:
        body (CreateSiemDestinationInput | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateSiemDestinationResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
