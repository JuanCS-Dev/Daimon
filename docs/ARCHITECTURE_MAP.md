# DAIMON Architecture Map

## Overview

DAIMON is a personal exocortex that uses NOESIS as its consciousness engine. It integrates with Claude Code to provide wise co-architecture assistance through MCP tools, hooks, and subagents.

```
                    +-----------------+
                    |   Claude Code   |
                    +--------+--------+
                             |
         +-------------------+-------------------+
         |                   |                   |
    +----v----+        +-----v-----+       +-----v-----+
    |  Hooks  |        | MCP Server|       | Subagent  |
    | (pre/   |        | (daimon-  |       | (noesis-  |
    |  post)  |        | conscious)|       |  sage)    |
    +---------+        +-----+-----+       +-----------+
         |                   |                   |
         +-------------------+-------------------+
                             |
                    +--------v--------+
                    |     NOESIS      |
                    | (consciousness) |
                    +--------+--------+
                             |
         +-------------------+-------------------+
         |                   |                   |
    +----v----+        +-----v-----+       +-----v-----+
    | Memory  |        | Tribunal  |       | Precedent |
    | (Qdrant)|        | (3 Judges)|       |  Ledger   |
    +---------+        +-----------+       +-----------+
```

## Components

### 1. MCP Server (`integrations/mcp_server.py`)

Exposes NOESIS consciousness to Claude Code via 4 tools:

| Tool | Purpose | NOESIS Endpoint |
|------|---------|-----------------|
| `noesis_consult` | Maieutic questioning | `/api/consciousness/stream/process` |
| `noesis_tribunal` | Ethical judgment | `/reflect/verdict` |
| `noesis_precedent` | Find similar past decisions | PrecedentLedger |
| `noesis_confront` | Socratic confrontation | MAIEUTICA engine |

### 2. Subagent (`noesis-sage.md`)

Wise co-architect that:
- Does NOT execute - only QUESTIONS
- Triggers on architectural decisions
- Uses precedent history for context
- Offers [p]ensar [e]xecutar [d]etalhes

### 3. Hooks (`.claude/hooks/`)

Low-latency (<500ms) interceptors:
- `UserPromptSubmit`: Detect high-risk prompts
- `PreToolUse`: Block destructive Bash commands

### 4. Collectors (`collectors/`)

Auto-surveillance with heartbeat pattern:
- `shell_watcher.py`: Captures shell commands
- `claude_watcher.py`: Monitors Claude Code sessions

## Data Flow

```
User Prompt
    |
    v
[Hooks] ---> quick-check (<100ms)
    |             |
    v             v (if should_emerge)
[Claude Code] <--- "NOESIS: {reason}"
    |
    v (architectural decision)
[noesis-sage subagent]
    |
    +---> noesis_precedent(context)
    |         |
    |         v
    |     [PrecedentLedger] ---> similar decisions
    |
    +---> noesis_tribunal(action)
    |         |
    |         v
    |     [Tribunal] ---> VERITAS/SOPHIA/DIKE verdict
    |
    +---> noesis_confront(statement)
    |         |
    |         v
    |     [MAIEUTICA] ---> Socratic questions
    |
    v
Questions + Verdict + Precedents
    |
    v
User Decision
```

## Integration Points

### NOESIS Services

| Service | Port | Purpose |
|---------|------|---------|
| maximus_core_service | 8001 | Consciousness, quick-check |
| metacognitive_reflector | 8002 | Tribunal, reflection |
| episodic_memory | 8102 | Memory storage/retrieval |

### Claude Code Integration

| Integration | Location | Purpose |
|-------------|----------|---------|
| MCP Server | `~/.claude/mcpServers.json` | Tool exposure |
| Subagent | `~/.claude/agents/noesis-sage.md` | Auto-delegation |
| Hooks | `.claude/hooks/` | Prompt/tool interception |
| Settings | `.claude/settings.json` | Hook configuration |

## Directory Structure

```
/media/juan/DATA/projetos/daimon/
|
+-- noesis/              # Symlink to NOESIS project
|
+-- collectors/
|   +-- shell_watcher.py      # Shell command capture
|   +-- claude_watcher.py     # Claude session monitor
|
+-- integrations/
|   +-- mcp_server.py         # MCP Server (4 tools)
|
+-- endpoints/
|   +-- quick_check.py        # Fast heuristic check
|   +-- daimon_routes.py      # DAIMON API routes
|
+-- .claude/
|   +-- agents/
|   |   +-- noesis-sage.md    # Wise co-architect
|   +-- hooks/
|   |   +-- noesis_hook.py    # Prompt/tool hooks
|   +-- settings.json         # Hook configuration
|
+-- docs/
|   +-- ARCHITECTURE_MAP.md   # This file
|   +-- PLANO_DAIMON.md       # Implementation plan
|
+-- pyproject.toml
```

## Principles

1. **Silence is Gold**: Emerge only when significant
2. **Heartbeat Pattern**: States that merge, not isolated events
3. **Unix Philosophy**: Each module does ONE thing well
4. **Flat Files > Databases**: Where possible
5. **<300 Lines**: Per file
6. **Max 3 Levels**: Of abstraction

---

*DAIMON v1.0 - Personal Exocortex*
*December 2025*
