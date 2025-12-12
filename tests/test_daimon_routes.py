"""
DAIMON Routes Tests
===================

Unit tests for FastAPI routes.

Follows CODE_CONSTITUTION: Measurable Quality.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from endpoints.daimon_routes import router


# Create test app with the router
app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestQuickCheckEndpoint:
    """Test suite for /api/daimon/quick-check endpoint."""

    def test_high_risk_delete(self) -> None:
        """Test high-risk delete keyword detection."""
        response = client.post(
            "/api/daimon/quick-check",
            json={"prompt": "Delete all user records"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["salience"] >= 0.85
        assert data["should_emerge"] is True
        assert data["mode"] == "emerge"

    def test_medium_risk_refactor(self) -> None:
        """Test medium-risk refactor keyword detection."""
        response = client.post(
            "/api/daimon/quick-check",
            json={"prompt": "Refactor the authentication module"},
        )
        assert response.status_code == 200
        data = response.json()
        assert 0.5 <= data["salience"] < 0.85
        assert data["should_emerge"] is False
        assert data["mode"] == "subtle"

    def test_low_risk_normal(self) -> None:
        """Test low-risk normal prompt."""
        response = client.post(
            "/api/daimon/quick-check",
            json={"prompt": "Add a console.log statement"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["salience"] < 0.5
        assert data["should_emerge"] is False
        assert data["mode"] == "silent"


class TestShellBatchEndpoint:
    """Test suite for /api/daimon/shell/batch endpoint."""

    def test_receive_batch(self) -> None:
        """Test receiving a batch of heartbeats."""
        response = client.post(
            "/api/daimon/shell/batch",
            json={
                "heartbeats": [
                    {
                        "timestamp": "2025-12-12T10:00:00",
                        "command": "ls -la",
                        "pwd": "/home/user",
                        "exit_code": 0,
                    }
                ],
                "patterns": {},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["stored"] == 1

    def test_receive_batch_with_frustration(self) -> None:
        """Test receiving batch with frustration pattern."""
        response = client.post(
            "/api/daimon/shell/batch",
            json={
                "heartbeats": [
                    {
                        "timestamp": "2025-12-12T10:00:00",
                        "command": "npm test",
                        "pwd": "/project",
                        "exit_code": 1,
                    }
                    for _ in range(3)
                ],
                "patterns": {
                    "possible_frustration": True,
                    "error_streak": 3,
                },
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "Frustration detected" in data["insights"][0]

    def test_empty_batch(self) -> None:
        """Test receiving empty batch."""
        response = client.post(
            "/api/daimon/shell/batch",
            json={"heartbeats": [], "patterns": {}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["stored"] == 0


class TestClaudeEventEndpoint:
    """Test suite for /api/daimon/claude/event endpoint."""

    def test_receive_event(self) -> None:
        """Test receiving Claude event."""
        response = client.post(
            "/api/daimon/claude/event",
            json={
                "event_type": "create",
                "timestamp": "2025-12-12T10:00:00",
                "project": "test-project",
                "files_touched": ["main.py"],
                "intention": "create",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["stored"] is True


class TestSessionEndEndpoint:
    """Test suite for /api/daimon/session/end endpoint."""

    def test_session_end_simple(self) -> None:
        """Test simple session end."""
        response = client.post(
            "/api/daimon/session/end",
            json={
                "session_id": "test-session-123",
                "summary": "Fixed a bug",
                "outcome": "success",
                "duration_minutes": 10,
                "files_changed": 2,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["precedent_id"] is None  # Not significant

    def test_session_end_creates_precedent(self) -> None:
        """Test that significant session creates precedent."""
        response = client.post(
            "/api/daimon/session/end",
            json={
                "session_id": "significant-session",
                "summary": "Major refactoring",
                "outcome": "success",
                "duration_minutes": 60,  # Long session
                "files_changed": 10,  # Many files
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["precedent_id"] is not None
        assert data["precedent_id"].startswith("sess_")


class TestHealthEndpoint:
    """Test suite for /api/daimon/health endpoint."""

    def test_health_check(self) -> None:
        """Test health endpoint."""
        response = client.get("/api/daimon/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "daimon"
        assert len(data["endpoints"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
