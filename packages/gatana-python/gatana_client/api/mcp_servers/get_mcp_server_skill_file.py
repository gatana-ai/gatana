from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_mcp_server_skill_file_response import GetMcpServerSkillFileResponse
from ...types import UNSET, Response


def _get_kwargs(
    server_slug: str,
    *,
    uri: str,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["uri"] = uri

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/mcp-servers/{server_slug}/skill-files".format(
            server_slug=quote(str(server_slug), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetMcpServerSkillFileResponse | None:
    if response.status_code == 200:
        response_200 = GetMcpServerSkillFileResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[GetMcpServerSkillFileResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    uri: str,
) -> Response[GetMcpServerSkillFileResponse]:
    """Read one file of a skill from an MCP server with the caller's credentials and verify it against the
    skill entry

    Args:
        server_slug (str):
        uri (str): URI of the file as the server publishes it

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetMcpServerSkillFileResponse]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        uri=uri,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    uri: str,
) -> GetMcpServerSkillFileResponse | None:
    """Read one file of a skill from an MCP server with the caller's credentials and verify it against the
    skill entry

    Args:
        server_slug (str):
        uri (str): URI of the file as the server publishes it

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetMcpServerSkillFileResponse
    """

    return sync_detailed(
        server_slug=server_slug,
        client=client,
        uri=uri,
    ).parsed


async def asyncio_detailed(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    uri: str,
) -> Response[GetMcpServerSkillFileResponse]:
    """Read one file of a skill from an MCP server with the caller's credentials and verify it against the
    skill entry

    Args:
        server_slug (str):
        uri (str): URI of the file as the server publishes it

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetMcpServerSkillFileResponse]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        uri=uri,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    uri: str,
) -> GetMcpServerSkillFileResponse | None:
    """Read one file of a skill from an MCP server with the caller's credentials and verify it against the
    skill entry

    Args:
        server_slug (str):
        uri (str): URI of the file as the server publishes it

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetMcpServerSkillFileResponse
    """

    return (
        await asyncio_detailed(
            server_slug=server_slug,
            client=client,
            uri=uri,
        )
    ).parsed
