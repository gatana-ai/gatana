from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.artifact_dto import ArtifactDto
from ...models.patch_artifact_body import PatchArtifactBody
from ...types import UNSET, Response, Unset


def _get_kwargs(
    artifact_id: str,
    *,
    body: PatchArtifactBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/artifacts/{artifact_id}".format(
            artifact_id=quote(str(artifact_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ArtifactDto | None:
    if response.status_code == 200:
        response_200 = ArtifactDto.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ArtifactDto]:
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
    body: PatchArtifactBody | Unset = UNSET,
) -> Response[ArtifactDto]:
    """Change the title, visibility or theme of an artifact without touching its content

    Args:
        artifact_id (str):
        body (PatchArtifactBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ArtifactDto]
    """

    kwargs = _get_kwargs(
        artifact_id=artifact_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    artifact_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PatchArtifactBody | Unset = UNSET,
) -> ArtifactDto | None:
    """Change the title, visibility or theme of an artifact without touching its content

    Args:
        artifact_id (str):
        body (PatchArtifactBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ArtifactDto
    """

    return sync_detailed(
        artifact_id=artifact_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    artifact_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PatchArtifactBody | Unset = UNSET,
) -> Response[ArtifactDto]:
    """Change the title, visibility or theme of an artifact without touching its content

    Args:
        artifact_id (str):
        body (PatchArtifactBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ArtifactDto]
    """

    kwargs = _get_kwargs(
        artifact_id=artifact_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    artifact_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: PatchArtifactBody | Unset = UNSET,
) -> ArtifactDto | None:
    """Change the title, visibility or theme of an artifact without touching its content

    Args:
        artifact_id (str):
        body (PatchArtifactBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ArtifactDto
    """

    return (
        await asyncio_detailed(
            artifact_id=artifact_id,
            client=client,
            body=body,
        )
    ).parsed
