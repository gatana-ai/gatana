from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_artifact_response_200 import DeleteArtifactResponse200
from ...types import Response


def _get_kwargs(
    artifact_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/artifacts/{artifact_id}".format(
            artifact_id=quote(str(artifact_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeleteArtifactResponse200 | None:
    if response.status_code == 200:
        response_200 = DeleteArtifactResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DeleteArtifactResponse200]:
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
) -> Response[DeleteArtifactResponse200]:
    """Delete an artifact with all of its versions and stored content

    Args:
        artifact_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteArtifactResponse200]
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
) -> DeleteArtifactResponse200 | None:
    """Delete an artifact with all of its versions and stored content

    Args:
        artifact_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteArtifactResponse200
    """

    return sync_detailed(
        artifact_id=artifact_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    artifact_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeleteArtifactResponse200]:
    """Delete an artifact with all of its versions and stored content

    Args:
        artifact_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteArtifactResponse200]
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
) -> DeleteArtifactResponse200 | None:
    """Delete an artifact with all of its versions and stored content

    Args:
        artifact_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteArtifactResponse200
    """

    return (
        await asyncio_detailed(
            artifact_id=artifact_id,
            client=client,
        )
    ).parsed
