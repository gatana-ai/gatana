from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.deployment_log_payload_pod_info import DeploymentLogPayloadPodInfo
from ...models.schema_1024 import Schema1024
from ...models.schema_1061 import Schema1061
from ...models.schema_1062 import Schema1062
from ...models.schema_1064 import Schema1064
from ...models.schema_1065 import Schema1065
from ...models.schema_1069 import Schema1069
from ...models.schema_1070 import Schema1070
from ...models.schema_1074 import Schema1074
from ...models.schema_1075 import Schema1075
from ...models.schema_1076 import Schema1076
from ...models.schema_1078 import Schema1078
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    hosted_function_id: str | Unset = UNSET,
    server_slug: str | Unset = UNSET,
    pod_name: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["hostedFunctionId"] = hosted_function_id

    params["serverSlug"] = server_slug

    params["podName"] = pod_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/deployments/deployment-logs",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    DeploymentLogPayloadPodInfo
    | Schema1024
    | Schema1061
    | Schema1062
    | Schema1064
    | Schema1065
    | Schema1069
    | Schema1070
    | Schema1074
    | Schema1075
    | Schema1076
    | Schema1078
    | None
):
    if response.status_code == 200:

        def _parse_response_200(
            data: object,
        ) -> (
            DeploymentLogPayloadPodInfo
            | Schema1024
            | Schema1061
            | Schema1062
            | Schema1064
            | Schema1065
            | Schema1069
            | Schema1070
            | Schema1074
            | Schema1075
            | Schema1076
            | Schema1078
        ):
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_0 = Schema1024.from_dict(data)

                return componentsschemas_deployment_log_payload_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_1 = DeploymentLogPayloadPodInfo.from_dict(data)

                return componentsschemas_deployment_log_payload_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_2 = Schema1061.from_dict(data)

                return componentsschemas_deployment_log_payload_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_3 = Schema1062.from_dict(data)

                return componentsschemas_deployment_log_payload_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_4 = Schema1064.from_dict(data)

                return componentsschemas_deployment_log_payload_type_4
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_5 = Schema1065.from_dict(data)

                return componentsschemas_deployment_log_payload_type_5
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_6 = Schema1069.from_dict(data)

                return componentsschemas_deployment_log_payload_type_6
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_7 = Schema1070.from_dict(data)

                return componentsschemas_deployment_log_payload_type_7
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_8 = Schema1074.from_dict(data)

                return componentsschemas_deployment_log_payload_type_8
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_9 = Schema1075.from_dict(data)

                return componentsschemas_deployment_log_payload_type_9
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_10 = Schema1076.from_dict(data)

                return componentsschemas_deployment_log_payload_type_10
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_deployment_log_payload_type_11 = Schema1078.from_dict(data)

            return componentsschemas_deployment_log_payload_type_11

        response_200 = _parse_response_200(response.text)

        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    DeploymentLogPayloadPodInfo
    | Schema1024
    | Schema1061
    | Schema1062
    | Schema1064
    | Schema1065
    | Schema1069
    | Schema1070
    | Schema1074
    | Schema1075
    | Schema1076
    | Schema1078
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    hosted_function_id: str | Unset = UNSET,
    server_slug: str | Unset = UNSET,
    pod_name: str | Unset = UNSET,
) -> Response[
    DeploymentLogPayloadPodInfo
    | Schema1024
    | Schema1061
    | Schema1062
    | Schema1064
    | Schema1065
    | Schema1069
    | Schema1070
    | Schema1074
    | Schema1075
    | Schema1076
    | Schema1078
]:
    """Stream the deployment and pod events of an MCP server as server-sent events. Requires read
    permission on the server and the Accept header text/event-stream; hostedFunctionId is no longer
    supported

    Args:
        hosted_function_id (str | Unset):
        server_slug (str | Unset):
        pod_name (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeploymentLogPayloadPodInfo | Schema1024 | Schema1061 | Schema1062 | Schema1064 | Schema1065 | Schema1069 | Schema1070 | Schema1074 | Schema1075 | Schema1076 | Schema1078]
    """

    kwargs = _get_kwargs(
        hosted_function_id=hosted_function_id,
        server_slug=server_slug,
        pod_name=pod_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    hosted_function_id: str | Unset = UNSET,
    server_slug: str | Unset = UNSET,
    pod_name: str | Unset = UNSET,
) -> (
    DeploymentLogPayloadPodInfo
    | Schema1024
    | Schema1061
    | Schema1062
    | Schema1064
    | Schema1065
    | Schema1069
    | Schema1070
    | Schema1074
    | Schema1075
    | Schema1076
    | Schema1078
    | None
):
    """Stream the deployment and pod events of an MCP server as server-sent events. Requires read
    permission on the server and the Accept header text/event-stream; hostedFunctionId is no longer
    supported

    Args:
        hosted_function_id (str | Unset):
        server_slug (str | Unset):
        pod_name (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeploymentLogPayloadPodInfo | Schema1024 | Schema1061 | Schema1062 | Schema1064 | Schema1065 | Schema1069 | Schema1070 | Schema1074 | Schema1075 | Schema1076 | Schema1078
    """

    return sync_detailed(
        client=client,
        hosted_function_id=hosted_function_id,
        server_slug=server_slug,
        pod_name=pod_name,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    hosted_function_id: str | Unset = UNSET,
    server_slug: str | Unset = UNSET,
    pod_name: str | Unset = UNSET,
) -> Response[
    DeploymentLogPayloadPodInfo
    | Schema1024
    | Schema1061
    | Schema1062
    | Schema1064
    | Schema1065
    | Schema1069
    | Schema1070
    | Schema1074
    | Schema1075
    | Schema1076
    | Schema1078
]:
    """Stream the deployment and pod events of an MCP server as server-sent events. Requires read
    permission on the server and the Accept header text/event-stream; hostedFunctionId is no longer
    supported

    Args:
        hosted_function_id (str | Unset):
        server_slug (str | Unset):
        pod_name (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DeploymentLogPayloadPodInfo | Schema1024 | Schema1061 | Schema1062 | Schema1064 | Schema1065 | Schema1069 | Schema1070 | Schema1074 | Schema1075 | Schema1076 | Schema1078]
    """

    kwargs = _get_kwargs(
        hosted_function_id=hosted_function_id,
        server_slug=server_slug,
        pod_name=pod_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    hosted_function_id: str | Unset = UNSET,
    server_slug: str | Unset = UNSET,
    pod_name: str | Unset = UNSET,
) -> (
    DeploymentLogPayloadPodInfo
    | Schema1024
    | Schema1061
    | Schema1062
    | Schema1064
    | Schema1065
    | Schema1069
    | Schema1070
    | Schema1074
    | Schema1075
    | Schema1076
    | Schema1078
    | None
):
    """Stream the deployment and pod events of an MCP server as server-sent events. Requires read
    permission on the server and the Accept header text/event-stream; hostedFunctionId is no longer
    supported

    Args:
        hosted_function_id (str | Unset):
        server_slug (str | Unset):
        pod_name (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DeploymentLogPayloadPodInfo | Schema1024 | Schema1061 | Schema1062 | Schema1064 | Schema1065 | Schema1069 | Schema1070 | Schema1074 | Schema1075 | Schema1076 | Schema1078
    """

    return (
        await asyncio_detailed(
            client=client,
            hosted_function_id=hosted_function_id,
            server_slug=server_slug,
            pod_name=pod_name,
        )
    ).parsed
