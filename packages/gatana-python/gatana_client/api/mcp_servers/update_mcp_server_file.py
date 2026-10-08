from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.update_mcp_server_file_response_200 import UpdateMcpServerFileResponse200
from ...types import Response


def _get_kwargs(
    server_slug: str,
    file_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/mcp-servers/{server_slug}/files/{file_id}".format(
            server_slug=quote(str(server_slug), safe=""),
            file_id=quote(str(file_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> UpdateMcpServerFileResponse200 | None:
    if response.status_code == 200:
        response_200 = UpdateMcpServerFileResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[UpdateMcpServerFileResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    server_slug: str,
    file_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[UpdateMcpServerFileResponse200]:
    """Replace the contents of an existing file of an MCP server with the uploaded file

    Args:
        server_slug (str):
        file_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateMcpServerFileResponse200]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        file_id=file_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    server_slug: str,
    file_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> UpdateMcpServerFileResponse200 | None:
    """Replace the contents of an existing file of an MCP server with the uploaded file

    Args:
        server_slug (str):
        file_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateMcpServerFileResponse200
    """

    return sync_detailed(
        server_slug=server_slug,
        file_id=file_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    server_slug: str,
    file_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[UpdateMcpServerFileResponse200]:
    """Replace the contents of an existing file of an MCP server with the uploaded file

    Args:
        server_slug (str):
        file_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateMcpServerFileResponse200]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        file_id=file_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    server_slug: str,
    file_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> UpdateMcpServerFileResponse200 | None:
    """Replace the contents of an existing file of an MCP server with the uploaded file

    Args:
        server_slug (str):
        file_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateMcpServerFileResponse200
    """

    return (
        await asyncio_detailed(
            server_slug=server_slug,
            file_id=file_id,
            client=client,
        )
    ).parsed
