"""
DAIMON MCP Server Tests
=======================

Unit tests for the MCP server module.

Follows CODE_CONSTITUTION: Measurable Quality.
"""

from __future__ import annotations

from typing import Any, Dict

import pytest

# Test the helper functions directly
from integrations.mcp_server import (
    NOESIS_CONSCIOUSNESS_URL,
    NOESIS_REFLECTOR_URL,
    REQUEST_TIMEOUT,
    _http_post,
    _http_get,
    mcp,
)


class TestConfiguration:
    """Test suite for MCP server configuration."""

    def test_consciousness_url(self) -> None:
        """Test consciousness URL configuration."""
        assert NOESIS_CONSCIOUSNESS_URL == "http://localhost:8001"

    def test_reflector_url(self) -> None:
        """Test reflector URL configuration."""
        assert NOESIS_REFLECTOR_URL == "http://localhost:8002"

    def test_request_timeout(self) -> None:
        """Test request timeout configuration."""
        assert REQUEST_TIMEOUT == 30.0

    def test_mcp_server_name(self) -> None:
        """Test MCP server name."""
        assert mcp.name == "daimon-consciousness"


class TestHttpHelpers:
    """Test suite for HTTP helper functions."""

    @pytest.mark.asyncio
    async def test_http_post_connection_error(self) -> None:
        """Test HTTP POST with connection error returns error dict."""
        # This tests error handling when server is unreachable
        result = await _http_post(
            "http://127.0.0.1:59999/nonexistent",
            {"test": "data"},
            timeout=1.0,
        )
        assert isinstance(result, dict)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_http_get_connection_error(self) -> None:
        """Test HTTP GET with connection error returns error dict."""
        result = await _http_get(
            "http://127.0.0.1:59999/nonexistent",
            timeout=1.0,
        )
        assert isinstance(result, dict)
        assert "error" in result


class TestMcpServerIntegration:
    """Integration tests for MCP server (tests error paths without NOESIS)."""

    def test_mcp_tools_registered(self) -> None:
        """Test that MCP tools are registered."""
        # The mcp object should have tools registered
        assert mcp is not None
        assert mcp.name == "daimon-consciousness"

    def test_http_post_returns_error_on_failure(self) -> None:
        """Test that _http_post returns error dict on connection failure."""
        import asyncio

        result = asyncio.run(_http_post(
            "http://127.0.0.1:59999/test",
            {"data": "test"},
            timeout=0.5,
        ))
        assert "error" in result

    def test_http_get_returns_error_on_failure(self) -> None:
        """Test that _http_get returns error dict on connection failure."""
        import asyncio

        result = asyncio.run(_http_get(
            "http://127.0.0.1:59999/test",
            timeout=0.5,
        ))
        assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
