from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.patch_secret_store_mapping_body import PatchSecretStoreMappingBody
from ...models.secret_mapping_response import SecretMappingResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    store_id: str,
    mapping_name: str,
    *,
    body: PatchSecretStoreMappingBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/secret-stores/{store_id}/mappings/{mapping_name}".format(
            store_id=quote(str(store_id), safe=""),
            mapping_name=quote(str(mapping_name), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SecretMappingResponse | None:
    if response.status_code == 200:
        response_200 = SecretMappingResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[SecretMappingResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    store_id: str,
    mapping_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: PatchSecretStoreMappingBody | Unset = UNSET,
) -> Response[SecretMappingResponse]:
    """Update a secret mapping

    Args:
        store_id (str):
        mapping_name (str):
        body (PatchSecretStoreMappingBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SecretMappingResponse]
    """

    kwargs = _get_kwargs(
        store_id=store_id,
        mapping_name=mapping_name,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    store_id: str,
    mapping_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: PatchSecretStoreMappingBody | Unset = UNSET,
) -> SecretMappingResponse | None:
    """Update a secret mapping

    Args:
        store_id (str):
        mapping_name (str):
        body (PatchSecretStoreMappingBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SecretMappingResponse
    """

    return sync_detailed(
        store_id=store_id,
        mapping_name=mapping_name,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    store_id: str,
    mapping_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: PatchSecretStoreMappingBody | Unset = UNSET,
) -> Response[SecretMappingResponse]:
    """Update a secret mapping

    Args:
        store_id (str):
        mapping_name (str):
        body (PatchSecretStoreMappingBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SecretMappingResponse]
    """

    kwargs = _get_kwargs(
        store_id=store_id,
        mapping_name=mapping_name,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    store_id: str,
    mapping_name: str,
    *,
    client: AuthenticatedClient | Client,
    body: PatchSecretStoreMappingBody | Unset = UNSET,
) -> SecretMappingResponse | None:
    """Update a secret mapping

    Args:
        store_id (str):
        mapping_name (str):
        body (PatchSecretStoreMappingBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SecretMappingResponse
    """

    return (
        await asyncio_detailed(
            store_id=store_id,
            mapping_name=mapping_name,
            client=client,
            body=body,
        )
    ).parsed
