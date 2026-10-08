from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.artifact_shares_response import ArtifactSharesResponse
from ...models.schema_306 import Schema306
from ...types import Response


def _get_kwargs(
    artifact_id: str,
    member_type: Schema306,
    member_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/artifacts/{artifact_id}/shares/{member_type}/{member_id}".format(
            artifact_id=quote(str(artifact_id), safe=""),
            member_type=quote(str(member_type), safe=""),
            member_id=quote(str(member_id), safe=""),
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
    member_type: Schema306,
    member_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ArtifactSharesResponse]:
    """Stop sharing an artifact with a user or a team and return who it is still shared with

    Args:
        artifact_id (str):
        member_type (Schema306): 'users' to share with one user account, 'teams' to share with
            every member of a team
        member_id (str): ID of the user or of the team

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ArtifactSharesResponse]
    """

    kwargs = _get_kwargs(
        artifact_id=artifact_id,
        member_type=member_type,
        member_id=member_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    artifact_id: str,
    member_type: Schema306,
    member_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> ArtifactSharesResponse | None:
    """Stop sharing an artifact with a user or a team and return who it is still shared with

    Args:
        artifact_id (str):
        member_type (Schema306): 'users' to share with one user account, 'teams' to share with
            every member of a team
        member_id (str): ID of the user or of the team

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ArtifactSharesResponse
    """

    return sync_detailed(
        artifact_id=artifact_id,
        member_type=member_type,
        member_id=member_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    artifact_id: str,
    member_type: Schema306,
    member_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ArtifactSharesResponse]:
    """Stop sharing an artifact with a user or a team and return who it is still shared with

    Args:
        artifact_id (str):
        member_type (Schema306): 'users' to share with one user account, 'teams' to share with
            every member of a team
        member_id (str): ID of the user or of the team

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ArtifactSharesResponse]
    """

    kwargs = _get_kwargs(
        artifact_id=artifact_id,
        member_type=member_type,
        member_id=member_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    artifact_id: str,
    member_type: Schema306,
    member_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> ArtifactSharesResponse | None:
    """Stop sharing an artifact with a user or a team and return who it is still shared with

    Args:
        artifact_id (str):
        member_type (Schema306): 'users' to share with one user account, 'teams' to share with
            every member of a team
        member_id (str): ID of the user or of the team

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ArtifactSharesResponse
    """

    return (
        await asyncio_detailed(
            artifact_id=artifact_id,
            member_type=member_type,
            member_id=member_id,
            client=client,
        )
    ).parsed
