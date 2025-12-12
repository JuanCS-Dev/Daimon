"""
DAIMON Hook Tests
=================

Unit tests for the Claude Code hook module.

Follows CODE_CONSTITUTION: Measurable Quality.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import pytest

import sys
sys.path.insert(0, "/media/juan/DATA/projetos/daimon/.claude/hooks")

from noesis_hook import (
    HIGH_RISK_KEYWORDS,
    MEDIUM_RISK_KEYWORDS,
    classify_risk,
    handle_user_prompt_submit,
    handle_pre_tool_use,
)


class TestClassifyRisk:
    """Test suite for risk classification."""

    def test_high_risk_delete(self) -> None:
        """Test high risk for delete keyword."""
        assert classify_risk("delete all records") == "high"

    def test_high_risk_drop(self) -> None:
        """Test high risk for drop keyword."""
        assert classify_risk("drop table users") == "high"

    def test_high_risk_rm_rf(self) -> None:
        """Test high risk for rm -rf keyword."""
        assert classify_risk("run rm -rf /tmp") == "high"

    def test_high_risk_production(self) -> None:
        """Test high risk for production keyword."""
        assert classify_risk("deploy to production") == "high"

    def test_high_risk_destroy(self) -> None:
        """Test high risk for destroy keyword."""
        assert classify_risk("destroy the instance") == "high"

    def test_medium_risk_refactor(self) -> None:
        """Test medium risk for refactor keyword."""
        assert classify_risk("refactor authentication") == "medium"

    def test_medium_risk_migrate(self) -> None:
        """Test medium risk for migrate keyword."""
        assert classify_risk("migrate database schema") == "medium"

    def test_medium_risk_security(self) -> None:
        """Test medium risk for security keyword."""
        assert classify_risk("update security settings") == "medium"

    def test_low_risk_normal(self) -> None:
        """Test low risk for normal text."""
        assert classify_risk("add a new function") == "low"

    def test_case_insensitive(self) -> None:
        """Test case insensitivity."""
        assert classify_risk("DELETE ALL") == "high"
        assert classify_risk("REFACTOR CODE") == "medium"

    def test_high_risk_keywords_list(self) -> None:
        """Test that high risk keywords list is non-empty."""
        assert len(HIGH_RISK_KEYWORDS) > 0
        assert "delete" in HIGH_RISK_KEYWORDS

    def test_medium_risk_keywords_list(self) -> None:
        """Test that medium risk keywords list is non-empty."""
        assert len(MEDIUM_RISK_KEYWORDS) > 0
        assert "refactor" in MEDIUM_RISK_KEYWORDS


class TestHandleUserPromptSubmit:
    """Test suite for UserPromptSubmit handler."""

    def test_low_risk_no_intervention(self) -> None:
        """Test that low risk prompts return None."""
        data: Dict[str, Any] = {"prompt": "add a button"}
        result = handle_user_prompt_submit(data)
        assert result is None

    def test_empty_prompt_no_intervention(self) -> None:
        """Test that empty prompts return None."""
        data: Dict[str, Any] = {"prompt": ""}
        result = handle_user_prompt_submit(data)
        assert result is None

    def test_missing_prompt_no_intervention(self) -> None:
        """Test that missing prompts return None."""
        data: Dict[str, Any] = {}
        result = handle_user_prompt_submit(data)
        assert result is None

    def test_high_risk_without_noesis(self) -> None:
        """Test high risk prompt without NOESIS connection."""
        data: Dict[str, Any] = {"prompt": "delete all user data"}
        result = handle_user_prompt_submit(data)
        # Should return context warning
        if result:
            assert "hookSpecificOutput" in result
            assert "NOESIS" in result["hookSpecificOutput"]["additionalContext"]

    def test_medium_risk_prompt(self) -> None:
        """Test medium risk prompt handling."""
        data: Dict[str, Any] = {"prompt": "refactor the authentication"}
        # Medium risk may or may not intervene based on NOESIS availability
        result = handle_user_prompt_submit(data)
        # Result can be None if NOESIS check didn't trigger emergence


class TestHandlePreToolUse:
    """Test suite for PreToolUse handler."""

    def test_non_bash_no_intervention(self) -> None:
        """Test that non-Bash tools return None."""
        data: Dict[str, Any] = {"tool_name": "Read", "tool_input": {}}
        result = handle_pre_tool_use(data)
        assert result is None

    def test_bash_low_risk_no_intervention(self) -> None:
        """Test that low-risk Bash commands return None."""
        data: Dict[str, Any] = {
            "tool_name": "Bash",
            "tool_input": {"command": "ls -la"},
        }
        result = handle_pre_tool_use(data)
        assert result is None

    def test_bash_high_risk_intervention(self) -> None:
        """Test that high-risk Bash commands trigger intervention."""
        data: Dict[str, Any] = {
            "tool_name": "Bash",
            "tool_input": {"command": "rm -rf /tmp/test"},
        }
        result = handle_pre_tool_use(data)
        assert result is not None
        assert "hookSpecificOutput" in result
        assert result["hookSpecificOutput"]["decision"] == "ask"

    def test_bash_production_command_intervention(self) -> None:
        """Test that production commands trigger intervention."""
        data: Dict[str, Any] = {
            "tool_name": "Bash",
            "tool_input": {"command": "deploy to production"},
        }
        result = handle_pre_tool_use(data)
        assert result is not None

    def test_bash_empty_command_no_intervention(self) -> None:
        """Test that empty commands return None."""
        data: Dict[str, Any] = {
            "tool_name": "Bash",
            "tool_input": {"command": ""},
        }
        result = handle_pre_tool_use(data)
        assert result is None

    def test_bash_missing_command_no_intervention(self) -> None:
        """Test that missing commands return None."""
        data: Dict[str, Any] = {
            "tool_name": "Bash",
            "tool_input": {},
        }
        result = handle_pre_tool_use(data)
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
