from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_sandbox_write_file_response_200 import CreateSandboxWriteFileResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    sandbox_id: str,
    *,
    body: Any | Unset = UNSET,
    path: str,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["path"] = path

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/sandboxes/{sandbox_id}/write-file".format(
            sandbox_id=quote(str(sandbox_id), safe=""),
        ),
        "params": params,
    }

    if not isinstance(body, Unset):
        _kwargs["content"] = body.payload

    headers["Content-Type"] = "application/octet-stream"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CreateSandboxWriteFileResponse200 | None:
    if response.status_code == 200:
        response_200 = CreateSandboxWriteFileResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CreateSandboxWriteFileResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    sandbox_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: Any | Unset = UNSET,
    path: str,
) -> Response[CreateSandboxWriteFileResponse200]:
    """Write the raw request body to the given file path in the sandbox

    Args:
        sandbox_id (str):
        path (str):
        body (Any | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateSandboxWriteFileResponse200]
    """

    kwargs = _get_kwargs(
        sandbox_id=sandbox_id,
        body=body,
        path=path,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    sandbox_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: Any | Unset = UNSET,
    path: str,
) -> CreateSandboxWriteFileResponse200 | None:
    """Write the raw request body to the given file path in the sandbox

    Args:
        sandbox_id (str):
        path (str):
        body (Any | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateSandboxWriteFileResponse200
    """

    return sync_detailed(
        sandbox_id=sandbox_id,
        client=client,
        body=body,
        path=path,
    ).parsed


async def asyncio_detailed(
    sandbox_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: Any | Unset = UNSET,
    path: str,
) -> Response[CreateSandboxWriteFileResponse200]:
    """Write the raw request body to the given file path in the sandbox

    Args:
        sandbox_id (str):
        path (str):
        body (Any | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateSandboxWriteFileResponse200]
    """

    kwargs = _get_kwargs(
        sandbox_id=sandbox_id,
        body=body,
        path=path,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    sandbox_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: Any | Unset = UNSET,
    path: str,
) -> CreateSandboxWriteFileResponse200 | None:
    """Write the raw request body to the given file path in the sandbox

    Args:
        sandbox_id (str):
        path (str):
        body (Any | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateSandboxWriteFileResponse200
    """

    return (
        await asyncio_detailed(
            sandbox_id=sandbox_id,
            client=client,
            body=body,
            path=path,
        )
    ).parsed
