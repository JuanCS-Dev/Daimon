"""
DAIMON Quick-Check Tests
========================

Unit tests for the quick-check endpoint.

Follows CODE_CONSTITUTION: Measurable Quality.
"""

from __future__ import annotations

import pytest

from endpoints.quick_check import (
    analyze_prompt,
    QuickCheckRequest,
    QuickCheckResponse,
    create_quick_check_endpoint,
)
from endpoints.constants import HIGH_RISK_KEYWORDS, MEDIUM_RISK_KEYWORDS


class TestQuickCheck:
    """Test suite for quick-check analysis."""

    def test_high_risk_delete(self) -> None:
        """Test high-risk keyword: delete."""
        result = analyze_prompt("Delete all user records")
        assert result.salience >= 0.85
        assert result.should_emerge is True
        assert result.mode == "emerge"
        assert "delete" in result.detected_keywords

    def test_high_risk_production(self) -> None:
        """Test high-risk keyword: production."""
        result = analyze_prompt("Deploy to production")
        assert result.salience >= 0.85
        assert result.should_emerge is True

    def test_high_risk_rm_rf(self) -> None:
        """Test high-risk keyword: rm -rf."""
        result = analyze_prompt("Run rm -rf on the directory")
        assert result.salience >= 0.85
        assert result.should_emerge is True

    def test_medium_risk_refactor(self) -> None:
        """Test medium-risk keyword: refactor."""
        result = analyze_prompt("Refactor the authentication module")
        assert 0.5 <= result.salience < 0.85
        assert result.should_emerge is False
        assert result.mode == "subtle"

    def test_medium_risk_migrate(self) -> None:
        """Test medium-risk keyword: migrate."""
        result = analyze_prompt("Migrate the database schema")
        assert 0.5 <= result.salience < 0.85
        assert result.mode == "subtle"

    def test_low_risk_normal_prompt(self) -> None:
        """Test low-risk normal prompt."""
        result = analyze_prompt("Add a new function to calculate sum")
        assert result.salience < 0.5
        assert result.should_emerge is False
        assert result.mode == "silent"

    def test_empty_prompt(self) -> None:
        """Test empty prompt returns low salience."""
        result = analyze_prompt("")
        assert result.salience == 0.1
        assert result.mode == "silent"

    def test_case_insensitive(self) -> None:
        """Test keyword detection is case insensitive."""
        result = analyze_prompt("DELETE ALL USERS")
        assert result.salience >= 0.85

    def test_multiple_keywords(self) -> None:
        """Test multiple keywords detected."""
        result = analyze_prompt("Delete the production database and drop tables")
        assert len(result.detected_keywords) >= 2


class TestConstants:
    """Test suite for constants module."""

    def test_high_risk_keywords_populated(self) -> None:
        """Test that high risk keywords list is populated."""
        assert len(HIGH_RISK_KEYWORDS) > 0
        assert "delete" in HIGH_RISK_KEYWORDS
        assert "production" in HIGH_RISK_KEYWORDS

    def test_medium_risk_keywords_populated(self) -> None:
        """Test that medium risk keywords list is populated."""
        assert len(MEDIUM_RISK_KEYWORDS) > 0
        assert "refactor" in MEDIUM_RISK_KEYWORDS
        assert "migrate" in MEDIUM_RISK_KEYWORDS


class TestQuickCheckRequest:
    """Test suite for QuickCheckRequest model."""

    def test_valid_request(self) -> None:
        """Test creating a valid request."""
        request = QuickCheckRequest(prompt="Test prompt")
        assert request.prompt == "Test prompt"


class TestQuickCheckResponse:
    """Test suite for QuickCheckResponse model."""

    def test_create_response(self) -> None:
        """Test creating a response."""
        response = QuickCheckResponse(
            salience=0.9,
            should_emerge=True,
            mode="emerge",
            emergence_reason="Test reason",
            detected_keywords=["delete"],
        )
        assert response.salience == 0.9
        assert response.should_emerge is True

    def test_response_defaults(self) -> None:
        """Test response default values."""
        response = QuickCheckResponse(
            salience=0.1,
            should_emerge=False,
            mode="silent",
        )
        assert response.emergence_reason is None
        assert response.detected_keywords == []


class TestCreateQuickCheckEndpoint:
    """Test suite for endpoint factory."""

    @pytest.mark.asyncio
    async def test_create_endpoint(self) -> None:
        """Test creating the endpoint handler."""
        handler = create_quick_check_endpoint()
        request = QuickCheckRequest(prompt="delete all data")
        result = await handler(request)
        assert result.salience >= 0.85
        assert result.should_emerge is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
