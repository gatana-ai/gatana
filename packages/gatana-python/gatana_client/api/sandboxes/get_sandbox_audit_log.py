from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.sandbox_audit_log import SandboxAuditLog
from ...types import Response


def _get_kwargs(
    sandbox_id: str,
    id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/sandboxes/{sandbox_id}/audit-logs/{id}".format(
            sandbox_id=quote(str(sandbox_id), safe=""),
            id=quote(str(id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> SandboxAuditLog | None:
    if response.status_code == 200:
        response_200 = SandboxAuditLog.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[SandboxAuditLog]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    sandbox_id: str,
    id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[SandboxAuditLog]:
    """Get a single audit log entry of the sandbox by ID

    Args:
        sandbox_id (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SandboxAuditLog]
    """

    kwargs = _get_kwargs(
        sandbox_id=sandbox_id,
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    sandbox_id: str,
    id: str,
    *,
    client: AuthenticatedClient | Client,
) -> SandboxAuditLog | None:
    """Get a single audit log entry of the sandbox by ID

    Args:
        sandbox_id (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SandboxAuditLog
    """

    return sync_detailed(
        sandbox_id=sandbox_id,
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    sandbox_id: str,
    id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[SandboxAuditLog]:
    """Get a single audit log entry of the sandbox by ID

    Args:
        sandbox_id (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SandboxAuditLog]
    """

    kwargs = _get_kwargs(
        sandbox_id=sandbox_id,
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    sandbox_id: str,
    id: str,
    *,
    client: AuthenticatedClient | Client,
) -> SandboxAuditLog | None:
    """Get a single audit log entry of the sandbox by ID

    Args:
        sandbox_id (str):
        id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SandboxAuditLog
    """

    return (
        await asyncio_detailed(
            sandbox_id=sandbox_id,
            id=id,
            client=client,
        )
    ).parsed
