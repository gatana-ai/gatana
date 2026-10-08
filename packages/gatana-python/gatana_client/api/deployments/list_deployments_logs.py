from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.list_deployments_logs_response_200 import ListDeploymentsLogsResponse200
from ...models.schema_201 import Schema201
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    pod_name: str,
    container_name: str | Unset = UNSET,
    previous: Schema201 | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["podName"] = pod_name

    params["containerName"] = container_name

    json_previous: str | Unset = UNSET
    if not isinstance(previous, Unset):
        json_previous = previous.value

    params["previous"] = json_previous

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/deployments/logs",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ListDeploymentsLogsResponse200 | None:
    if response.status_code == 200:
        response_200 = ListDeploymentsLogsResponse200.from_dict(response.json())

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ListDeploymentsLogsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    pod_name: str,
    container_name: str | Unset = UNSET,
    previous: Schema201 | Unset = UNSET,
) -> Response[ListDeploymentsLogsResponse200]:
    """Get the logs of a container of a pod, or stream them when the Accept header is text/event-stream.
    Defaults to the server container; set previous=true for the logs of the previous container instance

    Args:
        pod_name (str): Name of the pod
        container_name (str | Unset):
        previous (Schema201 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListDeploymentsLogsResponse200]
    """

    kwargs = _get_kwargs(
        pod_name=pod_name,
        container_name=container_name,
        previous=previous,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    pod_name: str,
    container_name: str | Unset = UNSET,
    previous: Schema201 | Unset = UNSET,
) -> ListDeploymentsLogsResponse200 | None:
    """Get the logs of a container of a pod, or stream them when the Accept header is text/event-stream.
    Defaults to the server container; set previous=true for the logs of the previous container instance

    Args:
        pod_name (str): Name of the pod
        container_name (str | Unset):
        previous (Schema201 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListDeploymentsLogsResponse200
    """

    return sync_detailed(
        client=client,
        pod_name=pod_name,
        container_name=container_name,
        previous=previous,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    pod_name: str,
    container_name: str | Unset = UNSET,
    previous: Schema201 | Unset = UNSET,
) -> Response[ListDeploymentsLogsResponse200]:
    """Get the logs of a container of a pod, or stream them when the Accept header is text/event-stream.
    Defaults to the server container; set previous=true for the logs of the previous container instance

    Args:
        pod_name (str): Name of the pod
        container_name (str | Unset):
        previous (Schema201 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ListDeploymentsLogsResponse200]
    """

    kwargs = _get_kwargs(
        pod_name=pod_name,
        container_name=container_name,
        previous=previous,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    pod_name: str,
    container_name: str | Unset = UNSET,
    previous: Schema201 | Unset = UNSET,
) -> ListDeploymentsLogsResponse200 | None:
    """Get the logs of a container of a pod, or stream them when the Accept header is text/event-stream.
    Defaults to the server container; set previous=true for the logs of the previous container instance

    Args:
        pod_name (str): Name of the pod
        container_name (str | Unset):
        previous (Schema201 | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ListDeploymentsLogsResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            pod_name=pod_name,
            container_name=container_name,
            previous=previous,
        )
    ).parsed
