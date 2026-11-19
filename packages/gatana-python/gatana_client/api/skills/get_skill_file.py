from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_skill_file_response import GetSkillFileResponse
from ...types import Response


def _get_kwargs(
    skill_id: str,
    path: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/skills/{skill_id}/files/{path}".format(
            skill_id=quote(str(skill_id), safe=""),
            path=quote(str(path), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> GetSkillFileResponse | None:
    if response.status_code == 200:
        response_200 = GetSkillFileResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetSkillFileResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    skill_id: str,
    path: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[GetSkillFileResponse]:
    """Read a skill file as text, or as base64 for bytes that are not valid UTF-8

    Args:
        skill_id (str):
        path (str): Path of the file in the skill folder, e.g. "references/guide.md"

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSkillFileResponse]
    """

    kwargs = _get_kwargs(
        skill_id=skill_id,
        path=path,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    skill_id: str,
    path: str,
    *,
    client: AuthenticatedClient | Client,
) -> GetSkillFileResponse | None:
    """Read a skill file as text, or as base64 for bytes that are not valid UTF-8

    Args:
        skill_id (str):
        path (str): Path of the file in the skill folder, e.g. "references/guide.md"

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSkillFileResponse
    """

    return sync_detailed(
        skill_id=skill_id,
        path=path,
        client=client,
    ).parsed


async def asyncio_detailed(
    skill_id: str,
    path: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[GetSkillFileResponse]:
    """Read a skill file as text, or as base64 for bytes that are not valid UTF-8

    Args:
        skill_id (str):
        path (str): Path of the file in the skill folder, e.g. "references/guide.md"

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetSkillFileResponse]
    """

    kwargs = _get_kwargs(
        skill_id=skill_id,
        path=path,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    skill_id: str,
    path: str,
    *,
    client: AuthenticatedClient | Client,
) -> GetSkillFileResponse | None:
    """Read a skill file as text, or as base64 for bytes that are not valid UTF-8

    Args:
        skill_id (str):
        path (str): Path of the file in the skill folder, e.g. "references/guide.md"

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetSkillFileResponse
    """

    return (
        await asyncio_detailed(
            skill_id=skill_id,
            path=path,
            client=client,
        )
    ).parsed
