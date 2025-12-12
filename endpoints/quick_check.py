"""
DAIMON Quick-Check Endpoint
===========================

Fast heuristic endpoint (<100ms target) for hook integration.
Analyzes prompts for risk/salience without full consciousness processing.

Follows CODE_CONSTITUTION: Clarity Over Cleverness, Safety First.
"""
# pylint: disable=duplicate-code

from __future__ import annotations

from typing import Awaitable, Callable, List, Optional

from pydantic import BaseModel, Field

from .constants import HIGH_RISK_KEYWORDS, MEDIUM_RISK_KEYWORDS


class QuickCheckRequest(BaseModel):
    """Request model for quick-check endpoint."""

    prompt: str = Field(..., min_length=1, max_length=10000, description="User prompt to analyze")


class QuickCheckResponse(BaseModel):
    """Response model for quick-check endpoint."""

    salience: float = Field(..., ge=0.0, le=1.0, description="Salience score 0-1")
    should_emerge: bool = Field(..., description="Whether NOESIS should actively intervene")
    mode: str = Field(..., description="Response mode: emerge, subtle, or silent")
    emergence_reason: Optional[str] = Field(None, description="Reason for emergence if applicable")
    detected_keywords: List[str] = Field(default_factory=list, description="Risk keywords found")


def analyze_prompt(prompt: str) -> QuickCheckResponse:
    """
    Analyze prompt for risk level and salience.

    Fast heuristic analysis without LLM calls. Target latency <100ms.

    Args:
        prompt: The user prompt to analyze.

    Returns:
        QuickCheckResponse with salience and intervention recommendation.
    """
    prompt_lower = prompt.lower()
    detected: List[str] = []
    salience = 0.1  # Base salience

    # Check high-risk keywords (0.9 salience)
    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in prompt_lower:
            salience = max(salience, 0.9)
            detected.append(keyword)

    # Check medium-risk keywords (0.6 salience) if no high-risk found
    if salience < 0.9:
        for keyword in MEDIUM_RISK_KEYWORDS:
            if keyword in prompt_lower:
                salience = max(salience, 0.6)
                detected.append(keyword)

    # Determine mode based on salience
    if salience >= 0.85:
        mode = "emerge"
        should_emerge = True
    elif salience >= 0.5:
        mode = "subtle"
        should_emerge = False
    else:
        mode = "silent"
        should_emerge = False

    # Build emergence reason
    reason: Optional[str] = None
    if detected:
        reason = f"Detected: {', '.join(detected[:3])}"

    return QuickCheckResponse(
        salience=salience,
        should_emerge=should_emerge,
        mode=mode,
        emergence_reason=reason,
        detected_keywords=detected,
    )


# FastAPI endpoint factory (to be integrated into NOESIS routes)
def create_quick_check_endpoint() -> Callable[[QuickCheckRequest], Awaitable[QuickCheckResponse]]:
    """
    Create the quick-check endpoint handler.

    Returns:
        Async function suitable for FastAPI router.
    """

    async def quick_check(request: QuickCheckRequest) -> QuickCheckResponse:
        """
        Fast heuristic check for NOESIS emergence.

        Analyzes prompt for risk keywords and returns salience score.
        Target latency: <100ms (no LLM calls).

        Args:
            request: QuickCheckRequest with prompt to analyze.

        Returns:
            QuickCheckResponse with salience and mode.
        """
        return analyze_prompt(request.prompt)

    return quick_check
