from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_team_claim_mapping_body import CreateTeamClaimMappingBody
from ...models.create_team_claim_mapping_response_200 import CreateTeamClaimMappingResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    team_id: str,
    *,
    body: CreateTeamClaimMappingBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/teams/{team_id}/claim-mappings".format(
            team_id=quote(str(team_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CreateTeamClaimMappingResponse200 | None:
    if response.status_code == 200:
        response_200 = CreateTeamClaimMappingResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CreateTeamClaimMappingResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    team_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateTeamClaimMappingBody | Unset = UNSET,
) -> Response[CreateTeamClaimMappingResponse200]:
    """Create a claim mapping that gives membership of a team to users with a matching identity provider
    claim

    Args:
        team_id (str): ID of the team
        body (CreateTeamClaimMappingBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateTeamClaimMappingResponse200]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateTeamClaimMappingBody | Unset = UNSET,
) -> CreateTeamClaimMappingResponse200 | None:
    """Create a claim mapping that gives membership of a team to users with a matching identity provider
    claim

    Args:
        team_id (str): ID of the team
        body (CreateTeamClaimMappingBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateTeamClaimMappingResponse200
    """

    return sync_detailed(
        team_id=team_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    team_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateTeamClaimMappingBody | Unset = UNSET,
) -> Response[CreateTeamClaimMappingResponse200]:
    """Create a claim mapping that gives membership of a team to users with a matching identity provider
    claim

    Args:
        team_id (str): ID of the team
        body (CreateTeamClaimMappingBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateTeamClaimMappingResponse200]
    """

    kwargs = _get_kwargs(
        team_id=team_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CreateTeamClaimMappingBody | Unset = UNSET,
) -> CreateTeamClaimMappingResponse200 | None:
    """Create a claim mapping that gives membership of a team to users with a matching identity provider
    claim

    Args:
        team_id (str): ID of the team
        body (CreateTeamClaimMappingBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateTeamClaimMappingResponse200
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            client=client,
            body=body,
        )
    ).parsed
