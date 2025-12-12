"""
DAIMON MCP Server - Personal Exocortex Interface
=================================================

Exposes NOESIS consciousness to Claude Code via 4 MCP tools.

Tools:
- noesis_consult: Maieutic questioning (returns questions, not answers)
- noesis_tribunal: Ethical judgment (3-judge verdict)
- noesis_precedent: Search past decisions for guidance
- noesis_confront: Socratic confrontation of premises

Usage:
    claude mcp add daimon-consciousness -- python /path/to/mcp_server.py
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import httpx
from fastmcp import FastMCP

# Configuration
NOESIS_CONSCIOUSNESS_URL = "http://localhost:8001"  # maximus_core_service
NOESIS_REFLECTOR_URL = "http://localhost:8002"  # metacognitive_reflector
REQUEST_TIMEOUT = 30.0

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("daimon-mcp")

# MCP Server
mcp = FastMCP(
    name="daimon-consciousness",
    version="1.0.0",
    instructions="""
    DAIMON is your wise co-architect. Use these tools for thoughtful decisions:

    - noesis_consult: Ask before deciding. Returns QUESTIONS, not answers.
      Use for: architectural decisions, unclear requirements, tradeoffs.

    - noesis_tribunal: Submit actions for ethical judgment by 3 judges.
      Use for: destructive operations, security-sensitive code, user data.

    - noesis_precedent: Search for similar past decisions and their outcomes.
      Use for: recurring patterns, learning from history, avoiding past mistakes.

    - noesis_confront: Challenge your premises socratically.
      Use for: high-confidence statements, assumptions, overconfident assertions.

    Philosophy: Silence is gold. Only emerge when truly significant.
    """,
)


async def _http_post(
    url: str, payload: Dict[str, Any], timeout: float = REQUEST_TIMEOUT
) -> Dict[str, Any]:
    """Make HTTP POST request with error handling."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result: Dict[str, Any] = response.json()
            return result
    except httpx.TimeoutException:
        logger.warning("Request timeout: %s", url)
        return {"error": "timeout", "message": f"Request to {url} timed out"}
    except httpx.HTTPStatusError as e:
        logger.warning("HTTP error %d: %s", e.response.status_code, url)
        return {"error": "http_error", "status": e.response.status_code}
    except httpx.RequestError as e:
        logger.warning("Request error: %s - %s", url, str(e))
        return {"error": "connection_error", "message": str(e)}


async def _http_get(url: str, timeout: float = REQUEST_TIMEOUT) -> Dict[str, Any]:
    """Make HTTP GET request with error handling."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            result: Dict[str, Any] = response.json()
            return result
    except httpx.TimeoutException:
        logger.warning("GET timeout: %s", url)
        return {"error": "timeout", "message": f"Request to {url} timed out"}
    except httpx.HTTPStatusError as exc:
        logger.warning("GET HTTP error %d: %s", exc.response.status_code, url)
        return {"error": "http_error", "status": exc.response.status_code}
    except httpx.RequestError as exc:
        logger.warning("GET error: %s - %s", url, str(exc))
        return {"error": "request_error", "message": str(exc)}


@mcp.tool
async def noesis_consult(
    question: str,
    context: Optional[str] = None,
    depth: int = 2
) -> str:
    """
    Consult NOESIS for maieutic guidance. Returns QUESTIONS, not answers.

    Use this when facing:
    - Architectural decisions with multiple valid approaches
    - Unclear or ambiguous requirements
    - Tradeoffs between competing concerns
    - Decisions that could have long-term consequences

    Args:
        question: What you want to think through
        context: Additional context about the situation (optional)
        depth: Thinking depth 1-5 (default: 2)

    Returns:
        Socratic questions to deepen your thinking
    """
    payload = {
        "content": question,
        "context": context or "",
        "depth": min(max(depth, 1), 5),
        "mode": "maieutic"  # Request maieutic (questioning) mode
    }

    result = await _http_post(
        f"{NOESIS_CONSCIOUSNESS_URL}/api/consciousness/stream/process",
        payload
    )

    if "error" in result:
        msg = result.get('message', 'unknown error')
        fallback = (
            f"[NOESIS unavailable: {msg}]\n\n"
            "Consider these questions yourself:\n"
            "1. What are the core tradeoffs?\n"
            "2. What could go wrong?\n"
            "3. What assumptions am I making?"
        )
        return fallback

    # Extract the maieutic questions from the response
    response_text = result.get("response", "")
    consciousness_state = result.get("consciousness_state", {})

    output = ["## NOESIS Consultation\n"]

    if response_text:
        output.append(response_text)

    # Add consciousness metrics if available
    if consciousness_state:
        coherence = consciousness_state.get("coherence", 0)
        if coherence > 0:
            output.append(f"\n\n*Coherence: {coherence:.2f}*")

    return "\n".join(output)


@mcp.tool
async def noesis_tribunal(  # pylint: disable=too-many-locals
    action: str,
    justification: Optional[str] = None,
    context: Optional[str] = None
) -> str:
    """
    Submit an action for ethical judgment by the Tribunal (3 judges).

    Judges:
    - VERITAS (Truth): Factual accuracy, honesty
    - SOPHIA (Wisdom): Strategic thinking, prudence
    - DIKE (Justice): Fairness, rights protection

    Use this for:
    - Destructive operations (delete, drop, rm -rf)
    - Security-sensitive code changes
    - User data handling decisions
    - Production deployments

    Args:
        action: The action to be judged
        justification: Why you believe this action is appropriate (optional)
        context: Additional context about the situation (optional)

    Returns:
        Verdict (PASS/REVIEW/FAIL) with judge reasoning
    """
    payload = {
        "execution_log": {
            "content": action,
            "task": action[:100],
            "result": justification or "Action pending judgment",
            "context": context or ""
        },
        "require_unanimous": False
    }

    result = await _http_post(
        f"{NOESIS_REFLECTOR_URL}/reflect/verdict",
        payload
    )

    if "error" in result:
        msg = result.get('message', 'unknown error')
        return (
            f"[Tribunal unavailable: {msg}]\n\n"
            "**CAUTION**: Proceed with extra care without ethical oversight."
        )

    # Format the verdict
    output = ["## Tribunal Verdict\n"]

    verdict = result.get("verdict", "UNKNOWN")
    consensus = result.get("consensus_score", 0)

    # Verdict emoji
    verdict_emoji = {
        "PASS": "PASS",
        "REVIEW": "REVIEW",
        "FAIL": "FAIL",
        "CAPITAL": "CAPITAL"
    }.get(verdict, "UNKNOWN")

    output.append(f"**Decision**: {verdict_emoji}")
    output.append(f"**Consensus**: {consensus:.1%}\n")

    # Individual judge verdicts
    individual = result.get("individual_verdicts", {})
    if individual:
        output.append("### Judge Verdicts\n")
        for judge, jv in individual.items():
            vote = jv.get("vote", "?")
            confidence = jv.get("confidence", 0)
            reasoning = jv.get("reasoning", "")[:200]
            output.append(f"**{judge}**: {vote} ({confidence:.0%})")
            if reasoning:
                output.append(f"> {reasoning}\n")

    # Crimes detected
    crimes = result.get("crimes_detected", [])
    if crimes:
        output.append(f"\n**Concerns**: {', '.join(crimes)}")

    # Overall reasoning
    reasoning = result.get("reasoning", "")
    if reasoning:
        output.append(f"\n### Reasoning\n{reasoning}")

    return "\n".join(output)


@mcp.tool
async def noesis_precedent(
    situation: str,
    limit: int = 3
) -> str:
    """
    Search for similar past decisions (precedents) for guidance.

    The precedent ledger records past tribunal decisions. Use this to:
    - Learn from past mistakes
    - Find guidance for recurring situations
    - Understand historical patterns

    Args:
        situation: Description of the current situation
        limit: Maximum number of precedents to return (1-10, default: 3)

    Returns:
        Similar past decisions with their outcomes and lessons
    """
    # First, try to get precedents via the tribunal service
    # The precedent search is built into the verdict process
    payload = {
        "execution_log": {
            "content": situation,
            "task": "precedent_search",
            "result": "searching"
        },
        "search_precedents_only": True,
        "precedent_limit": min(max(limit, 1), 10)
    }

    result = await _http_post(
        f"{NOESIS_REFLECTOR_URL}/reflect/verdict",
        payload
    )

    output = ["## Precedent Search\n"]
    output.append(f"**Situation**: {situation[:200]}...\n")

    # Extract precedents from result
    precedents = result.get("precedent_guidance", [])

    if precedents:
        output.append(f"### Found {len(precedents)} Relevant Precedent(s)\n")

        for i, prec in enumerate(precedents[:limit], 1):
            decision = prec.get("decision", "?")
            consensus = prec.get("consensus_score", 0)
            reasoning = prec.get("key_reasoning", "")[:300]
            timestamp = prec.get("timestamp", "")[:10]

            output.append(f"**{i}. {decision}** (consensus: {consensus:.0%})")
            if timestamp:
                output.append(f"   *Date: {timestamp}*")
            if reasoning:
                output.append(f"   > {reasoning}")
            output.append("")
    else:
        output.append("*No directly relevant precedents found.*\n")
        output.append("This may be a novel situation. Consider:")
        output.append("1. Use `noesis_tribunal` for ethical judgment")
        output.append("2. Use `noesis_consult` for maieutic guidance")
        output.append("3. Document this decision for future reference")

    return "\n".join(output)


@mcp.tool
async def noesis_confront(
    statement: str,
    shadow_pattern: Optional[str] = None
) -> str:
    """
    Challenge a premise or statement socratically.

    Use this when you notice:
    - High confidence in uncertain claims
    - Unexamined assumptions
    - Potential cognitive biases
    - Overconfident assertions

    The confrontation engine generates Socratic questions to:
    - Examine the evidence for claims
    - Consider alternative explanations
    - Identify hidden assumptions
    - Evaluate consequences of being wrong

    Args:
        statement: The premise or statement to challenge
        shadow_pattern: Optional pattern detected (e.g., "overconfidence", "assumption")

    Returns:
        Socratic questions challenging the premise
    """
    payload = {
        "trigger_event": statement,
        "violated_rule_id": None,
        "shadow_pattern": shadow_pattern or "unexamined_premise",
        "user_state": "ANALYTICAL"
    }

    result = await _http_post(
        f"{NOESIS_CONSCIOUSNESS_URL}/exocortex/confront",
        payload
    )

    if "error" in result:
        # Fallback: generate basic Socratic questions
        return f"""## Socratic Confrontation

**Premise**: {statement[:200]}

*[NOESIS unavailable - using fallback questions]*

### Challenge Questions

1. **Evidence**: What evidence supports this claim? Is it verifiable?

2. **Assumptions**: What unexamined assumptions underlie this statement?

3. **Alternatives**: What other explanations could account for this?

4. **Consequences**: If this is wrong, what would the consequences be?

5. **Origin**: Where did this belief come from? Training data? Heuristic?

*Reflect honestly before proceeding.*
"""

    output = ["## Socratic Confrontation\n"]
    output.append(f"**Premise**: {statement[:200]}\n")

    question = result.get("ai_question", "")
    style = result.get("style", "socratic")
    conf_id = result.get("id", "")

    if question:
        output.append(f"### {style.upper()} Challenge\n")
        output.append(question)
        output.append(f"\n*Confrontation ID: {conf_id}*")
    else:
        output.append("*No specific challenge generated.*")

    return "\n".join(output)


@mcp.tool
async def noesis_health() -> str:
    """
    Check the health of NOESIS services.

    Returns the status of:
    - Consciousness service (port 8001)
    - Metacognitive reflector (port 8002)
    """
    output = ["## NOESIS Health Check\n"]

    # Check consciousness service
    consciousness_health = await _http_get(f"{NOESIS_CONSCIOUSNESS_URL}/health")
    if "error" not in consciousness_health:
        output.append("**Consciousness**: ONLINE")
    else:
        msg = consciousness_health.get('message', 'unknown')
        output.append(f"**Consciousness**: OFFLINE ({msg})")

    # Check reflector service
    reflector_health = await _http_get(f"{NOESIS_REFLECTOR_URL}/health")
    if "error" not in reflector_health:
        output.append("**Tribunal**: ONLINE")
    else:
        msg = reflector_health.get('message', 'unknown')
        output.append(f"**Tribunal**: OFFLINE ({msg})")

    return "\n".join(output)


if __name__ == "__main__":
    logger.info("Starting DAIMON MCP Server...")
    logger.info("Consciousness URL: %s", NOESIS_CONSCIOUSNESS_URL)
    logger.info("Reflector URL: %s", NOESIS_REFLECTOR_URL)
    mcp.run(transport="stdio")
