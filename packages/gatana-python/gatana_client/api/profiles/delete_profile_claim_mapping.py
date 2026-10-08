from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_profile_claim_mapping_response_200 import DeleteProfileClaimMappingResponse200
from ...types import Response


def _get_kwargs(
    profile_id: str,
    mapping_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/profiles/{profile_id}/claim-mappings/{mapping_id}".format(
            profile_id=quote(str(profile_id), safe=""),
            mapping_id=quote(str(mapping_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeleteProfileClaimMappingResponse200 | None:
    if response.status_code == 200:
        response_200 = DeleteProfileClaimMappingResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DeleteProfileClaimMappingResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    profile_id: str,
    mapping_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeleteProfileClaimMappingResponse200]:
    """Remove an identity claim mapping from the profile

    Args:
        profile_id (str):
        mapping_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteProfileClaimMappingResponse200]
    """

    kwargs = _get_kwargs(
        profile_id=profile_id,
        mapping_id=mapping_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    profile_id: str,
    mapping_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> DeleteProfileClaimMappingResponse200 | None:
    """Remove an identity claim mapping from the profile

    Args:
        profile_id (str):
        mapping_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteProfileClaimMappingResponse200
    """

    return sync_detailed(
        profile_id=profile_id,
        mapping_id=mapping_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    profile_id: str,
    mapping_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeleteProfileClaimMappingResponse200]:
    """Remove an identity claim mapping from the profile

    Args:
        profile_id (str):
        mapping_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteProfileClaimMappingResponse200]
    """

    kwargs = _get_kwargs(
        profile_id=profile_id,
        mapping_id=mapping_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    profile_id: str,
    mapping_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> DeleteProfileClaimMappingResponse200 | None:
    """Remove an identity claim mapping from the profile

    Args:
        profile_id (str):
        mapping_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteProfileClaimMappingResponse200
    """

    return (
        await asyncio_detailed(
            profile_id=profile_id,
            mapping_id=mapping_id,
            client=client,
        )
    ).parsed
