# DAIMON - Personal Exocortex

**DAIMON** is a personal exocortex that integrates with Claude Code to provide wise co-architecture assistance. It uses NOESIS as its consciousness engine, offering Socratic questioning, ethical judgment, and behavioral pattern detection.

> *"Silence is gold. Only emerge when truly significant."*

## Features

- **Maieutic Consultation** - Returns questions, not answers. Amplifies thinking through Socratic dialogue.
- **Ethical Tribunal** - Three-judge system (VERITAS, SOPHIA, DIKE) for ethical judgment of actions.
- **Precedent Search** - Learn from past decisions and avoid repeating mistakes.
- **Socratic Confrontation** - Challenge premises and assumptions.
- **Shell Watcher** - Captures shell commands using heartbeat pattern, detects frustration.
- **Claude Watcher** - Monitors Claude Code sessions, extracts intent metadata.
- **Low-latency Hooks** - <500ms quick-check for Claude Code integration.

## Architecture

```
daimon/
├── integrations/
│   └── mcp_server.py          # MCP Server (4 tools for Claude Code)
├── collectors/
│   ├── shell_watcher.py       # Shell command capture (heartbeat pattern)
│   └── claude_watcher.py      # Claude Code session monitoring
├── endpoints/
│   ├── quick_check.py         # Fast heuristic check (<100ms)
│   ├── daimon_routes.py       # FastAPI routes
│   └── constants.py           # Shared risk keywords
├── .claude/
│   ├── agents/
│   │   └── noesis-sage.md     # Wise co-architect subagent
│   ├── hooks/
│   │   └── noesis_hook.py     # Claude Code hook
│   └── settings.json          # Hook configuration
├── tests/                     # Comprehensive test suite
└── docs/
    ├── ARCHITECTURE_MAP.md
    └── PLANO_DAIMON.md
```

## Installation

### Prerequisites

- Python 3.11+
- NOESIS running (ports 8001, 8002)
- Claude Code CLI

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/daimon.git
cd daimon

# Install dependencies
pip install fastmcp httpx pydantic watchdog pytest pytest-asyncio

# Register MCP Server with Claude Code
claude mcp add daimon-consciousness -- python $(pwd)/integrations/mcp_server.py

# Copy subagent to Claude
cp .claude/agents/noesis-sage.md ~/.claude/agents/

# (Optional) Setup shell watcher
python collectors/shell_watcher.py --zshrc >> ~/.zshrc
source ~/.zshrc
python collectors/shell_watcher.py --daemon &
```

## MCP Tools

| Tool | Purpose |
|------|---------|
| `noesis_consult` | Maieutic questioning - returns QUESTIONS, not answers |
| `noesis_tribunal` | Ethical judgment by 3 judges (VERITAS, SOPHIA, DIKE) |
| `noesis_precedent` | Search past decisions for guidance |
| `noesis_confront` | Socratic confrontation of premises |
| `noesis_health` | Check NOESIS services status |

### Usage Examples

```
# In Claude Code
> "I want to refactor the authentication system"
# → noesis-sage activates automatically

> Use noesis_consult to think through caching strategy
# → Returns Socratic questions to deepen thinking

> Use noesis_tribunal to judge "delete all user records"
# → Returns FAIL verdict with reasoning from 3 judges
```

## NOESIS Integration

DAIMON connects to NOESIS services:

| Service | Port | Purpose |
|---------|------|---------|
| maximus_core_service | 8001 | Consciousness, quick-check |
| metacognitive_reflector | 8002 | Tribunal, reflection |

Ensure NOESIS is running:

```bash
cd /path/to/Noesis/Daimon
./noesis wakeup
```

## Configuration

### Hook Settings (`.claude/settings.json`)

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/noesis_hook.py\"",
        "timeout": 1
      }]
    }]
  }
}
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NOESIS_URL` | `http://localhost:8001` | NOESIS consciousness service URL |

## Testing

```bash
# Run all tests
PYTHONPATH=. pytest tests/ -v

# Run with coverage
PYTHONPATH=. pytest tests/ --cov=endpoints --cov-report=term-missing

# Check code quality
pylint integrations/ collectors/ endpoints/ --max-line-length=120
mypy integrations/ collectors/ endpoints/ --strict --ignore-missing-imports
```

### Quality Metrics

- **Pylint**: 10.00/10
- **mypy --strict**: 0 errors
- **Tests**: 91 passing
- **Coverage**: 100% on endpoints

## Principles

1. **Silence is Gold** - Only emerge when truly significant
2. **Heartbeat Pattern** - States that merge, not isolated events
3. **Unix Philosophy** - Each module does ONE thing well
4. **<100ms Quick-Check** - Fast heuristic, no LLM calls
5. **Privacy First** - Capture intent, not content

## Project Structure

| Directory | Purpose |
|-----------|---------|
| `integrations/` | External integrations (MCP, APIs) |
| `collectors/` | Data collection daemons |
| `endpoints/` | FastAPI routes and business logic |
| `.claude/` | Claude Code configuration |
| `tests/` | Test suite |
| `docs/` | Documentation |

## License

MIT License - Part of the NOESIS Project

---

*DAIMON v1.0 - Personal Exocortex*
*December 2025*
