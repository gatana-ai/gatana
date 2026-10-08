from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.schema_332 import Schema332
from ...models.skill_shares_response import SkillSharesResponse
from ...types import Response


def _get_kwargs(
    skill_id: str,
    member_type: Schema332,
    member_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/skills/{skill_id}/shares/{member_type}/{member_id}".format(
            skill_id=quote(str(skill_id), safe=""),
            member_type=quote(str(member_type), safe=""),
            member_id=quote(str(member_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SkillSharesResponse | None:
    if response.status_code == 200:
        response_200 = SkillSharesResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SkillSharesResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    skill_id: str,
    member_type: Schema332,
    member_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[SkillSharesResponse]:
    """Stop sharing a skill with a user or a team and return who it is still shared with

    Args:
        skill_id (str):
        member_type (Schema332): 'users' to share with one user account, 'teams' to share with
            every member of a team
        member_id (str): ID of the user or of the team

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SkillSharesResponse]
    """

    kwargs = _get_kwargs(
        skill_id=skill_id,
        member_type=member_type,
        member_id=member_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    skill_id: str,
    member_type: Schema332,
    member_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> SkillSharesResponse | None:
    """Stop sharing a skill with a user or a team and return who it is still shared with

    Args:
        skill_id (str):
        member_type (Schema332): 'users' to share with one user account, 'teams' to share with
            every member of a team
        member_id (str): ID of the user or of the team

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SkillSharesResponse
    """

    return sync_detailed(
        skill_id=skill_id,
        member_type=member_type,
        member_id=member_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    skill_id: str,
    member_type: Schema332,
    member_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[SkillSharesResponse]:
    """Stop sharing a skill with a user or a team and return who it is still shared with

    Args:
        skill_id (str):
        member_type (Schema332): 'users' to share with one user account, 'teams' to share with
            every member of a team
        member_id (str): ID of the user or of the team

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SkillSharesResponse]
    """

    kwargs = _get_kwargs(
        skill_id=skill_id,
        member_type=member_type,
        member_id=member_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    skill_id: str,
    member_type: Schema332,
    member_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> SkillSharesResponse | None:
    """Stop sharing a skill with a user or a team and return who it is still shared with

    Args:
        skill_id (str):
        member_type (Schema332): 'users' to share with one user account, 'teams' to share with
            every member of a team
        member_id (str): ID of the user or of the team

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SkillSharesResponse
    """

    return (
        await asyncio_detailed(
            skill_id=skill_id,
            member_type=member_type,
            member_id=member_id,
            client=client,
        )
    ).parsed
