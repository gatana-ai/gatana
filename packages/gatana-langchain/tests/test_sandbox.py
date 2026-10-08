"""Tests for the GatanaSandbox implementation."""

from __future__ import annotations

from http import HTTPStatus
from unittest.mock import MagicMock, patch

import httpx
import pytest

from gatana_client import AuthenticatedClient
from gatana_client.models.create_sandbox_response import CreateSandboxResponse
from gatana_client.models.create_sandbox_write_file_response_200 import (
    CreateSandboxWriteFileResponse200,
)
from gatana_client.models.sandbox_dto import SandboxDto
from gatana_client.models.user_small_dto import UserSmallDto
from gatana_client.types import Response
from gatana_langchain.sandbox import GatanaSandbox, _parse_ndjson

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_sandbox_dto(sandbox_id: str = "sb-123") -> SandboxDto:
    return SandboxDto(
        id=sandbox_id,
        tenant_id="t-1",
        is_archived=False,
        last_activity_at="2026-01-01T00:00:00Z",
        created_at="2026-01-01T00:00:00Z",
        updated_at="2026-01-01T00:00:00Z",
        user=UserSmallDto(id="u-1", email="test@test.com", name="Test"),
    )


def _make_create_response(
    sandbox_id: str = "sb-123",
) -> Response[CreateSandboxResponse]:
    return Response(
        status_code=HTTPStatus.OK,
        content=b"",
        headers=httpx.Headers(),
        parsed=CreateSandboxResponse(sandbox=_make_sandbox_dto(sandbox_id)),
    )


@pytest.fixture()
def mock_client() -> AuthenticatedClient:
    return MagicMock(spec=AuthenticatedClient)


# ---------------------------------------------------------------------------
# NDJSON parsing
# ---------------------------------------------------------------------------


class TestParseNdjson:
    def test_stdout_only(self) -> None:
        raw = b'{"stream":"stdout","data":"hello"}\n{"done":true,"exitCode":0}\n'
        resp = _parse_ndjson(raw)
        assert resp.output == "hello"
        assert resp.exit_code == 0
        assert resp.truncated is False

    def test_stderr_included(self) -> None:
        raw = (
            b'{"stream":"stdout","data":"out"}\n'
            b'{"stream":"stderr","data":"err"}\n'
            b'{"done":true,"exitCode":1}\n'
        )
        resp = _parse_ndjson(raw)
        assert resp.output == "outerr"
        assert resp.exit_code == 1

    def test_error_line(self) -> None:
        raw = b'{"error":true,"message":"boom"}\n{"done":true,"exitCode":127}\n'
        resp = _parse_ndjson(raw)
        assert "boom" in resp.output
        assert resp.exit_code == 127

    def test_keepalive_ignored(self) -> None:
        raw = (
            b'{"keepAlive":true}\n'
            b'{"stream":"stdout","data":"ok"}\n'
            b'{"done":true,"exitCode":0}\n'
        )
        resp = _parse_ndjson(raw)
        assert resp.output == "ok"

    def test_empty_response(self) -> None:
        resp = _parse_ndjson(b"")
        assert resp.output == ""
        assert resp.exit_code is None

    def test_malformed_line_skipped(self) -> None:
        raw = b'not json\n{"stream":"stdout","data":"ok"}\n{"done":true,"exitCode":0}\n'
        resp = _parse_ndjson(raw)
        assert resp.output == "ok"
        assert resp.exit_code == 0

    def test_multiple_stdout_chunks(self) -> None:
        raw = (
            b'{"stream":"stdout","data":"line1\\n"}\n'
            b'{"stream":"stdout","data":"line2\\n"}\n'
            b'{"done":true,"exitCode":0}\n'
        )
        resp = _parse_ndjson(raw)
        assert resp.output == "line1\nline2\n"


# ---------------------------------------------------------------------------
# Sandbox lifecycle
# ---------------------------------------------------------------------------


class TestSandboxLifecycle:
    @patch("gatana_langchain.sandbox.create_sandbox")
    def test_create_new_sandbox(
        self, mock_post: MagicMock, mock_client: AuthenticatedClient
    ) -> None:
        mock_post.sync_detailed.return_value = _make_create_response("sb-new")
        sb = GatanaSandbox(client=mock_client)
        assert sb.id == "sb-new"
        assert sb._owns_sandbox is True
        mock_post.sync_detailed.assert_called_once_with(client=mock_client)

    def test_wrap_existing_sandbox(self, mock_client: AuthenticatedClient) -> None:
        sb = GatanaSandbox(client=mock_client, sandbox_id="sb-existing")
        assert sb.id == "sb-existing"
        assert sb._owns_sandbox is False

    @patch("gatana_langchain.sandbox.create_sandbox")
    def test_create_fails_raises(
        self, mock_post: MagicMock, mock_client: AuthenticatedClient
    ) -> None:
        mock_post.sync_detailed.return_value = Response(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            content=b'{"message":"something went wrong"}',
            headers=httpx.Headers(),
            parsed=None,
        )
        with pytest.raises(RuntimeError, match="HTTP 500"):
            GatanaSandbox(client=mock_client)

    @patch("gatana_langchain.sandbox.delete_sandbox")
    @patch("gatana_langchain.sandbox.create_sandbox")
    def test_context_manager_deletes_owned(
        self,
        mock_post: MagicMock,
        mock_delete: MagicMock,
        mock_client: AuthenticatedClient,
    ) -> None:
        mock_post.sync_detailed.return_value = _make_create_response("sb-ctx")
        with GatanaSandbox(client=mock_client) as sb:
            assert sb.id == "sb-ctx"
        mock_delete.sync.assert_called_once_with("sb-ctx", client=mock_client)

    @patch("gatana_langchain.sandbox.delete_sandbox")
    def test_context_manager_no_delete_for_wrapped(
        self,
        mock_delete: MagicMock,
        mock_client: AuthenticatedClient,
    ) -> None:
        with GatanaSandbox(client=mock_client, sandbox_id="sb-ext"):
            pass
        mock_delete.sync.assert_not_called()

    @patch("gatana_langchain.sandbox.delete_sandbox")
    @patch("gatana_langchain.sandbox.create_sandbox")
    def test_double_close_is_safe(
        self,
        mock_post: MagicMock,
        mock_delete: MagicMock,
        mock_client: AuthenticatedClient,
    ) -> None:
        mock_post.sync_detailed.return_value = _make_create_response("sb-dbl")
        sb = GatanaSandbox(client=mock_client)
        sb.close()
        sb.close()
        assert mock_delete.sync.call_count == 1


# ---------------------------------------------------------------------------
# Execute
# ---------------------------------------------------------------------------


class TestExecute:
    @patch("gatana_langchain.sandbox.exec_sandbox")
    def test_execute_basic(
        self, mock_exec: MagicMock, mock_client: AuthenticatedClient
    ) -> None:
        ndjson = (
            b'{"stream":"stdout","data":"hello world\\n"}\n{"done":true,"exitCode":0}\n'
        )
        mock_exec.sync_detailed.return_value = Response(
            status_code=HTTPStatus.OK,
            content=ndjson,
            headers=httpx.Headers(),
            parsed=None,
        )
        sb = GatanaSandbox(client=mock_client, sandbox_id="sb-1")
        result = sb.execute("echo hello world")
        assert result.output == "hello world\n"
        assert result.exit_code == 0

        call_args = mock_exec.sync_detailed.call_args
        assert call_args.args[0] == "sb-1"
        assert call_args.kwargs["body"].command == "echo hello world"

    @patch("gatana_langchain.sandbox.exec_sandbox")
    def test_execute_with_timeout(
        self, mock_exec: MagicMock, mock_client: AuthenticatedClient
    ) -> None:
        mock_exec.sync_detailed.return_value = Response(
            status_code=HTTPStatus.OK,
            content=b'{"done":true,"exitCode":0}\n',
            headers=httpx.Headers(),
            parsed=None,
        )
        sb = GatanaSandbox(client=mock_client, sandbox_id="sb-1")
        sb.execute("sleep 10", timeout=5)

        body = mock_exec.sync_detailed.call_args.kwargs["body"]
        assert body.timeout == 5.0

    @patch("gatana_langchain.sandbox.exec_sandbox")
    def test_execute_nonzero_exit(
        self, mock_exec: MagicMock, mock_client: AuthenticatedClient
    ) -> None:
        ndjson = (
            b'{"stream":"stderr","data":"not found\\n"}\n{"done":true,"exitCode":1}\n'
        )
        mock_exec.sync_detailed.return_value = Response(
            status_code=HTTPStatus.OK,
            content=ndjson,
            headers=httpx.Headers(),
            parsed=None,
        )
        sb = GatanaSandbox(client=mock_client, sandbox_id="sb-1")
        result = sb.execute("false")
        assert result.exit_code == 1
        assert "not found" in result.output


# ---------------------------------------------------------------------------
# File operations
# ---------------------------------------------------------------------------


class TestFileOperations:
    @patch("gatana_langchain.sandbox.create_sandbox_write_file")
    def test_upload_files_success(
        self, mock_write: MagicMock, mock_client: AuthenticatedClient
    ) -> None:
        mock_write.sync.return_value = CreateSandboxWriteFileResponse200(success=True)
        sb = GatanaSandbox(client=mock_client, sandbox_id="sb-1")
        results = sb.upload_files([("/app/test.txt", b"hello")])
        assert len(results) == 1
        assert results[0].path == "/app/test.txt"
        assert results[0].error is None

    @patch("gatana_langchain.sandbox.create_sandbox_write_file")
    def test_upload_files_failure(
        self, mock_write: MagicMock, mock_client: AuthenticatedClient
    ) -> None:
        mock_write.sync.return_value = CreateSandboxWriteFileResponse200(success=False)
        sb = GatanaSandbox(client=mock_client, sandbox_id="sb-1")
        results = sb.upload_files([("/readonly/file.txt", b"data")])
        assert results[0].error == "permission_denied"

    @patch("gatana_langchain.sandbox.create_sandbox_write_file")
    def test_upload_files_exception(
        self, mock_write: MagicMock, mock_client: AuthenticatedClient
    ) -> None:
        mock_write.sync.side_effect = RuntimeError("network error")
        sb = GatanaSandbox(client=mock_client, sandbox_id="sb-1")
        results = sb.upload_files([("/app/fail.txt", b"data")])
        assert results[0].error == "permission_denied"

    @patch("gatana_langchain.sandbox.create_sandbox_read_file")
    def test_download_files_success(
        self, mock_read: MagicMock, mock_client: AuthenticatedClient
    ) -> None:
        mock_read.sync_detailed.return_value = Response(
            status_code=HTTPStatus.OK,
            content=b"file content here",
            headers=httpx.Headers(),
            parsed=None,
        )
        sb = GatanaSandbox(client=mock_client, sandbox_id="sb-1")
        results = sb.download_files(["/app/test.txt"])
        assert len(results) == 1
        assert results[0].path == "/app/test.txt"
        assert results[0].content == b"file content here"
        assert results[0].error is None

    @patch("gatana_langchain.sandbox.create_sandbox_read_file")
    def test_download_files_not_found(
        self, mock_read: MagicMock, mock_client: AuthenticatedClient
    ) -> None:
        mock_read.sync_detailed.return_value = Response(
            status_code=HTTPStatus.NOT_FOUND,
            content=b"",
            headers=httpx.Headers(),
            parsed=None,
        )
        sb = GatanaSandbox(client=mock_client, sandbox_id="sb-1")
        results = sb.download_files(["/missing.txt"])
        assert results[0].error == "file_not_found"
        assert results[0].content is None

    @patch("gatana_langchain.sandbox.create_sandbox_read_file")
    def test_download_files_exception(
        self, mock_read: MagicMock, mock_client: AuthenticatedClient
    ) -> None:
        mock_read.sync_detailed.side_effect = RuntimeError("timeout")
        sb = GatanaSandbox(client=mock_client, sandbox_id="sb-1")
        results = sb.download_files(["/app/fail.txt"])
        assert results[0].error == "file_not_found"

    @patch("gatana_langchain.sandbox.create_sandbox_write_file")
    def test_upload_multiple_files(
        self, mock_write: MagicMock, mock_client: AuthenticatedClient
    ) -> None:
        mock_write.sync.return_value = CreateSandboxWriteFileResponse200(success=True)
        sb = GatanaSandbox(client=mock_client, sandbox_id="sb-1")
        files = [
            ("/app/a.txt", b"aaa"),
            ("/app/b.txt", b"bbb"),
            ("/app/c.txt", b"ccc"),
        ]
        results = sb.upload_files(files)
        assert len(results) == 3
        assert all(r.error is None for r in results)
        assert mock_write.sync.call_count == 3
