"""Gatana sandbox backend implementation for LangChain deepagents."""

from __future__ import annotations

import io
import json
import logging
from typing import Any

from deepagents.backends.protocol import (
    ExecuteResponse,
    FileDownloadResponse,
    FileUploadResponse,
)
from deepagents.backends.sandbox import BaseSandbox

from gatana_client import AuthenticatedClient
from gatana_client.api.sandboxes import (
    create_sandbox,
    create_sandbox_read_file,
    create_sandbox_write_file,
    delete_sandbox,
    exec_sandbox,
)
from gatana_client.models.exec_command_body import ExecCommandBody
from gatana_client.types import File

logger = logging.getLogger(__name__)


def _parse_ndjson(raw: bytes) -> ExecuteResponse:
    """Parse an NDJSON exec response into an ExecuteResponse.

    The NDJSON stream contains lines of these types:
    - ``{"stream": "stdout"|"stderr", "data": "..."}`` — incremental output
    - ``{"done": true, "exitCode": N}`` — command finished
    - ``{"error": true, "message": "..."}`` — error
    - ``{"keepAlive": true}`` — heartbeat (ignored)
    """
    output_parts: list[str] = []
    exit_code: int | None = None

    for line in raw.split(b"\n"):
        line = line.strip()
        if not line:
            continue
        try:
            obj: dict[str, Any] = json.loads(line)
        except json.JSONDecodeError:
            logger.warning("Skipping unparseable NDJSON line: %r", line)
            continue

        if "stream" in obj:
            # ExecNdjsonOutputLine
            output_parts.append(obj.get("data", ""))
        elif "done" in obj:
            # ExecNdjsonDoneLine
            exit_code = obj.get("exitCode")
        elif "error" in obj:
            # ExecNdjsonErrorLine
            output_parts.append(obj.get("message", ""))
        # keepAlive lines are silently ignored

    return ExecuteResponse(
        output="".join(output_parts),
        exit_code=exit_code,
        truncated=False,
    )


class GatanaSandbox(BaseSandbox):
    """Gatana sandbox implementation conforming to ``BaseSandbox``.

    Provides command execution and file operations inside an isolated
    Gatana sandbox environment.

    The sandbox can either **create** a new sandbox automatically or
    **wrap** an existing one by ID.

    Examples
    --------
    Create a new sandbox (auto-deleted on exit)::

        from gatana_client import AuthenticatedClient
        from gatana_langchain import GatanaSandbox

        client = AuthenticatedClient(base_url="https://api.gatana.ai", token="...")
        with GatanaSandbox(client=client) as sb:
            result = sb.execute("echo hello")
            print(result.output)

    Wrap an existing sandbox (not deleted on exit)::

        sb = GatanaSandbox(client=client, sandbox_id="existing-id")
        result = sb.execute("ls /")
    """

    def __init__(
        self,
        *,
        client: AuthenticatedClient,
        sandbox_id: str | None = None,
    ) -> None:
        """Initialise a Gatana sandbox.

        Parameters
        ----------
        client:
            An authenticated Gatana API client.
        sandbox_id:
            If provided, wraps an existing sandbox (no auto-delete).
            If ``None``, a new sandbox is created and will be deleted
            on :meth:`close`.
        """
        self._client = client
        self._closed = False

        if sandbox_id is not None:
            self._sandbox_id = sandbox_id
            self._owns_sandbox = False
        else:
            resp = create_sandbox.sync_detailed(client=self._client)
            if resp.parsed is None:
                body_text = resp.content.decode(errors="replace")
                raise RuntimeError(
                    f"Failed to create sandbox: "
                    f"HTTP {resp.status_code.value} — {body_text}"
                )
            self._sandbox_id = resp.parsed.sandbox.id
            self._owns_sandbox = True

    # -- BaseSandbox protocol --------------------------------------------------

    @property
    def id(self) -> str:
        """Unique identifier for the sandbox."""
        return self._sandbox_id

    def execute(
        self,
        command: str,
        *,
        timeout: int | None = None,
    ) -> ExecuteResponse:
        """Execute a shell command inside the sandbox.

        Parameters
        ----------
        command:
            Shell command string to execute.
        timeout:
            Maximum seconds to wait.  ``None`` uses the server default.

        Returns
        -------
        ExecuteResponse
            Combined output, exit code, and truncation flag.
        """
        body = ExecCommandBody(
            command=command,
            timeout=float(timeout) if timeout is not None else timeout,
        )
        resp = exec_sandbox.sync_detailed(
            self._sandbox_id,
            client=self._client,
            body=body,
        )
        if resp.status_code.value != 200:
            body_text = resp.content.decode(errors="replace")
            raise RuntimeError(
                f"Exec failed: HTTP {resp.status_code.value} — {body_text}"
            )
        return _parse_ndjson(resp.content)

    def upload_files(self, files: list[tuple[str, bytes]]) -> list[FileUploadResponse]:
        """Upload files into the sandbox.

        Parameters
        ----------
        files:
            List of ``(path, content)`` tuples.

        Returns
        -------
        list[FileUploadResponse]
            One response per input file. Check ``error`` for failures.
        """
        responses: list[FileUploadResponse] = []
        for path, content in files:
            try:
                file_obj = File(payload=io.BytesIO(content))
                result = create_sandbox_write_file.sync(
                    self._sandbox_id,
                    client=self._client,
                    body=file_obj,
                    path=path,
                )
                if result is not None and result.success:
                    responses.append(FileUploadResponse(path=path, error=None))
                else:
                    responses.append(
                        FileUploadResponse(path=path, error="permission_denied")
                    )
            except Exception:
                logger.exception("Failed to upload file %s", path)
                responses.append(
                    FileUploadResponse(path=path, error="permission_denied")
                )
        return responses

    def download_files(self, paths: list[str]) -> list[FileDownloadResponse]:
        """Download files from the sandbox.

        Parameters
        ----------
        paths:
            List of file paths to download.

        Returns
        -------
        list[FileDownloadResponse]
            One response per input path. Check ``error`` for failures.
        """
        responses: list[FileDownloadResponse] = []
        for path in paths:
            try:
                resp = create_sandbox_read_file.sync_detailed(
                    self._sandbox_id,
                    client=self._client,
                    path=path,
                )
                if resp.status_code.value == 200:
                    responses.append(
                        FileDownloadResponse(
                            path=path,
                            content=resp.content,
                            error=None,
                        )
                    )
                else:
                    responses.append(
                        FileDownloadResponse(
                            path=path,
                            content=None,
                            error="file_not_found",
                        )
                    )
            except Exception:
                logger.exception("Failed to download file %s", path)
                responses.append(
                    FileDownloadResponse(
                        path=path, content=None, error="file_not_found"
                    )
                )
        return responses

    # -- Lifecycle -------------------------------------------------------------

    def close(self) -> None:
        """Delete the sandbox if it was created by this instance."""
        if self._closed:
            return
        self._closed = True
        if self._owns_sandbox:
            try:
                delete_sandbox.sync(self._sandbox_id, client=self._client)
            except Exception:
                logger.exception("Failed to delete sandbox %s", self._sandbox_id)

    def __enter__(self) -> GatanaSandbox:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
