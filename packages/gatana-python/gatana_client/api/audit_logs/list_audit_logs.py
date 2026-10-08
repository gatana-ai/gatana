import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.paginated_audit_log_response import PaginatedAuditLogResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    page: str | Unset = UNSET,
    limit: str | Unset = UNSET,
    user_id: str | Unset = UNSET,
    entity_types: list[str] | str | Unset = UNSET,
    entity_id: str | Unset = UNSET,
    tenant_id: str | Unset = UNSET,
    start_date: datetime.datetime | Unset = UNSET,
    end_date: datetime.datetime | Unset = UNSET,
    search: str | Unset = UNSET,
    filter_: list[str] | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["page"] = page

    params["limit"] = limit

    params["userId"] = user_id

    json_entity_types: list[str] | str | Unset
    if isinstance(entity_types, Unset):
        json_entity_types = UNSET
    elif isinstance(entity_types, list):
        json_entity_types = entity_types

    else:
        json_entity_types = entity_types
    params["entityTypes"] = json_entity_types

    params["entityId"] = entity_id

    params["tenantId"] = tenant_id

    json_start_date: str | Unset = UNSET
    if not isinstance(start_date, Unset):
        json_start_date = start_date.isoformat()
    params["startDate"] = json_start_date

    json_end_date: str | Unset = UNSET
    if not isinstance(end_date, Unset):
        json_end_date = end_date.isoformat()
    params["endDate"] = json_end_date

    params["search"] = search

    json_filter_: list[str] | str | Unset
    if isinstance(filter_, Unset):
        json_filter_ = UNSET
    elif isinstance(filter_, list):
        json_filter_ = filter_

    else:
        json_filter_ = filter_
    params["filter"] = json_filter_

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/audit-logs",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PaginatedAuditLogResponse | None:
    if response.status_code == 200:
        response_200 = PaginatedAuditLogResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[PaginatedAuditLogResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    page: str | Unset = UNSET,
    limit: str | Unset = UNSET,
    user_id: str | Unset = UNSET,
    entity_types: list[str] | str | Unset = UNSET,
    entity_id: str | Unset = UNSET,
    tenant_id: str | Unset = UNSET,
    start_date: datetime.datetime | Unset = UNSET,
    end_date: datetime.datetime | Unset = UNSET,
    search: str | Unset = UNSET,
    filter_: list[str] | str | Unset = UNSET,
) -> Response[PaginatedAuditLogResponse]:
    """List audit log entries page by page. Callers without full access only see their own entries

    Args:
        page (str | Unset):
        limit (str | Unset):
        user_id (str | Unset):
        entity_types (list[str] | str | Unset):
        entity_id (str | Unset):
        tenant_id (str | Unset):
        start_date (datetime.datetime | Unset):
        end_date (datetime.datetime | Unset):
        search (str | Unset):
        filter_ (list[str] | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedAuditLogResponse]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        user_id=user_id,
        entity_types=entity_types,
        entity_id=entity_id,
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date,
        search=search,
        filter_=filter_,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    page: str | Unset = UNSET,
    limit: str | Unset = UNSET,
    user_id: str | Unset = UNSET,
    entity_types: list[str] | str | Unset = UNSET,
    entity_id: str | Unset = UNSET,
    tenant_id: str | Unset = UNSET,
    start_date: datetime.datetime | Unset = UNSET,
    end_date: datetime.datetime | Unset = UNSET,
    search: str | Unset = UNSET,
    filter_: list[str] | str | Unset = UNSET,
) -> PaginatedAuditLogResponse | None:
    """List audit log entries page by page. Callers without full access only see their own entries

    Args:
        page (str | Unset):
        limit (str | Unset):
        user_id (str | Unset):
        entity_types (list[str] | str | Unset):
        entity_id (str | Unset):
        tenant_id (str | Unset):
        start_date (datetime.datetime | Unset):
        end_date (datetime.datetime | Unset):
        search (str | Unset):
        filter_ (list[str] | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedAuditLogResponse
    """

    return sync_detailed(
        client=client,
        page=page,
        limit=limit,
        user_id=user_id,
        entity_types=entity_types,
        entity_id=entity_id,
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date,
        search=search,
        filter_=filter_,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    page: str | Unset = UNSET,
    limit: str | Unset = UNSET,
    user_id: str | Unset = UNSET,
    entity_types: list[str] | str | Unset = UNSET,
    entity_id: str | Unset = UNSET,
    tenant_id: str | Unset = UNSET,
    start_date: datetime.datetime | Unset = UNSET,
    end_date: datetime.datetime | Unset = UNSET,
    search: str | Unset = UNSET,
    filter_: list[str] | str | Unset = UNSET,
) -> Response[PaginatedAuditLogResponse]:
    """List audit log entries page by page. Callers without full access only see their own entries

    Args:
        page (str | Unset):
        limit (str | Unset):
        user_id (str | Unset):
        entity_types (list[str] | str | Unset):
        entity_id (str | Unset):
        tenant_id (str | Unset):
        start_date (datetime.datetime | Unset):
        end_date (datetime.datetime | Unset):
        search (str | Unset):
        filter_ (list[str] | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PaginatedAuditLogResponse]
    """

    kwargs = _get_kwargs(
        page=page,
        limit=limit,
        user_id=user_id,
        entity_types=entity_types,
        entity_id=entity_id,
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date,
        search=search,
        filter_=filter_,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    page: str | Unset = UNSET,
    limit: str | Unset = UNSET,
    user_id: str | Unset = UNSET,
    entity_types: list[str] | str | Unset = UNSET,
    entity_id: str | Unset = UNSET,
    tenant_id: str | Unset = UNSET,
    start_date: datetime.datetime | Unset = UNSET,
    end_date: datetime.datetime | Unset = UNSET,
    search: str | Unset = UNSET,
    filter_: list[str] | str | Unset = UNSET,
) -> PaginatedAuditLogResponse | None:
    """List audit log entries page by page. Callers without full access only see their own entries

    Args:
        page (str | Unset):
        limit (str | Unset):
        user_id (str | Unset):
        entity_types (list[str] | str | Unset):
        entity_id (str | Unset):
        tenant_id (str | Unset):
        start_date (datetime.datetime | Unset):
        end_date (datetime.datetime | Unset):
        search (str | Unset):
        filter_ (list[str] | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PaginatedAuditLogResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            page=page,
            limit=limit,
            user_id=user_id,
            entity_types=entity_types,
            entity_id=entity_id,
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date,
            search=search,
            filter_=filter_,
        )
    ).parsed
