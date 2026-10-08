from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.update_mcp_server_file_name_body import UpdateMcpServerFileNameBody
from ...models.update_mcp_server_file_name_response_200 import UpdateMcpServerFileNameResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    server_slug: str,
    file_id: str,
    *,
    body: UpdateMcpServerFileNameBody | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/mcp-servers/{server_slug}/files/{file_id}/name".format(
            server_slug=quote(str(server_slug), safe=""),
            file_id=quote(str(file_id), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> UpdateMcpServerFileNameResponse200 | None:
    if response.status_code == 200:
        response_200 = UpdateMcpServerFileNameResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[UpdateMcpServerFileNameResponse200]:
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
    body: UpdateMcpServerFileNameBody | Unset = UNSET,
) -> Response[UpdateMcpServerFileNameResponse200]:
    """Rename a file of an MCP server

    Args:
        server_slug (str):
        file_id (str):
        body (UpdateMcpServerFileNameBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateMcpServerFileNameResponse200]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        file_id=file_id,
        body=body,
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
    body: UpdateMcpServerFileNameBody | Unset = UNSET,
) -> UpdateMcpServerFileNameResponse200 | None:
    """Rename a file of an MCP server

    Args:
        server_slug (str):
        file_id (str):
        body (UpdateMcpServerFileNameBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateMcpServerFileNameResponse200
    """

    return sync_detailed(
        server_slug=server_slug,
        file_id=file_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    server_slug: str,
    file_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateMcpServerFileNameBody | Unset = UNSET,
) -> Response[UpdateMcpServerFileNameResponse200]:
    """Rename a file of an MCP server

    Args:
        server_slug (str):
        file_id (str):
        body (UpdateMcpServerFileNameBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UpdateMcpServerFileNameResponse200]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        file_id=file_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    server_slug: str,
    file_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: UpdateMcpServerFileNameBody | Unset = UNSET,
) -> UpdateMcpServerFileNameResponse200 | None:
    """Rename a file of an MCP server

    Args:
        server_slug (str):
        file_id (str):
        body (UpdateMcpServerFileNameBody | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UpdateMcpServerFileNameResponse200
    """

    return (
        await asyncio_detailed(
            server_slug=server_slug,
            file_id=file_id,
            client=client,
            body=body,
        )
    ).parsed
