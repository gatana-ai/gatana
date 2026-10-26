from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.artifact_theme_dto import ArtifactThemeDto
from ...types import Response


def _get_kwargs(
    theme_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/artifact-themes/{theme_id}".format(
            theme_id=quote(str(theme_id), safe=""),
        ),
    }

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
    theme_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ArtifactThemeDto]:
    """Get an organization theme for artifacts with its logo and extra CSS

    Args:
        theme_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ArtifactThemeDto]
    """

    kwargs = _get_kwargs(
        theme_id=theme_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    theme_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> ArtifactThemeDto | None:
    """Get an organization theme for artifacts with its logo and extra CSS

    Args:
        theme_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ArtifactThemeDto
    """

    return sync_detailed(
        theme_id=theme_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    theme_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ArtifactThemeDto]:
    """Get an organization theme for artifacts with its logo and extra CSS

    Args:
        theme_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ArtifactThemeDto]
    """

    kwargs = _get_kwargs(
        theme_id=theme_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    theme_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> ArtifactThemeDto | None:
    """Get an organization theme for artifacts with its logo and extra CSS

    Args:
        theme_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ArtifactThemeDto
    """

    return (
        await asyncio_detailed(
            theme_id=theme_id,
            client=client,
        )
    ).parsed
