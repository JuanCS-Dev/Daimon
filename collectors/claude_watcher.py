#!/usr/bin/env python3
"""
DAIMON Claude Code Watcher - Session Intent Capture
====================================================

Monitors Claude Code sessions and extracts intention metadata.
Captures INTENT, not content - respects privacy.

Usage:
    python claude_watcher.py --daemon

Follows CODE_CONSTITUTION: Clarity Over Cleverness, Safety First.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Configuration
NOESIS_URL = os.getenv("NOESIS_URL", "http://localhost:8001")
CLAUDE_DIR = Path.home() / ".claude" / "projects"
POLL_INTERVAL_SECONDS = 5

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("daimon-claude")

# Intent detection patterns (match user messages, not content)
INTENT_PATTERNS: Dict[str, List[str]] = {
    "create": ["create", "add", "implement", "build", "make", "generate", "write"],
    "fix": ["fix", "bug", "error", "broken", "issue", "problem", "crash"],
    "refactor": ["refactor", "clean", "reorganize", "restructure", "improve"],
    "understand": ["explain", "what", "how", "why", "understand", "help me"],
    "delete": ["delete", "remove", "drop", "destroy", "clean up"],
    "test": ["test", "verify", "check", "validate", "coverage"],
    "deploy": ["deploy", "release", "production", "publish", "ship"],
}


def detect_intention(message: str) -> str:
    """
    Detect intention category from message.

    Args:
        message: User message text.

    Returns:
        Intent category or "unknown".
    """
    message_lower = message.lower()

    for intent, keywords in INTENT_PATTERNS.items():
        for keyword in keywords:
            if keyword in message_lower:
                return intent

    return "unknown"


def extract_files_touched(message: str) -> List[str]:
    """
    Extract file paths mentioned in message.

    Only extracts paths, not content.

    Args:
        message: Message text.

    Returns:
        List of file paths found.
    """
    # Match common file path patterns
    patterns = [
        r'[\'"`]([^\'"`]+\.[a-zA-Z]{2,4})[\'"`]',  # Quoted paths with extension
        r'(\S+\.[a-zA-Z]{2,4})\b',  # Unquoted paths with extension
    ]

    files: List[str] = []
    for pattern in patterns:
        matches = re.findall(pattern, message)
        files.extend(matches)

    # Deduplicate and filter
    return list(set(f for f in files if "/" in f or "." in f))[:10]


class SessionTracker:  # pylint: disable=too-few-public-methods
    """
    Tracks Claude Code session state.

    Monitors JSONL files for new messages and extracts metadata.

    Note: Single public method (scan_projects) is the intended API.
    Internal methods handle the actual processing.
    """

    def __init__(self) -> None:
        """Initialize tracker with empty state."""
        self.positions: Dict[Path, int] = {}
        self.session_events: List[Dict[str, Any]] = []

    async def scan_projects(self) -> None:
        """
        Scan all project directories for session files.

        Monitors ~/.claude/projects/*/sessions/*.jsonl.
        """
        if not CLAUDE_DIR.exists():
            logger.debug("Claude directory not found: %s", CLAUDE_DIR)
            return

        for project_dir in CLAUDE_DIR.iterdir():
            if not project_dir.is_dir():
                continue

            sessions_dir = project_dir / "sessions"
            if not sessions_dir.exists():
                continue

            for jsonl_file in sessions_dir.glob("*.jsonl"):
                await self._process_file(jsonl_file, project_dir.name)

    async def _process_file(self, file_path: Path, project: str) -> None:
        """
        Process JSONL file for new messages.

        Args:
            file_path: Path to JSONL file.
            project: Project identifier.
        """
        # Get current position
        current_pos = self.positions.get(file_path, 0)

        try:
            file_size = file_path.stat().st_size
            if file_size <= current_pos:
                return

            with open(file_path, "r", encoding="utf-8") as f:
                f.seek(current_pos)
                new_lines = f.readlines()
                self.positions[file_path] = f.tell()

            for line in new_lines:
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)
                    await self._process_entry(entry, project)
                except json.JSONDecodeError:
                    continue

        except (IOError, OSError) as exc:
            logger.warning("Error reading %s: %s", file_path, exc)

    async def _process_entry(self, entry: Dict[str, Any], project: str) -> None:
        """
        Process single JSONL entry.

        Extracts metadata without capturing content.

        Args:
            entry: Parsed JSON entry.
            project: Project identifier.
        """
        # Only process user messages
        role = entry.get("role", "")
        if role != "user":
            return

        # Extract content for intent detection (then discard content)
        content = entry.get("content", "")
        if not content:
            return

        # Detect intention
        intention = detect_intention(content)
        files_touched = extract_files_touched(content)

        # Create event (no content stored)
        event = {
            "event_type": intention,
            "timestamp": datetime.now().isoformat(),
            "project": project,
            "files_touched": files_touched,
            "intention": intention,
        }

        self.session_events.append(event)
        logger.debug("Session event: %s (%s)", intention, project)

        # Send to NOESIS
        await self._send_event(event)

    async def _send_event(self, event: Dict[str, Any]) -> None:
        """
        Send event to NOESIS.

        Args:
            event: Event metadata to send.
        """
        try:
            import httpx  # pylint: disable=import-outside-toplevel

            async with httpx.AsyncClient(timeout=2.0) as client:
                await client.post(
                    f"{NOESIS_URL}/api/daimon/claude/event",
                    json=event,
                )
        except ImportError:
            logger.debug("httpx not available")
        except Exception as exc:  # pylint: disable=broad-except
            logger.debug("Failed to send event: %s", exc)


async def run_daemon() -> None:
    """
    Run the watcher daemon.

    Polls Claude session files at regular intervals.
    """
    tracker = SessionTracker()
    logger.info("DAIMON Claude Watcher started")
    logger.info("Monitoring: %s", CLAUDE_DIR)

    try:
        while True:
            await tracker.scan_projects()
            await asyncio.sleep(POLL_INTERVAL_SECONDS)
    except asyncio.CancelledError:
        logger.info("DAIMON Claude Watcher stopped")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="DAIMON Claude Code Watcher")
    parser.add_argument("--daemon", action="store_true", help="Start daemon mode")
    args = parser.parse_args()

    if args.daemon:
        try:
            asyncio.run(run_daemon())
        except KeyboardInterrupt:
            logger.info("DAIMON Claude Watcher stopped")
        return

    # Default: show usage
    parser.print_help()


if __name__ == "__main__":
    main()
