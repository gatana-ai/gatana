from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.request_email_change_verification_request import RequestEmailChangeVerificationRequest
from ...models.request_own_email_verification_response_200 import RequestOwnEmailVerificationResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: RequestEmailChangeVerificationRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/users/me/request-email-verification",
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> RequestOwnEmailVerificationResponse200 | None:
    if response.status_code == 200:
        response_200 = RequestOwnEmailVerificationResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[RequestOwnEmailVerificationResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: RequestEmailChangeVerificationRequest | Unset = UNSET,
) -> Response[RequestOwnEmailVerificationResponse200]:
    """Send a verification code to a new email address before changing it

    Args:
        body (RequestEmailChangeVerificationRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestOwnEmailVerificationResponse200]
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
    body: RequestEmailChangeVerificationRequest | Unset = UNSET,
) -> RequestOwnEmailVerificationResponse200 | None:
    """Send a verification code to a new email address before changing it

    Args:
        body (RequestEmailChangeVerificationRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestOwnEmailVerificationResponse200
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: RequestEmailChangeVerificationRequest | Unset = UNSET,
) -> Response[RequestOwnEmailVerificationResponse200]:
    """Send a verification code to a new email address before changing it

    Args:
        body (RequestEmailChangeVerificationRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RequestOwnEmailVerificationResponse200]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: RequestEmailChangeVerificationRequest | Unset = UNSET,
) -> RequestOwnEmailVerificationResponse200 | None:
    """Send a verification code to a new email address before changing it

    Args:
        body (RequestEmailChangeVerificationRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RequestOwnEmailVerificationResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
