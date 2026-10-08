from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.schema_605 import Schema605
from ...models.schema_606 import Schema606
from ...models.test_open_api_spec_request import TestOpenApiSpecRequest
from ...types import UNSET, Response, Unset


def _get_kwargs(
    server_slug: str,
    *,
    body: TestOpenApiSpecRequest | Unset = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/mcp-servers/{server_slug}/openapi/test".format(
            server_slug=quote(str(server_slug), safe=""),
        ),
    }

    if not isinstance(body, Unset):
        _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Schema605 | Schema606 | None:
    if response.status_code == 200:

        def _parse_response_200(data: object) -> Schema605 | Schema606:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_test_open_api_spec_response_type_0 = Schema605.from_dict(data)

                return componentsschemas_test_open_api_spec_response_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_test_open_api_spec_response_type_1 = Schema606.from_dict(data)

            return componentsschemas_test_open_api_spec_response_type_1

        response_200 = _parse_response_200(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Schema605 | Schema606]:
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
    body: TestOpenApiSpecRequest | Unset = UNSET,
) -> Response[Schema605 | Schema606]:
    """Fetch a remote OpenAPI/Swagger specification from the given URL and validate that it is a valid spec

    Args:
        server_slug (str):
        body (TestOpenApiSpecRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Schema605 | Schema606]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    body: TestOpenApiSpecRequest | Unset = UNSET,
) -> Schema605 | Schema606 | None:
    """Fetch a remote OpenAPI/Swagger specification from the given URL and validate that it is a valid spec

    Args:
        server_slug (str):
        body (TestOpenApiSpecRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Schema605 | Schema606
    """

    return sync_detailed(
        server_slug=server_slug,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    body: TestOpenApiSpecRequest | Unset = UNSET,
) -> Response[Schema605 | Schema606]:
    """Fetch a remote OpenAPI/Swagger specification from the given URL and validate that it is a valid spec

    Args:
        server_slug (str):
        body (TestOpenApiSpecRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Schema605 | Schema606]
    """

    kwargs = _get_kwargs(
        server_slug=server_slug,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    server_slug: str,
    *,
    client: AuthenticatedClient | Client,
    body: TestOpenApiSpecRequest | Unset = UNSET,
) -> Schema605 | Schema606 | None:
    """Fetch a remote OpenAPI/Swagger specification from the given URL and validate that it is a valid spec

    Args:
        server_slug (str):
        body (TestOpenApiSpecRequest | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Schema605 | Schema606
    """

    return (
        await asyncio_detailed(
            server_slug=server_slug,
            client=client,
            body=body,
        )
    ).parsed
