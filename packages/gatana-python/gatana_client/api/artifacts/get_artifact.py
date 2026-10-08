from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_artifact_response import GetArtifactResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    artifact_id: str,
    *,
    version: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["version"] = version

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/artifacts/{artifact_id}".format(
            artifact_id=quote(str(artifact_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetArtifactResponse | None:
    if response.status_code == 200:
        response_200 = GetArtifactResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetArtifactResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    artifact_id: str,
    *,
    client: AuthenticatedClient | Client,
    version: str | Unset = UNSET,
) -> Response[GetArtifactResponse]:
    """Get an artifact with its version history and a frame URL for the requested or current version,
    honoring its visibility for anonymous callers

    Args:
        artifact_id (str):
        version (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetArtifactResponse]
    """

    kwargs = _get_kwargs(
        artifact_id=artifact_id,
        version=version,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    artifact_id: str,
    *,
    client: AuthenticatedClient | Client,
    version: str | Unset = UNSET,
) -> GetArtifactResponse | None:
    """Get an artifact with its version history and a frame URL for the requested or current version,
    honoring its visibility for anonymous callers

    Args:
        artifact_id (str):
        version (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetArtifactResponse
    """

    return sync_detailed(
        artifact_id=artifact_id,
        client=client,
        version=version,
    ).parsed


async def asyncio_detailed(
    artifact_id: str,
    *,
    client: AuthenticatedClient | Client,
    version: str | Unset = UNSET,
) -> Response[GetArtifactResponse]:
    """Get an artifact with its version history and a frame URL for the requested or current version,
    honoring its visibility for anonymous callers

    Args:
        artifact_id (str):
        version (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetArtifactResponse]
    """

    kwargs = _get_kwargs(
        artifact_id=artifact_id,
        version=version,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    artifact_id: str,
    *,
    client: AuthenticatedClient | Client,
    version: str | Unset = UNSET,
) -> GetArtifactResponse | None:
    """Get an artifact with its version history and a frame URL for the requested or current version,
    honoring its visibility for anonymous callers

    Args:
        artifact_id (str):
        version (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetArtifactResponse
    """

    return (
        await asyncio_detailed(
            artifact_id=artifact_id,
            client=client,
            version=version,
        )
    ).parsed
