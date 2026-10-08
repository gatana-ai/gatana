import datetime
from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.paginated_sandbox_audit_log import PaginatedSandboxAuditLog
from ...types import UNSET, Response, Unset


def _get_kwargs(
    sandbox_id: str,
    *,
    page: str | Unset = UNSET,
    limit: str | Unset = UNSET,
    event_name: str | Unset = UNSET,
    start_date: datetime.datetime | Unset = UNSET,
    end_date: datetime.datetime | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["limit"] = limit

    params["eventName"] = event_name

    json_start_date: str | Unset = UNSET
    if not isinstance(start_date, Unset):
        json_start_date = start_date.isoformat()
    params["startDate"] = json_start_date

    json_end_date: str | Unset = UNSET
    if not isinstance(end_date, Unset):
        json_end_date = end_date.isoformat()
    params["endDate"] = json_end_date

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/sandboxes/{sandbox_id}/audit-logs".format(
            sandbox_id=quote(str(sandbox_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PaginatedSandboxAuditLog | None:
    if response.status_code == 200:
        response_200 = PaginatedSandboxAuditLog.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PaginatedSandboxAuditLog]:
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
    page: str | Unset = UNSET,
    limit: str | Unset = UNSET,
    event_name: str | Unset = UNSET,
    start_date: datetime.datetime | Unset = UNSET,
    end_date: datetime.datetime | Unset = UNSET,
) -> Response[PaginatedSandboxAuditLog]:
    """List the audit log entries of the sandbox, paginated and optionally filtered by date range

    Args:
        sandbox_id (str):
        page (str | Unset):
        limit (str | Unset):
        event_name (str | Unset):
        start_date (datetime.datetime | Unset):
        end_date (datetime.datetime | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedSandboxAuditLog]
    """

    kwargs = _get_kwargs(
        sandbox_id=sandbox_id,
        page=page,
        limit=limit,
        event_name=event_name,
        start_date=start_date,
        end_date=end_date,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    sandbox_id: str,
    *,
    client: AuthenticatedClient | Client,
    page: str | Unset = UNSET,
    limit: str | Unset = UNSET,
    event_name: str | Unset = UNSET,
    start_date: datetime.datetime | Unset = UNSET,
    end_date: datetime.datetime | Unset = UNSET,
) -> PaginatedSandboxAuditLog | None:
    """List the audit log entries of the sandbox, paginated and optionally filtered by date range

    Args:
        sandbox_id (str):
        page (str | Unset):
        limit (str | Unset):
        event_name (str | Unset):
        start_date (datetime.datetime | Unset):
        end_date (datetime.datetime | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedSandboxAuditLog
    """

    return sync_detailed(
        sandbox_id=sandbox_id,
        client=client,
        page=page,
        limit=limit,
        event_name=event_name,
        start_date=start_date,
        end_date=end_date,
    ).parsed


async def asyncio_detailed(
    sandbox_id: str,
    *,
    client: AuthenticatedClient | Client,
    page: str | Unset = UNSET,
    limit: str | Unset = UNSET,
    event_name: str | Unset = UNSET,
    start_date: datetime.datetime | Unset = UNSET,
    end_date: datetime.datetime | Unset = UNSET,
) -> Response[PaginatedSandboxAuditLog]:
    """List the audit log entries of the sandbox, paginated and optionally filtered by date range

    Args:
        sandbox_id (str):
        page (str | Unset):
        limit (str | Unset):
        event_name (str | Unset):
        start_date (datetime.datetime | Unset):
        end_date (datetime.datetime | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedSandboxAuditLog]
    """

    kwargs = _get_kwargs(
        sandbox_id=sandbox_id,
        page=page,
        limit=limit,
        event_name=event_name,
        start_date=start_date,
        end_date=end_date,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    sandbox_id: str,
    *,
    client: AuthenticatedClient | Client,
    page: str | Unset = UNSET,
    limit: str | Unset = UNSET,
    event_name: str | Unset = UNSET,
    start_date: datetime.datetime | Unset = UNSET,
    end_date: datetime.datetime | Unset = UNSET,
) -> PaginatedSandboxAuditLog | None:
    """List the audit log entries of the sandbox, paginated and optionally filtered by date range

    Args:
        sandbox_id (str):
        page (str | Unset):
        limit (str | Unset):
        event_name (str | Unset):
        start_date (datetime.datetime | Unset):
        end_date (datetime.datetime | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedSandboxAuditLog
    """

    return (
        await asyncio_detailed(
            sandbox_id=sandbox_id,
            client=client,
            page=page,
            limit=limit,
            event_name=event_name,
            start_date=start_date,
            end_date=end_date,
        )
    ).parsed
