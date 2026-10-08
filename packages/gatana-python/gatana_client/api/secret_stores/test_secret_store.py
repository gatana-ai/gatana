from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.test_secret_request import TestSecretRequest
from ...models.test_secret_response import TestSecretResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    store_id: str,
    *,
    body: TestSecretRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/secret-stores/{store_id}/test".format(
            store_id=quote(str(store_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> TestSecretResponse | None:
    if response.status_code == 200:
        response_200 = TestSecretResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[TestSecretResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    store_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: TestSecretRequest | Unset = UNSET,
) -> Response[TestSecretResponse]:
    """Test fetching a secret from the store using a secret identifier (e.g., AWS ARN, GCP secret path)

    Args:
        store_id (str):
        body (TestSecretRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TestSecretResponse]
    """

    kwargs = _get_kwargs(
        store_id=store_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    store_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: TestSecretRequest | Unset = UNSET,
) -> TestSecretResponse | None:
    """Test fetching a secret from the store using a secret identifier (e.g., AWS ARN, GCP secret path)

    Args:
        store_id (str):
        body (TestSecretRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TestSecretResponse
    """

    return sync_detailed(
        store_id=store_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    store_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: TestSecretRequest | Unset = UNSET,
) -> Response[TestSecretResponse]:
    """Test fetching a secret from the store using a secret identifier (e.g., AWS ARN, GCP secret path)

    Args:
        store_id (str):
        body (TestSecretRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TestSecretResponse]
    """

    kwargs = _get_kwargs(
        store_id=store_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    store_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: TestSecretRequest | Unset = UNSET,
) -> TestSecretResponse | None:
    """Test fetching a secret from the store using a secret identifier (e.g., AWS ARN, GCP secret path)

    Args:
        store_id (str):
        body (TestSecretRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TestSecretResponse
    """

    return (
        await asyncio_detailed(
            store_id=store_id,
            client=client,
            body=body,
        )
    ).parsed
