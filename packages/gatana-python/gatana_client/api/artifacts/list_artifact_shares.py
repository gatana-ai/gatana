from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.artifact_shares_response import ArtifactSharesResponse
from ...types import Response


def _get_kwargs(
    artifact_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/artifacts/{artifact_id}/shares".format(
            artifact_id=quote(str(artifact_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ArtifactSharesResponse | None:
    if response.status_code == 200:
        response_200 = ArtifactSharesResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ArtifactSharesResponse]:
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
) -> Response[ArtifactSharesResponse]:
    """List the users and teams an artifact is shared with

    Args:
        artifact_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ArtifactSharesResponse]
    """

    kwargs = _get_kwargs(
        artifact_id=artifact_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    artifact_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> ArtifactSharesResponse | None:
    """List the users and teams an artifact is shared with

    Args:
        artifact_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ArtifactSharesResponse
    """

    return sync_detailed(
        artifact_id=artifact_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    artifact_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ArtifactSharesResponse]:
    """List the users and teams an artifact is shared with

    Args:
        artifact_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ArtifactSharesResponse]
    """

    kwargs = _get_kwargs(
        artifact_id=artifact_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    artifact_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> ArtifactSharesResponse | None:
    """List the users and teams an artifact is shared with

    Args:
        artifact_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ArtifactSharesResponse
    """

    return (
        await asyncio_detailed(
            artifact_id=artifact_id,
            client=client,
        )
    ).parsed
