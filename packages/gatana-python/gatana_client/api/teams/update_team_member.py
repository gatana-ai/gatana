from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.update_team_member_body import UpdateTeamMemberBody
from ...models.update_team_member_response_200 import UpdateTeamMemberResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    team_id: str,
    user_id: str,
    *,
    body: UpdateTeamMemberBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/teams/{team_id}/members/{user_id}".format(
            team_id=quote(str(team_id), safe=""),
            user_id=quote(str(user_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> UpdateTeamMemberResponse200 | None:
    if response.status_code == 200:
        response_200 = UpdateTeamMemberResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[UpdateTeamMemberResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    team_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateTeamMemberBody | Unset = UNSET,
) -> Response[UpdateTeamMemberResponse200]:
    """Change the role of a team member

    Args:
        team_id (str): ID of the team
        user_id (str): ID of the team member
        body (UpdateTeamMemberBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateTeamMemberResponse200]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        user_id=user_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateTeamMemberBody | Unset = UNSET,
) -> UpdateTeamMemberResponse200 | None:
    """Change the role of a team member

    Args:
        team_id (str): ID of the team
        user_id (str): ID of the team member
        body (UpdateTeamMemberBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateTeamMemberResponse200
    """

    return sync_detailed(
        team_id=team_id,
        user_id=user_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    team_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateTeamMemberBody | Unset = UNSET,
) -> Response[UpdateTeamMemberResponse200]:
    """Change the role of a team member

    Args:
        team_id (str): ID of the team
        user_id (str): ID of the team member
        body (UpdateTeamMemberBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateTeamMemberResponse200]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        user_id=user_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str,
    user_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateTeamMemberBody | Unset = UNSET,
) -> UpdateTeamMemberResponse200 | None:
    """Change the role of a team member

    Args:
        team_id (str): ID of the team
        user_id (str): ID of the team member
        body (UpdateTeamMemberBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateTeamMemberResponse200
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            user_id=user_id,
            client=client,
            body=body,
        )
    ).parsed
