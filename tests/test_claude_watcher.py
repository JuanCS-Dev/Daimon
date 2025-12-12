"""
DAIMON Claude Watcher Tests
===========================

Unit tests for the Claude Code watcher module.

Follows CODE_CONSTITUTION: Measurable Quality.
"""

from __future__ import annotations

import pytest

from collectors.claude_watcher import (
    INTENT_PATTERNS,
    detect_intention,
    extract_files_touched,
    SessionTracker,
)


class TestDetectIntention:
    """Test suite for intention detection."""

    def test_detect_create_intention(self) -> None:
        """Test detecting create intention."""
        assert detect_intention("Create a new component") == "create"
        assert detect_intention("Add authentication") == "create"
        assert detect_intention("implement the feature") == "create"

    def test_detect_fix_intention(self) -> None:
        """Test detecting fix intention."""
        assert detect_intention("Fix the bug") == "fix"
        assert detect_intention("There's an error here") == "fix"
        assert detect_intention("This is broken") == "fix"

    def test_detect_refactor_intention(self) -> None:
        """Test detecting refactor intention."""
        assert detect_intention("Refactor this module") == "refactor"
        assert detect_intention("Clean up the code") == "refactor"
        assert detect_intention("Reorganize the structure") == "refactor"

    def test_detect_understand_intention(self) -> None:
        """Test detecting understand intention."""
        assert detect_intention("Explain this function") == "understand"
        assert detect_intention("What does this do?") == "understand"
        assert detect_intention("How does this work?") == "understand"
        assert detect_intention("Help me with this") == "understand"

    def test_detect_delete_intention(self) -> None:
        """Test detecting delete intention."""
        assert detect_intention("Delete the old files") == "delete"
        assert detect_intention("Remove this function") == "delete"
        assert detect_intention("Drop the table") == "delete"

    def test_detect_test_intention(self) -> None:
        """Test detecting test intention."""
        assert detect_intention("Test this endpoint") == "test"
        assert detect_intention("Verify the output") == "test"
        assert detect_intention("Check the coverage") == "test"

    def test_detect_deploy_intention(self) -> None:
        """Test detecting deploy intention."""
        assert detect_intention("Deploy to production") == "deploy"
        assert detect_intention("Release the new version") == "deploy"
        assert detect_intention("Ship this feature") == "deploy"

    def test_detect_unknown_intention(self) -> None:
        """Test unknown intention fallback."""
        assert detect_intention("Let's do something") == "unknown"
        assert detect_intention("Random text here") == "unknown"

    def test_case_insensitive(self) -> None:
        """Test case insensitivity."""
        assert detect_intention("CREATE A NEW FILE") == "create"
        assert detect_intention("FIX THE BUG") == "fix"

    def test_intent_patterns_exist(self) -> None:
        """Test that all expected intent patterns exist."""
        expected_intents = ["create", "fix", "refactor", "understand", "delete", "test", "deploy"]
        for intent in expected_intents:
            assert intent in INTENT_PATTERNS


class TestExtractFilesTouched:
    """Test suite for file path extraction."""

    def test_extract_quoted_paths(self) -> None:
        """Test extracting quoted file paths."""
        files = extract_files_touched('Edit the file "src/main.py"')
        assert "src/main.py" in files

    def test_extract_unquoted_paths(self) -> None:
        """Test extracting unquoted file paths."""
        files = extract_files_touched("Check components/App.tsx for errors")
        assert "components/App.tsx" in files

    def test_extract_multiple_paths(self) -> None:
        """Test extracting multiple file paths."""
        files = extract_files_touched("Compare config.json and settings.yaml")
        assert any("config.json" in f for f in files)
        assert any("settings.yaml" in f for f in files)

    def test_limit_extracted_files(self) -> None:
        """Test that extracted files are limited to 10."""
        # Create message with many file references
        many_files = " ".join([f"file{i}.py" for i in range(20)])
        files = extract_files_touched(many_files)
        assert len(files) <= 10

    def test_no_files_found(self) -> None:
        """Test when no files are found."""
        files = extract_files_touched("Just regular text without files")
        assert len(files) == 0

    def test_deduplicate_files(self) -> None:
        """Test that duplicate files are removed."""
        files = extract_files_touched("Edit main.py and then main.py again")
        # Count occurrences of main.py
        main_count = sum(1 for f in files if "main.py" in f)
        assert main_count == 1


class TestSessionTracker:
    """Test suite for SessionTracker class."""

    def test_init(self) -> None:
        """Test SessionTracker initialization."""
        tracker = SessionTracker()
        assert tracker.positions == {}
        assert tracker.session_events == []

    @pytest.mark.asyncio
    async def test_scan_projects_no_directory(self) -> None:
        """Test scanning when claude directory doesn't exist."""
        tracker = SessionTracker()
        # Should not raise, just return
        await tracker.scan_projects()
        # No events should be captured
        assert tracker.session_events == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
