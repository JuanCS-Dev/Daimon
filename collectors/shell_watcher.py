#!/usr/bin/env python3
"""
DAIMON Shell Watcher - Heartbeat Pattern Command Capture
========================================================

Captures shell commands using heartbeat pattern (ActivityWatch style).
States that merge, not isolated events.

Usage:
    # Start daemon
    python shell_watcher.py --daemon

    # Generate zshrc hooks
    python shell_watcher.py --zshrc >> ~/.zshrc

Follows CODE_CONSTITUTION: Clarity Over Cleverness, Safety First.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

# Configuration
NOESIS_URL = os.getenv("NOESIS_URL", "http://localhost:8001")
BATCH_INTERVAL_SECONDS = 30
SOCKET_DIR = Path.home() / ".daimon"
SOCKET_PATH = SOCKET_DIR / "daimon.sock"
MAX_PENDING_HEARTBEATS = 100

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("daimon-shell")


@dataclass
class ShellHeartbeat:
    """
    Single shell command heartbeat.

    Attributes:
        timestamp: ISO format timestamp.
        command: Shell command executed.
        pwd: Working directory at execution time.
        exit_code: Command exit code (0 = success).
        duration: Execution duration in seconds.
        git_branch: Current git branch if in repository.
    """

    timestamp: str
    command: str
    pwd: str
    exit_code: int
    duration: float = 0.0
    git_branch: str = ""

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ShellHeartbeat":
        """Create heartbeat from JSON dict."""
        return cls(
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            command=data.get("command", ""),
            pwd=data.get("pwd", ""),
            exit_code=int(data.get("exit_code", 0)),
            duration=float(data.get("duration", 0.0)),
            git_branch=data.get("git_branch", ""),
        )


@dataclass
class HeartbeatAggregator:
    """
    Aggregates heartbeats and flushes to NOESIS in batches.

    Follows heartbeat pattern: states that merge, not isolated events.
    """

    pending: List[ShellHeartbeat] = field(default_factory=list)
    last_flush: datetime = field(default_factory=datetime.now)

    def add(self, heartbeat: ShellHeartbeat) -> None:
        """
        Add heartbeat to pending list.

        Auto-flushes if conditions met (time interval or significant command).

        Args:
            heartbeat: The heartbeat to add.
        """
        self.pending.append(heartbeat)

        # Trim if too many pending
        if len(self.pending) > MAX_PENDING_HEARTBEATS:
            self.pending = self.pending[-MAX_PENDING_HEARTBEATS:]

        # Check if should flush
        if self._should_flush(heartbeat):
            asyncio.create_task(self.flush())

    def _should_flush(self, heartbeat: ShellHeartbeat) -> bool:
        """
        Determine if should flush based on time or significance.

        Args:
            heartbeat: The latest heartbeat.

        Returns:
            True if should flush.
        """
        # Time-based flush
        if datetime.now() - self.last_flush > timedelta(seconds=BATCH_INTERVAL_SECONDS):
            return True

        # Significance-based flush
        significant_patterns = ["git push", "git commit", "rm ", "docker", "kubectl"]
        cmd_lower = heartbeat.command.lower()
        return any(pattern in cmd_lower for pattern in significant_patterns)

    async def flush(self) -> None:
        """
        Flush pending heartbeats to NOESIS.

        Detects patterns and sends batch to /api/daimon/shell/batch.
        """
        if not self.pending:
            return

        batch = self.pending.copy()
        self.pending.clear()
        self.last_flush = datetime.now()

        patterns = self._detect_patterns(batch)

        try:
            import httpx  # pylint: disable=import-outside-toplevel

            async with httpx.AsyncClient(timeout=2.0) as client:
                await client.post(
                    f"{NOESIS_URL}/api/daimon/shell/batch",
                    json={
                        "heartbeats": [asdict(h) for h in batch],
                        "patterns": patterns,
                    },
                )
                logger.debug("Flushed %d heartbeats to NOESIS", len(batch))
        except ImportError:
            logger.warning("httpx not available, heartbeats not sent")
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Failed to flush heartbeats: %s", exc)

    def _detect_patterns(self, batch: List[ShellHeartbeat]) -> Dict[str, Any]:
        """
        Detect behavioral patterns from heartbeat batch.

        Args:
            batch: List of heartbeats to analyze.

        Returns:
            Dict of detected patterns.
        """
        patterns: Dict[str, Any] = {}

        # Error streak detection
        errors = sum(1 for h in batch if h.exit_code != 0)
        if errors >= 3:
            patterns["error_streak"] = errors
            patterns["possible_frustration"] = True

        # Repetition detection (same command multiple times)
        commands = [h.command for h in batch]
        if len(commands) >= 3:
            for cmd in set(commands):
                if commands.count(cmd) >= 3:
                    patterns["repetitive_command"] = cmd
                    break

        return patterns


# Module-level state container (avoids global statement)
_state: Dict[str, HeartbeatAggregator] = {}


def get_aggregator() -> HeartbeatAggregator:
    """Get or create the singleton aggregator."""
    if "aggregator" not in _state:
        _state["aggregator"] = HeartbeatAggregator()
    return _state["aggregator"]


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    """
    Handle incoming socket connection.

    Reads JSON heartbeat data and adds to aggregator.

    Args:
        reader: Stream reader.
        writer: Stream writer.
    """
    try:
        data = await reader.read(4096)
        if data:
            json_data = json.loads(data.decode("utf-8"))
            heartbeat = ShellHeartbeat.from_json(json_data)
            get_aggregator().add(heartbeat)
            logger.debug("Received: %s", heartbeat.command[:50])
    except json.JSONDecodeError:
        logger.warning("Invalid JSON received")
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning("Client error: %s", exc)
    finally:
        writer.close()
        await writer.wait_closed()


async def start_server() -> None:
    """
    Start Unix socket server for receiving heartbeats.

    Creates socket at ~/.daimon/daimon.sock.
    """
    # Ensure directory exists
    SOCKET_DIR.mkdir(parents=True, exist_ok=True)

    # Remove old socket if exists
    if SOCKET_PATH.exists():
        SOCKET_PATH.unlink()

    server = await asyncio.start_unix_server(handle_client, path=str(SOCKET_PATH))
    logger.info("DAIMON Shell Watcher started: %s", SOCKET_PATH)

    async with server:
        await server.serve_forever()


def generate_zshrc_hooks() -> str:
    """
    Generate zshrc hooks for shell command capture.

    Returns:
        Shell script to append to ~/.zshrc.
    """
    return '''
# ============================================================================
# DAIMON Shell Watcher Hooks
# ============================================================================

# Capture command before execution
daimon_preexec() {
    DAIMON_CMD_START=$(date +%s.%N)
    DAIMON_CMD="$1"
}

# Capture command after execution
daimon_precmd() {
    local exit_code=$?
    local end_time=$(date +%s.%N)

    # Skip if no command recorded
    [[ -z "$DAIMON_CMD" ]] && return

    # Calculate duration
    local duration=$(echo "$end_time - ${DAIMON_CMD_START:-$end_time}" | bc 2>/dev/null || echo "0")

    # Get git branch if in repo
    local git_branch=""
    if git rev-parse --git-dir > /dev/null 2>&1; then
        git_branch=$(git branch --show-current 2>/dev/null || echo "")
    fi

    # Send to DAIMON socket (non-blocking)
    if [[ -S "$HOME/.daimon/daimon.sock" ]]; then
        (
            echo "{
                \\"timestamp\\": \\"$(date -Iseconds)\\",
                \\"command\\": \\"${DAIMON_CMD//\\"/\\\\\\"}\\" ,
                \\"pwd\\": \\"$PWD\\",
                \\"exit_code\\": $exit_code,
                \\"duration\\": $duration,
                \\"git_branch\\": \\"$git_branch\\"
            }" | nc -U "$HOME/.daimon/daimon.sock" 2>/dev/null &
        ) &!
    fi

    unset DAIMON_CMD
}

# Register hooks
autoload -Uz add-zsh-hook
add-zsh-hook preexec daimon_preexec
add-zsh-hook precmd daimon_precmd

# ============================================================================
'''


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="DAIMON Shell Watcher")
    parser.add_argument("--daemon", action="store_true", help="Start daemon mode")
    parser.add_argument("--zshrc", action="store_true", help="Output zshrc hooks")
    args = parser.parse_args()

    if args.zshrc:
        print(generate_zshrc_hooks())
        return

    if args.daemon:
        try:
            asyncio.run(start_server())
        except KeyboardInterrupt:
            logger.info("DAIMON Shell Watcher stopped")
        return

    # Default: show usage
    parser.print_help()


if __name__ == "__main__":
    main()
