from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.artifact_content_response import ArtifactContentResponse
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
        "url": "/artifacts/{artifact_id}/content".format(
            artifact_id=quote(str(artifact_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ArtifactContentResponse | None:
    if response.status_code == 200:
        response_200 = ArtifactContentResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ArtifactContentResponse]:
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
) -> Response[ArtifactContentResponse]:
    """Get the served HTML of an artifact version as JSON, rendered and themed, plus the Markdown source
    when there is one

    Args:
        artifact_id (str):
        version (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ArtifactContentResponse]
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
) -> ArtifactContentResponse | None:
    """Get the served HTML of an artifact version as JSON, rendered and themed, plus the Markdown source
    when there is one

    Args:
        artifact_id (str):
        version (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ArtifactContentResponse
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
) -> Response[ArtifactContentResponse]:
    """Get the served HTML of an artifact version as JSON, rendered and themed, plus the Markdown source
    when there is one

    Args:
        artifact_id (str):
        version (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ArtifactContentResponse]
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
) -> ArtifactContentResponse | None:
    """Get the served HTML of an artifact version as JSON, rendered and themed, plus the Markdown source
    when there is one

    Args:
        artifact_id (str):
        version (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ArtifactContentResponse
    """

    return (
        await asyncio_detailed(
            artifact_id=artifact_id,
            client=client,
            version=version,
        )
    ).parsed
