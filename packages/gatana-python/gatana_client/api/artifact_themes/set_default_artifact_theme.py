from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.set_default_artifact_theme_body import SetDefaultArtifactThemeBody
from ...models.set_default_artifact_theme_response import SetDefaultArtifactThemeResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: SetDefaultArtifactThemeBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/artifact-themes/default",
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> SetDefaultArtifactThemeResponse | None:
    if response.status_code == 200:
        response_200 = SetDefaultArtifactThemeResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[SetDefaultArtifactThemeResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: SetDefaultArtifactThemeBody | Unset = UNSET,
) -> Response[SetDefaultArtifactThemeResponse]:
    """Set the theme new artifacts get when their creator names none; existing artifacts keep their theme

    Args:
        body (SetDefaultArtifactThemeBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SetDefaultArtifactThemeResponse]
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
    body: SetDefaultArtifactThemeBody | Unset = UNSET,
) -> SetDefaultArtifactThemeResponse | None:
    """Set the theme new artifacts get when their creator names none; existing artifacts keep their theme

    Args:
        body (SetDefaultArtifactThemeBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SetDefaultArtifactThemeResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: SetDefaultArtifactThemeBody | Unset = UNSET,
) -> Response[SetDefaultArtifactThemeResponse]:
    """Set the theme new artifacts get when their creator names none; existing artifacts keep their theme

    Args:
        body (SetDefaultArtifactThemeBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SetDefaultArtifactThemeResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: SetDefaultArtifactThemeBody | Unset = UNSET,
) -> SetDefaultArtifactThemeResponse | None:
    """Set the theme new artifacts get when their creator names none; existing artifacts keep their theme

    Args:
        body (SetDefaultArtifactThemeBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SetDefaultArtifactThemeResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
