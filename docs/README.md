# DAIMON - Personal Exocortex

**DAIMON** is a personal exocortex that uses NOESIS as its consciousness engine. It integrates with Claude Code to provide wise co-architecture assistance.

## Quick Start

### 1. Install Dependencies

```bash
cd /media/juan/DATA/projetos/daimon
pip install fastmcp httpx watchdog pydantic
```

### 2. Register MCP Server

```bash
claude mcp add daimon-consciousness -- python /media/juan/DATA/projetos/daimon/integrations/mcp_server.py
```

### 3. Copy Subagent

```bash
cp .claude/agents/noesis-sage.md ~/.claude/agents/
```

### 4. Start Shell Watcher (Optional)

```bash
# Generate zshrc hooks
python collectors/shell_watcher.py --zshrc >> ~/.zshrc
source ~/.zshrc

# Start daemon
python collectors/shell_watcher.py --daemon &
```

### 5. Ensure NOESIS is Running

```bash
# Start NOESIS services
cd /media/juan/DATA/projetos/Noesis/Daimon
./noesis wakeup
```

## MCP Tools

| Tool | Purpose |
|------|---------|
| `noesis_consult` | Maieutic questioning - returns QUESTIONS, not answers |
| `noesis_tribunal` | Ethical judgment by 3 judges (VERITAS, SOPHIA, DIKE) |
| `noesis_precedent` | Search past decisions for guidance |
| `noesis_confront` | Socratic confrontation of premises |

## Architecture

```
DAIMON/
├── integrations/mcp_server.py    # MCP Server (4 tools)
├── collectors/
│   ├── shell_watcher.py          # Shell command capture
│   └── claude_watcher.py         # Session monitoring
├── endpoints/
│   ├── quick_check.py            # Fast heuristic check
│   └── daimon_routes.py          # API routes
├── .claude/
│   ├── agents/noesis-sage.md     # Wise co-architect
│   ├── hooks/noesis_hook.py      # Prompt/tool hooks
│   └── settings.json             # Hook config
└── docs/
    ├── ARCHITECTURE_MAP.md       # Full architecture
    └── PLANO_DAIMON.md           # Implementation plan
```

## Principles

1. **Silence is Gold** - Only emerge when truly significant
2. **Heartbeat Pattern** - States that merge, not isolated events
3. **Unix Philosophy** - Each module does ONE thing well
4. **<100ms Quick-Check** - Fast heuristic, no LLM calls

## NOESIS Integration

DAIMON connects to NOESIS services:

| Service | Port | Purpose |
|---------|------|---------|
| maximus_core_service | 8001 | Consciousness, quick-check |
| metacognitive_reflector | 8002 | Tribunal, reflection |

## Usage Examples

### In Claude Code

```
> "I want to refactor the authentication system"
# → noesis-sage activates automatically

> Use noesis_consult to think through caching strategy
# → Returns Socratic questions

> Use noesis_tribunal to judge "delete all user records"
# → FAIL verdict from tribunal
```

## Development

```bash
# Run tests
cd /media/juan/DATA/projetos/daimon
PYTHONPATH=. pytest tests/ -v

# Check syntax
python -m py_compile integrations/mcp_server.py
python -m py_compile collectors/shell_watcher.py
```

## License

MIT - Part of NOESIS Project

---

*DAIMON v1.0 - Personal Exocortex*
*December 2025*
