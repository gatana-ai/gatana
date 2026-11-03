from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.deployment_log_payload_pod_info import DeploymentLogPayloadPodInfo
from ...models.schema_965 import Schema965
from ...models.schema_1002 import Schema1002
from ...models.schema_1003 import Schema1003
from ...models.schema_1005 import Schema1005
from ...models.schema_1006 import Schema1006
from ...models.schema_1010 import Schema1010
from ...models.schema_1011 import Schema1011
from ...models.schema_1015 import Schema1015
from ...models.schema_1016 import Schema1016
from ...models.schema_1017 import Schema1017
from ...models.schema_1019 import Schema1019
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
    | Schema1002
    | Schema1003
    | Schema1005
    | Schema1006
    | Schema1010
    | Schema1011
    | Schema1015
    | Schema1016
    | Schema1017
    | Schema1019
    | Schema965
    | None
):
    if response.status_code == 200:

        def _parse_response_200(
            data: object,
        ) -> (
            DeploymentLogPayloadPodInfo
            | Schema1002
            | Schema1003
            | Schema1005
            | Schema1006
            | Schema1010
            | Schema1011
            | Schema1015
            | Schema1016
            | Schema1017
            | Schema1019
            | Schema965
        ):
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_0 = Schema965.from_dict(data)

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
                componentsschemas_deployment_log_payload_type_2 = Schema1002.from_dict(data)

                return componentsschemas_deployment_log_payload_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_3 = Schema1003.from_dict(data)

                return componentsschemas_deployment_log_payload_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_4 = Schema1005.from_dict(data)

                return componentsschemas_deployment_log_payload_type_4
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_5 = Schema1006.from_dict(data)

                return componentsschemas_deployment_log_payload_type_5
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_6 = Schema1010.from_dict(data)

                return componentsschemas_deployment_log_payload_type_6
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_7 = Schema1011.from_dict(data)

                return componentsschemas_deployment_log_payload_type_7
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_8 = Schema1015.from_dict(data)

                return componentsschemas_deployment_log_payload_type_8
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_9 = Schema1016.from_dict(data)

                return componentsschemas_deployment_log_payload_type_9
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_deployment_log_payload_type_10 = Schema1017.from_dict(data)

                return componentsschemas_deployment_log_payload_type_10
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_deployment_log_payload_type_11 = Schema1019.from_dict(data)

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
    | Schema1002
    | Schema1003
    | Schema1005
    | Schema1006
    | Schema1010
    | Schema1011
    | Schema1015
    | Schema1016
    | Schema1017
    | Schema1019
    | Schema965
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
    | Schema1002
    | Schema1003
    | Schema1005
    | Schema1006
    | Schema1010
    | Schema1011
    | Schema1015
    | Schema1016
    | Schema1017
    | Schema1019
    | Schema965
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
        Response[DeploymentLogPayloadPodInfo | Schema1002 | Schema1003 | Schema1005 | Schema1006 | Schema1010 | Schema1011 | Schema1015 | Schema1016 | Schema1017 | Schema1019 | Schema965]
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
    | Schema1002
    | Schema1003
    | Schema1005
    | Schema1006
    | Schema1010
    | Schema1011
    | Schema1015
    | Schema1016
    | Schema1017
    | Schema1019
    | Schema965
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
        DeploymentLogPayloadPodInfo | Schema1002 | Schema1003 | Schema1005 | Schema1006 | Schema1010 | Schema1011 | Schema1015 | Schema1016 | Schema1017 | Schema1019 | Schema965
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
    | Schema1002
    | Schema1003
    | Schema1005
    | Schema1006
    | Schema1010
    | Schema1011
    | Schema1015
    | Schema1016
    | Schema1017
    | Schema1019
    | Schema965
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
        Response[DeploymentLogPayloadPodInfo | Schema1002 | Schema1003 | Schema1005 | Schema1006 | Schema1010 | Schema1011 | Schema1015 | Schema1016 | Schema1017 | Schema1019 | Schema965]
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
    | Schema1002
    | Schema1003
    | Schema1005
    | Schema1006
    | Schema1010
    | Schema1011
    | Schema1015
    | Schema1016
    | Schema1017
    | Schema1019
    | Schema965
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
        DeploymentLogPayloadPodInfo | Schema1002 | Schema1003 | Schema1005 | Schema1006 | Schema1010 | Schema1011 | Schema1015 | Schema1016 | Schema1017 | Schema1019 | Schema965
    """

    return (
        await asyncio_detailed(
            client=client,
            hosted_function_id=hosted_function_id,
            server_slug=server_slug,
            pod_name=pod_name,
        )
    ).parsed
