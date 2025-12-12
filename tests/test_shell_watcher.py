"""
DAIMON Shell Watcher Tests
==========================

Unit tests for the shell watcher module.

Follows CODE_CONSTITUTION: Measurable Quality.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List

import pytest

from collectors.shell_watcher import (
    HeartbeatAggregator,
    ShellHeartbeat,
    generate_zshrc_hooks,
    get_aggregator,
)


class TestShellHeartbeat:
    """Test suite for ShellHeartbeat dataclass."""

    def test_create_heartbeat(self) -> None:
        """Test creating a heartbeat with all fields."""
        hb = ShellHeartbeat(
            timestamp="2025-12-12T10:00:00",
            command="ls -la",
            pwd="/home/user",
            exit_code=0,
            duration=0.5,
            git_branch="main",
        )
        assert hb.command == "ls -la"
        assert hb.exit_code == 0
        assert hb.duration == 0.5
        assert hb.git_branch == "main"

    def test_create_heartbeat_defaults(self) -> None:
        """Test creating a heartbeat with default values."""
        hb = ShellHeartbeat(
            timestamp="2025-12-12T10:00:00",
            command="pwd",
            pwd="/home",
            exit_code=0,
        )
        assert hb.duration == 0.0
        assert hb.git_branch == ""

    def test_from_json(self) -> None:
        """Test creating heartbeat from JSON dict."""
        data: Dict[str, Any] = {
            "timestamp": "2025-12-12T10:00:00",
            "command": "git status",
            "pwd": "/project",
            "exit_code": 0,
            "duration": 0.1,
            "git_branch": "feature",
        }
        hb = ShellHeartbeat.from_json(data)
        assert hb.command == "git status"
        assert hb.git_branch == "feature"

    def test_from_json_missing_fields(self) -> None:
        """Test creating heartbeat from JSON with missing fields."""
        data: Dict[str, Any] = {
            "command": "echo test",
            "pwd": "/tmp",
        }
        hb = ShellHeartbeat.from_json(data)
        assert hb.command == "echo test"
        assert hb.exit_code == 0
        assert hb.duration == 0.0

    def test_from_json_string_exit_code(self) -> None:
        """Test that string exit code is converted to int."""
        data: Dict[str, Any] = {
            "command": "fail",
            "pwd": "/tmp",
            "exit_code": "1",
        }
        hb = ShellHeartbeat.from_json(data)
        assert hb.exit_code == 1


class TestHeartbeatAggregator:
    """Test suite for HeartbeatAggregator."""

    def test_add_heartbeat(self) -> None:
        """Test adding a heartbeat to the aggregator."""
        agg = HeartbeatAggregator()
        hb = ShellHeartbeat(
            timestamp="2025-12-12T10:00:00",
            command="ls",
            pwd="/home",
            exit_code=0,
        )
        agg.add(hb)
        assert len(agg.pending) == 1

    def test_trim_pending_when_max_exceeded(self) -> None:
        """Test that pending list is trimmed when exceeding max."""
        agg = HeartbeatAggregator()
        # Add more than MAX_PENDING_HEARTBEATS (100)
        for i in range(110):
            hb = ShellHeartbeat(
                timestamp=f"2025-12-12T10:00:{i:02d}",
                command=f"cmd{i}",
                pwd="/home",
                exit_code=0,
            )
            agg.pending.append(hb)

        # Add one more through the normal method
        final_hb = ShellHeartbeat(
            timestamp="2025-12-12T11:00:00",
            command="final",
            pwd="/home",
            exit_code=0,
        )
        agg.add(final_hb)

        # Should be trimmed to last 100
        assert len(agg.pending) <= 101  # MAX + 1 before next trim

    def test_should_flush_time_based(self) -> None:
        """Test flush trigger based on time interval."""
        agg = HeartbeatAggregator()
        agg.last_flush = datetime.now() - timedelta(seconds=60)

        hb = ShellHeartbeat(
            timestamp="2025-12-12T10:00:00",
            command="ls",
            pwd="/home",
            exit_code=0,
        )

        assert agg._should_flush(hb) is True

    def test_should_flush_significant_command(self) -> None:
        """Test flush trigger for significant commands."""
        agg = HeartbeatAggregator()

        # git push should trigger flush
        hb = ShellHeartbeat(
            timestamp="2025-12-12T10:00:00",
            command="git push origin main",
            pwd="/project",
            exit_code=0,
        )

        assert agg._should_flush(hb) is True

    def test_should_not_flush_normal_command(self) -> None:
        """Test that normal commands don't trigger flush."""
        agg = HeartbeatAggregator()

        hb = ShellHeartbeat(
            timestamp="2025-12-12T10:00:00",
            command="ls -la",
            pwd="/home",
            exit_code=0,
        )

        assert agg._should_flush(hb) is False

    def test_detect_patterns_error_streak(self) -> None:
        """Test frustration detection from error streak."""
        agg = HeartbeatAggregator()

        batch: List[ShellHeartbeat] = [
            ShellHeartbeat(
                timestamp=f"2025-12-12T10:00:{i:02d}",
                command=f"cmd{i}",
                pwd="/home",
                exit_code=1,  # All errors
            )
            for i in range(5)
        ]

        patterns = agg._detect_patterns(batch)
        assert patterns.get("possible_frustration") is True
        assert patterns.get("error_streak") == 5

    def test_detect_patterns_repetitive_command(self) -> None:
        """Test repetitive command detection."""
        agg = HeartbeatAggregator()

        batch: List[ShellHeartbeat] = [
            ShellHeartbeat(
                timestamp=f"2025-12-12T10:00:{i:02d}",
                command="npm test",  # Same command repeated
                pwd="/project",
                exit_code=0,
            )
            for i in range(5)
        ]

        patterns = agg._detect_patterns(batch)
        assert patterns.get("repetitive_command") == "npm test"

    def test_detect_patterns_no_patterns(self) -> None:
        """Test when no patterns are detected."""
        agg = HeartbeatAggregator()

        batch: List[ShellHeartbeat] = [
            ShellHeartbeat(
                timestamp="2025-12-12T10:00:00",
                command="ls",
                pwd="/home",
                exit_code=0,
            )
        ]

        patterns = agg._detect_patterns(batch)
        assert patterns == {}


class TestGetAggregator:
    """Test suite for singleton aggregator."""

    def test_get_aggregator_creates_instance(self) -> None:
        """Test that get_aggregator returns an instance."""
        agg = get_aggregator()
        assert isinstance(agg, HeartbeatAggregator)

    def test_get_aggregator_returns_same_instance(self) -> None:
        """Test that get_aggregator returns singleton."""
        agg1 = get_aggregator()
        agg2 = get_aggregator()
        assert agg1 is agg2


class TestGenerateZshrcHooks:
    """Test suite for zshrc hooks generation."""

    def test_generate_zshrc_hooks_content(self) -> None:
        """Test that generated hooks contain required functions."""
        hooks = generate_zshrc_hooks()

        # Should contain preexec and precmd functions
        assert "daimon_preexec" in hooks
        assert "daimon_precmd" in hooks

        # Should register hooks
        assert "add-zsh-hook preexec daimon_preexec" in hooks
        assert "add-zsh-hook precmd daimon_precmd" in hooks

        # Should reference socket
        assert ".daimon/daimon.sock" in hooks


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
