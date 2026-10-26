from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.artifact_theme_dto import ArtifactThemeDto
from ...models.create_artifact_theme_body import CreateArtifactThemeBody
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: CreateArtifactThemeBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/artifact-themes",
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ArtifactThemeDto | None:
    if response.status_code == 200:
        response_200 = ArtifactThemeDto.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ArtifactThemeDto]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateArtifactThemeBody | Unset = UNSET,
) -> Response[ArtifactThemeDto]:
    """Create an organization theme for artifacts: the Gatana theme with the organization's colors, fonts
    and logo

    Args:
        body (CreateArtifactThemeBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ArtifactThemeDto]
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
    body: CreateArtifactThemeBody | Unset = UNSET,
) -> ArtifactThemeDto | None:
    """Create an organization theme for artifacts: the Gatana theme with the organization's colors, fonts
    and logo

    Args:
        body (CreateArtifactThemeBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ArtifactThemeDto
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateArtifactThemeBody | Unset = UNSET,
) -> Response[ArtifactThemeDto]:
    """Create an organization theme for artifacts: the Gatana theme with the organization's colors, fonts
    and logo

    Args:
        body (CreateArtifactThemeBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ArtifactThemeDto]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: CreateArtifactThemeBody | Unset = UNSET,
) -> ArtifactThemeDto | None:
    """Create an organization theme for artifacts: the Gatana theme with the organization's colors, fonts
    and logo

    Args:
        body (CreateArtifactThemeBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ArtifactThemeDto
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
