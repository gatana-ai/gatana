from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.delete_team_profile_response_200 import DeleteTeamProfileResponse200
from ...types import Response


def _get_kwargs(
    team_id: str,
    profile_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/teams/{team_id}/profiles/{profile_id}".format(
            team_id=quote(str(team_id), safe=""),
            profile_id=quote(str(profile_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DeleteTeamProfileResponse200 | None:
    if response.status_code == 200:
        response_200 = DeleteTeamProfileResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[DeleteTeamProfileResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    team_id: str,
    profile_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeleteTeamProfileResponse200]:
    """Remove a profile assignment from a team. Only organization owners can remove a locked assignment

    Args:
        team_id (str): ID of the team
        profile_id (str): ID of the assigned profile

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteTeamProfileResponse200]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        profile_id=profile_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_id: str,
    profile_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> DeleteTeamProfileResponse200 | None:
    """Remove a profile assignment from a team. Only organization owners can remove a locked assignment

    Args:
        team_id (str): ID of the team
        profile_id (str): ID of the assigned profile

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteTeamProfileResponse200
    """

    return sync_detailed(
        team_id=team_id,
        profile_id=profile_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    team_id: str,
    profile_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DeleteTeamProfileResponse200]:
    """Remove a profile assignment from a team. Only organization owners can remove a locked assignment

    Args:
        team_id (str): ID of the team
        profile_id (str): ID of the assigned profile

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeleteTeamProfileResponse200]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        profile_id=profile_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str,
    profile_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> DeleteTeamProfileResponse200 | None:
    """Remove a profile assignment from a team. Only organization owners can remove a locked assignment

    Args:
        team_id (str): ID of the team
        profile_id (str): ID of the assigned profile

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeleteTeamProfileResponse200
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            profile_id=profile_id,
            client=client,
        )
    ).parsed
