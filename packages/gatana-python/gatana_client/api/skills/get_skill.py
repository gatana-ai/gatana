from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_skill_response import GetSkillResponse
from ...types import Response


def _get_kwargs(
    skill_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/skills/{skill_id}".format(
            skill_id=quote(str(skill_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetSkillResponse | None:
    if response.status_code == 200:
        response_200 = GetSkillResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[GetSkillResponse]:
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
) -> Response[GetSkillResponse]:
    """Get a skill with its Markdown instructions, also rendered as one SKILL.md document

    Args:
        skill_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSkillResponse]
    """

    kwargs = _get_kwargs(
        skill_id=skill_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    skill_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> GetSkillResponse | None:
    """Get a skill with its Markdown instructions, also rendered as one SKILL.md document

    Args:
        skill_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSkillResponse
    """

    return sync_detailed(
        skill_id=skill_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    skill_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[GetSkillResponse]:
    """Get a skill with its Markdown instructions, also rendered as one SKILL.md document

    Args:
        skill_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSkillResponse]
    """

    kwargs = _get_kwargs(
        skill_id=skill_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    skill_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> GetSkillResponse | None:
    """Get a skill with its Markdown instructions, also rendered as one SKILL.md document

    Args:
        skill_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSkillResponse
    """

    return (
        await asyncio_detailed(
            skill_id=skill_id,
            client=client,
        )
    ).parsed
