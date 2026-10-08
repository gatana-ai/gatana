from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.list_skills_response import ListSkillsResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    query: str | Unset = UNSET,
    collection: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["query"] = query

    params["collection"] = collection

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/skills",
        "params": params,
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> ListSkillsResponse | None:
    if response.status_code == 200:
        response_200 = ListSkillsResponse.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[ListSkillsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    query: str | Unset = UNSET,
    collection: str | Unset = UNSET,
) -> Response[ListSkillsResponse]:
    """List the skills the caller can read and the collections they can see, optionally narrowed to one
    collection or to a text in the name or description

    Args:
        query (str | Unset):
        collection (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListSkillsResponse]
    """

    kwargs = _get_kwargs(
        query=query,
        collection=collection,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    query: str | Unset = UNSET,
    collection: str | Unset = UNSET,
) -> ListSkillsResponse | None:
    """List the skills the caller can read and the collections they can see, optionally narrowed to one
    collection or to a text in the name or description

    Args:
        query (str | Unset):
        collection (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListSkillsResponse
    """

    return sync_detailed(
        client=client,
        query=query,
        collection=collection,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    query: str | Unset = UNSET,
    collection: str | Unset = UNSET,
) -> Response[ListSkillsResponse]:
    """List the skills the caller can read and the collections they can see, optionally narrowed to one
    collection or to a text in the name or description

    Args:
        query (str | Unset):
        collection (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListSkillsResponse]
    """

    kwargs = _get_kwargs(
        query=query,
        collection=collection,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    query: str | Unset = UNSET,
    collection: str | Unset = UNSET,
) -> ListSkillsResponse | None:
    """List the skills the caller can read and the collections they can see, optionally narrowed to one
    collection or to a text in the name or description

    Args:
        query (str | Unset):
        collection (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListSkillsResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            query=query,
            collection=collection,
        )
    ).parsed
