from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_team_invitation_response_200 import DeleteTeamInvitationResponse200
from ...types import Response


def _get_kwargs(
    team_id: str,
    invitation_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/teams/{team_id}/invitations/{invitation_id}".format(
            team_id=quote(str(team_id), safe=""),
            invitation_id=quote(str(invitation_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeleteTeamInvitationResponse200 | None:
    if response.status_code == 200:
        response_200 = DeleteTeamInvitationResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DeleteTeamInvitationResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    team_id: str,
    invitation_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeleteTeamInvitationResponse200]:
    """Delete a team invitation

    Args:
        team_id (str): ID of the team
        invitation_id (str): ID of the invitation

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteTeamInvitationResponse200]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        invitation_id=invitation_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_id: str,
    invitation_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> DeleteTeamInvitationResponse200 | None:
    """Delete a team invitation

    Args:
        team_id (str): ID of the team
        invitation_id (str): ID of the invitation

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteTeamInvitationResponse200
    """

    return sync_detailed(
        team_id=team_id,
        invitation_id=invitation_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    team_id: str,
    invitation_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeleteTeamInvitationResponse200]:
    """Delete a team invitation

    Args:
        team_id (str): ID of the team
        invitation_id (str): ID of the invitation

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteTeamInvitationResponse200]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        invitation_id=invitation_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str,
    invitation_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> DeleteTeamInvitationResponse200 | None:
    """Delete a team invitation

    Args:
        team_id (str): ID of the team
        invitation_id (str): ID of the invitation

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteTeamInvitationResponse200
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            invitation_id=invitation_id,
            client=client,
        )
    ).parsed
