from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.skill_dto import SkillDto
from ...models.update_skill_body import UpdateSkillBody
from ...types import UNSET, Response, Unset


def _get_kwargs(
    skill_id: str,
    *,
    body: UpdateSkillBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/skills/{skill_id}".format(
            skill_id=quote(str(skill_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SkillDto | None:
    if response.status_code == 200:
        response_200 = SkillDto.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SkillDto]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    skill_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateSkillBody | Unset = UNSET,
) -> Response[SkillDto]:
    """Update a skill from a SKILL.md document, or change its name, description, instructions, visibility
    or collection

    Args:
        skill_id (str):
        body (UpdateSkillBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SkillDto]
    """

    kwargs = _get_kwargs(
        skill_id=skill_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    skill_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateSkillBody | Unset = UNSET,
) -> SkillDto | None:
    """Update a skill from a SKILL.md document, or change its name, description, instructions, visibility
    or collection

    Args:
        skill_id (str):
        body (UpdateSkillBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SkillDto
    """

    return sync_detailed(
        skill_id=skill_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    skill_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateSkillBody | Unset = UNSET,
) -> Response[SkillDto]:
    """Update a skill from a SKILL.md document, or change its name, description, instructions, visibility
    or collection

    Args:
        skill_id (str):
        body (UpdateSkillBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SkillDto]
    """

    kwargs = _get_kwargs(
        skill_id=skill_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    skill_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateSkillBody | Unset = UNSET,
) -> SkillDto | None:
    """Update a skill from a SKILL.md document, or change its name, description, instructions, visibility
    or collection

    Args:
        skill_id (str):
        body (UpdateSkillBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SkillDto
    """

    return (
        await asyncio_detailed(
            skill_id=skill_id,
            client=client,
            body=body,
        )
    ).parsed
