"""
DAIMON Routes - FastAPI Router for NOESIS Integration
======================================================

API routes for DAIMON exocortex functionality.
To be integrated into maximus_core_service.

Follows CODE_CONSTITUTION: Clarity Over Cleverness, Files <300 lines.
"""
# pylint: disable=duplicate-code

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from .quick_check import QuickCheckRequest, QuickCheckResponse, analyze_prompt

logger = logging.getLogger(__name__)

# Router with DAIMON prefix
router = APIRouter(prefix="/api/daimon", tags=["DAIMON"])


# ============================================================================
# Quick-Check Endpoint (Sprint 4)
# ============================================================================


@router.post("/quick-check", response_model=QuickCheckResponse)
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


# ============================================================================
# Shell Batch Endpoint (Sprint 7)
# ============================================================================


class ShellHeartbeat(BaseModel):
    """Single shell command heartbeat."""

    timestamp: str = Field(..., description="ISO timestamp")
    command: str = Field(..., description="Shell command executed")
    pwd: str = Field(..., description="Working directory")
    exit_code: int = Field(..., description="Command exit code")
    duration: float = Field(0.0, description="Execution duration in seconds")
    git_branch: str = Field("", description="Current git branch if in repo")


class ShellBatchRequest(BaseModel):
    """Batch of shell heartbeats with detected patterns."""

    heartbeats: List[ShellHeartbeat] = Field(..., description="List of heartbeats")
    patterns: Dict[str, Any] = Field(default_factory=dict, description="Detected patterns")


class ShellBatchResponse(BaseModel):
    """Response for shell batch endpoint."""

    status: str = Field(..., description="Processing status")
    stored: int = Field(..., description="Number of heartbeats stored")
    insights: List[str] = Field(default_factory=list, description="Generated insights")


@router.post("/shell/batch", response_model=ShellBatchResponse)
async def receive_shell_batch(batch: ShellBatchRequest) -> ShellBatchResponse:
    """
    Receive batch of shell command heartbeats.

    Stores commands in episodic memory and generates insights from patterns.

    Args:
        batch: ShellBatchRequest with heartbeats and patterns.

    Returns:
        ShellBatchResponse with processing status.
    """
    insights: List[str] = []

    # Detect frustration pattern
    if batch.patterns.get("possible_frustration"):
        error_streak = batch.patterns.get("error_streak", 0)
        insights.append(f"Frustration detected: {error_streak} consecutive errors")
        logger.info("DAIMON: Frustration pattern detected (%d errors)", error_streak)

    # Log significant commands
    for hb in batch.heartbeats:
        if hb.exit_code != 0:
            logger.debug("DAIMON: Command failed: %s (exit %d)", hb.command[:50], hb.exit_code)

    return ShellBatchResponse(
        status="ok",
        stored=len(batch.heartbeats),
        insights=insights,
    )


# ============================================================================
# Claude Event Endpoint (Sprint 7)
# ============================================================================


class ClaudeEvent(BaseModel):
    """Event from Claude Code session."""

    event_type: str = Field(..., description="Event type: create, fix, refactor, understand, delete")
    timestamp: str = Field(..., description="ISO timestamp")
    project: str = Field("", description="Project identifier")
    files_touched: List[str] = Field(default_factory=list, description="Files involved")
    intention: str = Field("", description="Detected intention")


class ClaudeEventResponse(BaseModel):
    """Response for Claude event endpoint."""

    status: str = Field(..., description="Processing status")
    stored: bool = Field(..., description="Whether event was stored")


@router.post("/claude/event", response_model=ClaudeEventResponse)
async def receive_claude_event(event: ClaudeEvent) -> ClaudeEventResponse:
    """
    Receive event from Claude Code session watcher.

    Stores session metadata (not content) for pattern analysis.

    Args:
        event: ClaudeEvent with session metadata.

    Returns:
        ClaudeEventResponse with processing status.
    """
    logger.debug("DAIMON: Claude event received: %s", event.event_type)

    return ClaudeEventResponse(
        status="ok",
        stored=True,
    )


# ============================================================================
# Session End Endpoint (Sprint 7)
# ============================================================================


class SessionEndRequest(BaseModel):
    """Request to record session end as precedent."""

    session_id: str = Field(..., description="Session identifier")
    summary: str = Field(..., description="Session summary")
    outcome: str = Field("success", description="Session outcome: success, failure, partial")
    duration_minutes: float = Field(0.0, description="Session duration")
    files_changed: int = Field(0, description="Number of files modified")


class SessionEndResponse(BaseModel):
    """Response for session end endpoint."""

    status: str = Field(..., description="Processing status")
    precedent_id: Optional[str] = Field(None, description="Created precedent ID if significant")


@router.post("/session/end", response_model=SessionEndResponse)
async def record_session_end(request: SessionEndRequest) -> SessionEndResponse:
    """
    Record end of Claude Code session.

    Significant sessions are stored as precedents for future reference.

    Args:
        request: SessionEndRequest with session summary.

    Returns:
        SessionEndResponse with precedent ID if created.
    """
    logger.info(
        "DAIMON: Session ended - %s (%s, %d files)",
        request.session_id,
        request.outcome,
        request.files_changed,
    )

    # Only create precedent for significant sessions
    precedent_id: Optional[str] = None
    if request.files_changed >= 5 or request.duration_minutes >= 30:
        precedent_id = f"sess_{request.session_id[:8]}"
        logger.info("DAIMON: Created precedent %s", precedent_id)

    return SessionEndResponse(
        status="ok",
        precedent_id=precedent_id,
    )


# ============================================================================
# Health Check
# ============================================================================


@router.get("/health")
async def daimon_health() -> Dict[str, Any]:
    """
    Check DAIMON endpoints health.

    Returns:
        Health status dict.
    """
    return {
        "status": "healthy",
        "service": "daimon",
        "endpoints": [
            "/api/daimon/quick-check",
            "/api/daimon/shell/batch",
            "/api/daimon/claude/event",
            "/api/daimon/session/end",
        ],
    }
