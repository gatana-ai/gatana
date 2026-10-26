from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_artifact_theme_response_200 import DeleteArtifactThemeResponse200
from ...types import Response


def _get_kwargs(
    theme_id: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/artifact-themes/{theme_id}".format(
            theme_id=quote(str(theme_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeleteArtifactThemeResponse200 | None:
    if response.status_code == 200:
        response_200 = DeleteArtifactThemeResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DeleteArtifactThemeResponse200]:
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
) -> Response[DeleteArtifactThemeResponse200]:
    """Delete an organization theme; the artifacts on it, and the organization default when it names it, go
    back to Gatana

    Args:
        theme_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteArtifactThemeResponse200]
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
) -> DeleteArtifactThemeResponse200 | None:
    """Delete an organization theme; the artifacts on it, and the organization default when it names it, go
    back to Gatana

    Args:
        theme_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteArtifactThemeResponse200
    """

    return sync_detailed(
        theme_id=theme_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    theme_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeleteArtifactThemeResponse200]:
    """Delete an organization theme; the artifacts on it, and the organization default when it names it, go
    back to Gatana

    Args:
        theme_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteArtifactThemeResponse200]
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
) -> DeleteArtifactThemeResponse200 | None:
    """Delete an organization theme; the artifacts on it, and the organization default when it names it, go
    back to Gatana

    Args:
        theme_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteArtifactThemeResponse200
    """

    return (
        await asyncio_detailed(
            theme_id=theme_id,
            client=client,
        )
    ).parsed
