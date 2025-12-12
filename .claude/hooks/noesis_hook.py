#!/usr/bin/env python3
"""
DAIMON Hook - Claude Code Integration
=====================================

Low-latency (<500ms) hook for Claude Code events.
Intercepts prompts and tool uses to provide NOESIS guidance.

Follows CODE_CONSTITUTION: Clarity Over Cleverness, Safety First.

Note: This hook is self-contained for portability (runs via Claude Code directly).
Keywords intentionally duplicated from endpoints/constants.py.
"""
# pylint: disable=duplicate-code

from __future__ import annotations

import json
import logging
import sys
from typing import Any, Dict, List, Optional

# Logging setup (stderr to not interfere with stdout JSON)
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("daimon-hook")

# Configuration
NOESIS_URL = "http://localhost:8001"
QUICK_CHECK_TIMEOUT = 0.5  # 500ms max

# Risk keywords (CODE_CONSTITUTION: Explicit, not clever)
HIGH_RISK_KEYWORDS: List[str] = [
    "delete",
    "drop",
    "rm -rf",
    "truncate",
    "production",
    "destroy",
    "wipe",
    "purge",
]

MEDIUM_RISK_KEYWORDS: List[str] = [
    "refactor",
    "migrate",
    "architecture",
    "auth",
    "security",
    "payment",
    "credential",
    "deploy",
]


def classify_risk(text: str) -> str:
    """
    Classify risk level of a text based on keywords.

    Args:
        text: The text to analyze (prompt or command).

    Returns:
        Risk level: "high", "medium", or "low".
    """
    text_lower = text.lower()

    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in text_lower:
            return "high"

    for keyword in MEDIUM_RISK_KEYWORDS:
        if keyword in text_lower:
            return "medium"

    return "low"


def quick_check(prompt: str) -> Optional[Dict[str, Any]]:
    """
    Fast heuristic check for NOESIS guidance.

    Makes HTTP request to NOESIS quick-check endpoint with strict timeout.
    Falls back to None if service unavailable.

    Args:
        prompt: The user prompt to check.

    Returns:
        Response dict with salience/should_emerge, or None if unavailable.
    """
    try:
        import httpx  # pylint: disable=import-outside-toplevel

        with httpx.Client(timeout=QUICK_CHECK_TIMEOUT) as client:
            response = client.post(
                f"{NOESIS_URL}/api/consciousness/quick-check",
                json={"prompt": prompt},
            )
            response.raise_for_status()
            result: Dict[str, Any] = response.json()
            return result
    except ImportError:
        logger.debug("httpx not available, skipping quick-check")
        return None
    except Exception as exc:  # pylint: disable=broad-except
        logger.debug("Quick-check failed: %s", exc)
        return None


def handle_user_prompt_submit(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Handle UserPromptSubmit event.

    Analyzes user prompt for risk and optionally adds NOESIS context.

    Args:
        data: Event data from Claude Code.

    Returns:
        Hook output dict if intervention needed, None otherwise.
    """
    prompt = data.get("prompt", "")
    if not prompt:
        return None

    risk = classify_risk(prompt)

    # Only intervene on high/medium risk
    if risk == "low":
        return None

    # Try NOESIS quick-check
    check = quick_check(prompt)

    if check and check.get("should_emerge"):
        reason = check.get("emergence_reason", "Significant action detected")
        return {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": f"NOESIS: {reason}",
            }
        }

    # Fallback for high risk without NOESIS
    if risk == "high" and not check:
        return {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": "NOESIS: High-risk keywords detected. Consider using noesis_tribunal.",
            }
        }

    return None


def handle_pre_tool_use(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Handle PreToolUse event.

    Intercepts tool uses, particularly Bash commands, to flag destructive operations.

    Args:
        data: Event data from Claude Code.

    Returns:
        Hook output dict if intervention needed, None otherwise.
    """
    tool_name = data.get("tool_name", "")

    # Only intercept Bash for now
    if tool_name != "Bash":
        return None

    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "")

    if not command:
        return None

    risk = classify_risk(command)

    if risk == "high":
        # Request user confirmation for destructive commands
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "decision": "ask",
                "reason": "NOESIS: Destructive command detected. Confirm execution.",
            }
        }

    return None


def main() -> None:
    """
    Main entry point for the hook.

    Reads JSON from stdin, processes the event, outputs JSON to stdout.
    Exit code 0 indicates success (Claude Code requirement).
    """
    try:
        # Read input from stdin
        raw_input = sys.stdin.read()
        if not raw_input.strip():
            sys.exit(0)

        data = json.loads(raw_input)
        event = data.get("hook_event_name", "")

        result: Optional[Dict[str, Any]] = None

        if event == "UserPromptSubmit":
            result = handle_user_prompt_submit(data)
        elif event == "PreToolUse":
            result = handle_pre_tool_use(data)

        # Output result if any
        if result:
            print(json.dumps(result))

    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON input: %s", exc)
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Hook error: %s", exc)

    # Always exit 0 (Claude Code requirement)
    sys.exit(0)


if __name__ == "__main__":
    main()
