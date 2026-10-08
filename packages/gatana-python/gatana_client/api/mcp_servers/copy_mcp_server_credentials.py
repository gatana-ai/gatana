from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.copy_mcp_server_credentials_response_200 import CopyMcpServerCredentialsResponse200
from ...models.schema_193 import Schema193
from ...types import UNSET, Response, Unset


def _get_kwargs(
    server_slug: str,
    *,
    id: str,
    to: Schema193,
    profile_id: str | Unset = UNSET,
    user_id: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["id"] = id

    json_to = to.value
    params["to"] = json_to

    params["profileId"] = profile_id

    params["userId"] = user_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/mcp-servers/{server_slug}/credentials/copy".format(
            server_slug=quote(str(server_slug), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CopyMcpServerCredentialsResponse200 | None:
    if response.status_code == 200:
        response_200 = CopyMcpServerCredentialsResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CopyMcpServerCredentialsResponse200]:
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
    id: str,
    to: Schema193,
    profile_id: str | Unset = UNSET,
    user_id: str | Unset = UNSET,
) -> Response[CopyMcpServerCredentialsResponse200]:
    """Copy credentials to another scope

    Args:
        server_slug (str):
        id (str): ID of the credentials to copy
        to (Schema193):
        profile_id (str | Unset):
        user_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CopyMcpServerCredentialsResponse200]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        id=id,
        to=to,
        profile_id=profile_id,
        user_id=user_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    id: str,
    to: Schema193,
    profile_id: str | Unset = UNSET,
    user_id: str | Unset = UNSET,
) -> CopyMcpServerCredentialsResponse200 | None:
    """Copy credentials to another scope

    Args:
        server_slug (str):
        id (str): ID of the credentials to copy
        to (Schema193):
        profile_id (str | Unset):
        user_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CopyMcpServerCredentialsResponse200
    """

    return sync_detailed(
        server_slug=server_slug,
        client=client,
        id=id,
        to=to,
        profile_id=profile_id,
        user_id=user_id,
    ).parsed


async def asyncio_detailed(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    id: str,
    to: Schema193,
    profile_id: str | Unset = UNSET,
    user_id: str | Unset = UNSET,
) -> Response[CopyMcpServerCredentialsResponse200]:
    """Copy credentials to another scope

    Args:
        server_slug (str):
        id (str): ID of the credentials to copy
        to (Schema193):
        profile_id (str | Unset):
        user_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CopyMcpServerCredentialsResponse200]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        id=id,
        to=to,
        profile_id=profile_id,
        user_id=user_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    id: str,
    to: Schema193,
    profile_id: str | Unset = UNSET,
    user_id: str | Unset = UNSET,
) -> CopyMcpServerCredentialsResponse200 | None:
    """Copy credentials to another scope

    Args:
        server_slug (str):
        id (str): ID of the credentials to copy
        to (Schema193):
        profile_id (str | Unset):
        user_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CopyMcpServerCredentialsResponse200
    """

    return (
        await asyncio_detailed(
            server_slug=server_slug,
            client=client,
            id=id,
            to=to,
            profile_id=profile_id,
            user_id=user_id,
        )
    ).parsed
