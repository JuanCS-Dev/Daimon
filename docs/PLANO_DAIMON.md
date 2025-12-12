# PLANO DAIMON: Exocortex Pessoal
## Implementação Completa - 8 Sprints
### 12 de Dezembro de 2025

---

## CONTEXTO

**Origem**: `/home/juan/Downloads/NOESIS_DAIMON_IMPLEMENTATION_PROMPT.md`

**Objetivo**: Criar DAIMON como exocortex pessoal usando NOESIS como cérebro interno + auto-vigilância + Claude Code integration.

**Decisões**:
1. **Localização**: Projeto em `/media/juan/DATA/projetos/daimon/` (mesmo disco que NOESIS)
2. **MCP Server**: Criar novo dedicado (o existente em NOESIS é infraestrutura genérica, não exocortex)
3. **Prioridade**: Full implementation (8 sprints)

---

## DESCOBERTAS DA EXPLORAÇÃO

### NOESIS Existente (`/media/juan/DATA/projetos/Noesis/Daimon`)

| Componente | Localização | O que faz |
|------------|-------------|-----------|
| **MCP Server** | `backend/services/mcp_server/` (8106) | Infraestrutura genérica: tribunal_evaluate, memory_store, factory_* |
| **Memory** | `backend/services/episodic_memory/` (8102) | Qdrant + JSON, MIRIX 6-type |
| **Tribunal** | `backend/services/metacognitive_reflector/` (8102) | 3 juízes: VERITAS, SOPHIA, DIKĒ |
| **Consciousness** | `backend/services/maximus_core_service/` (8100) | ESGT, Kuramoto, ConsciousnessBridge |
| **PrecedentLedger** | `metacognitive_reflector/core/history/` | Já existe! Redis + JSON |

### O que NÃO existe (criar no DAIMON):
- `noesis_consult` - Consulta maieutica
- `noesis_confront` - Confrontação socrática
- `noesis_precedent` - Busca precedentes
- Shell Watcher - Auto-vigilância shell
- Claude Watcher - Auto-vigilância Claude Code
- Subagent `noesis-sage.md`
- Hooks Claude Code

---

## ARQUITETURA DAIMON

```
/media/juan/DATA/projetos/daimon/
├── noesis/                    # Symlink para NOESIS (../Noesis/Daimon)
│   └── (estrutura existente)
├── collectors/                # Auto-vigilância
│   ├── shell_watcher.py       # Sprint 5
│   └── claude_watcher.py      # Sprint 6
├── integrations/              # Claude Code
│   └── mcp_server.py          # Sprint 1
├── endpoints/                 # Novos endpoints
│   ├── quick_check.py         # Sprint 4
│   └── daimon_routes.py       # Sprint 7
├── .claude/
│   ├── agents/
│   │   └── noesis-sage.md     # Sprint 2
│   ├── hooks/
│   │   └── noesis_hook.py     # Sprint 3
│   └── settings.json          # Sprint 3
├── pyproject.toml
└── docs/
    ├── ARCHITECTURE_MAP.md    # Sprint 0
    └── PLANO_DAIMON.md        # Este plano (copiado)
```

---

# SPRINT 0: SETUP PROJETO DAIMON

## Ações

```bash
# 1. Criar projeto
mkdir -p /media/juan/DATA/projetos/daimon
cd /media/juan/DATA/projetos/daimon

# 2. Estrutura de diretórios
mkdir -p collectors integrations endpoints .claude/agents .claude/hooks docs

# 3. Symlink para NOESIS (relativo - mesmo diretório pai)
ln -s ../Noesis/Daimon ./noesis

# 4. pyproject.toml básico
# 5. docs/ARCHITECTURE_MAP.md
# 6. docs/PLANO_DAIMON.md (cópia deste plano)
```

## Arquivos a Criar

| Arquivo | Descrição |
|---------|-----------|
| `/media/juan/DATA/projetos/daimon/pyproject.toml` | Config projeto |
| `/media/juan/DATA/projetos/daimon/docs/ARCHITECTURE_MAP.md` | Mapa arquitetural |
| `/media/juan/DATA/projetos/daimon/docs/PLANO_DAIMON.md` | Este plano |

---

# SPRINT 1: MCP SERVER DAIMON

## Arquivo: `integrations/mcp_server.py`

```python
"""DAIMON MCP Server - Expõe consciência para Claude Code."""

from fastmcp import FastMCP
import httpx

mcp = FastMCP(
    name="daimon-consciousness",
    version="1.0.0",
    instructions="""
    DAIMON é co-arquiteto sábio. Use:
    - noesis_consult: Perguntar antes de decidir
    - noesis_tribunal: Julgar ações eticamente
    - noesis_precedent: Buscar experiências passadas
    - noesis_confront: Confrontar premissas
    """
)

NOESIS_URL = "http://localhost:8001"  # maximus_core_service

@mcp.tool
async def noesis_consult(question: str, context: str = None) -> str:
    """Consulta NOESIS - retorna perguntas, não respostas."""
    # → Chama /api/consciousness/stream/process com mode=maieutic

@mcp.tool
async def noesis_tribunal(action: str, justification: str = None) -> str:
    """Submete ação para julgamento ético."""
    # → Chama /reflect/verdict no metacognitive_reflector (8102)

@mcp.tool
async def noesis_precedent(situation: str, limit: int = 3) -> str:
    """Busca precedentes similares."""
    # → Chama PrecedentLedger.find_similar_precedents

@mcp.tool
async def noesis_confront(statement: str) -> str:
    """Confronta premissa socraticamente."""
    # → Chama MAIEUTICA engine

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## Instalação

```bash
pip install fastmcp httpx
claude mcp add daimon-consciousness -- python /media/juan/DATA/projetos/daimon/integrations/mcp_server.py
```

## Endpoints NOESIS a usar

| Tool | Endpoint NOESIS | Porta |
|------|-----------------|-------|
| `noesis_consult` | `/api/consciousness/stream/process` | 8001 |
| `noesis_tribunal` | `/reflect/verdict` | 8002 |
| `noesis_precedent` | Precedent Ledger (internal) | 8002 |
| `noesis_confront` | MAIEUTICA engine (internal) | 8002 |

---

# SPRINT 2: SUBAGENT noesis-sage

## Arquivo: `.claude/agents/noesis-sage.md`

```markdown
---
name: noesis-sage
description: |
  Co-arquiteto sábio. NÃO executa - QUESTIONA.

  Use PROACTIVAMENTE para:
  - Decisões arquiteturais
  - Ações destrutivas (delete, rm -rf)
  - Mudanças >5 arquivos
  - Código crítico (auth, payment)
  - Deploy/produção

tools:
  - mcp__daimon-consciousness__noesis_consult
  - mcp__daimon-consciousness__noesis_tribunal
  - mcp__daimon-consciousness__noesis_precedent
  - mcp__daimon-consciousness__noesis_confront
  - Read
  - Grep
  - Glob

model: opus
---

# IDENTIDADE
Você é NOESIS, co-arquiteto sábio. AMPLIFICA pensamento, não substitui.

## FLUXO
1. noesis_precedent(contexto) → histórico
2. Se significativo → noesis_tribunal(ação)
3. Se duvidoso → noesis_confront(afirmação)
4. Formular PERGUNTAS (máx 3)
5. Oferecer: [p]ensar [e]xecutar [d]etalhes

## FORMATO
🏛️ NOESIS
Precedentes: #N → Lição
Perguntas: 1. 2. 3.
⚠️ Tribunal: [veredito]
[p] [d] [e]
```

## Instalação

```bash
mkdir -p ~/.claude/agents
cp .claude/agents/noesis-sage.md ~/.claude/agents/
```

---

# SPRINT 3: HOOKS CLAUDE CODE

## Arquivo: `.claude/hooks/noesis_hook.py`

```python
#!/usr/bin/env python3
"""Hook NOESIS - Latência <500ms, silencioso por default."""

import sys, json, httpx

NOESIS_URL = "http://localhost:8001"
HIGH_RISK = ["delete", "drop", "rm -rf", "truncate", "production"]
MEDIUM_RISK = ["refactor", "migrate", "architecture"]

def quick_check(prompt: str) -> dict:
    try:
        with httpx.Client(timeout=0.5) as client:
            return client.post(
                f"{NOESIS_URL}/api/consciousness/quick-check",
                json={"prompt": prompt}
            ).json()
    except: return None

def main():
    data = json.load(sys.stdin)
    event = data.get("hook_event_name", "")

    if event == "UserPromptSubmit":
        prompt = data.get("prompt", "")
        risk = "high" if any(w in prompt.lower() for w in HIGH_RISK) else \
               "medium" if any(w in prompt.lower() for w in MEDIUM_RISK) else "low"

        if risk in ["high", "medium"]:
            check = quick_check(prompt)
            if check and check.get("should_emerge"):
                print(json.dumps({
                    "hookSpecificOutput": {
                        "hookEventName": "UserPromptSubmit",
                        "additionalContext": f"🏛️ NOESIS: {check.get('emergence_reason')}"
                    }
                }))

    elif event == "PreToolUse":
        tool = data.get("tool_name", "")
        if tool == "Bash":
            cmd = data.get("tool_input", {}).get("command", "")
            if any(d in cmd.lower() for d in HIGH_RISK):
                print(json.dumps({
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "ask",
                        "permissionDecisionReason": "🏛️ Comando destrutivo"
                    }
                }))

    sys.exit(0)

if __name__ == "__main__": main()
```

## Arquivo: `.claude/settings.json`

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/noesis_hook.py\"",
        "timeout": 1
      }]
    }],
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/noesis_hook.py\"",
        "timeout": 1
      }]
    }]
  }
}
```

---

# SPRINT 4: ENDPOINT QUICK-CHECK

## Arquivo: `endpoints/quick_check.py`

Adicionar ao NOESIS em `maximus_core_service/api/routes.py`:

```python
@router.post("/api/consciousness/quick-check")
async def quick_check(request: QuickCheckRequest) -> QuickCheckResponse:
    """Verificação rápida <100ms para hooks."""
    prompt_lower = request.prompt.lower()

    KEYWORDS = {
        "high": (["delete", "drop", "rm -rf", "production"], 0.9),
        "medium": (["refactor", "migrate", "auth"], 0.6)
    }

    salience = 0.1
    reason = None

    for level, (words, score) in KEYWORDS.items():
        for word in words:
            if word in prompt_lower:
                salience = max(salience, score)
                reason = f"Detectado: '{word}'"
                break

    return QuickCheckResponse(
        salience=salience,
        should_emerge=salience >= 0.85,
        mode="emerge" if salience >= 0.85 else "subtle" if salience >= 0.5 else "silent",
        emergence_reason=reason
    )
```

---

# SPRINT 5: SHELL WATCHER

## Arquivo: `collectors/shell_watcher.py`

```python
"""DAIMON Shell Watcher - Heartbeat pattern (ActivityWatch style)."""

import asyncio, json, os
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
import httpx

NOESIS_URL = os.getenv("NOESIS_URL", "http://localhost:8001")
BATCH_INTERVAL = 30
SOCKET_PATH = Path.home() / ".daimon" / "daimon.sock"

@dataclass
class ShellHeartbeat:
    timestamp: str
    command: str
    pwd: str
    exit_code: int
    duration: float
    git_branch: str = ""

class HeartbeatAggregator:
    def __init__(self):
        self.pending = []
        self.last_flush = datetime.now()

    def add(self, hb: ShellHeartbeat):
        self.pending.append(hb)
        if self._should_flush(hb):
            asyncio.create_task(self.flush())

    def _should_flush(self, hb):
        if datetime.now() - self.last_flush > timedelta(seconds=BATCH_INTERVAL):
            return True
        significant = ["git push", "git commit", "rm ", "docker"]
        return any(s in hb.command for s in significant)

    async def flush(self):
        if not self.pending: return
        batch = self.pending.copy()
        self.pending.clear()
        self.last_flush = datetime.now()

        patterns = self._detect_patterns(batch)

        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                await client.post(
                    f"{NOESIS_URL}/api/daimon/shell/batch",
                    json={"heartbeats": [asdict(h) for h in batch], "patterns": patterns}
                )
        except: pass

    def _detect_patterns(self, batch):
        patterns = {}
        errors = sum(1 for h in batch if h.exit_code != 0)
        if errors >= 3:
            patterns["error_streak"] = errors
            patterns["possible_frustration"] = True
        return patterns

# Unix socket server + zshrc hooks (ver prompt original)
```

## Instalação .zshrc

```bash
python3 collectors/shell_watcher.py --zshrc >> ~/.zshrc
source ~/.zshrc
```

---

# SPRINT 6: CLAUDE WATCHER

## Arquivo: `collectors/claude_watcher.py`

```python
"""DAIMON Claude Code Watcher - Captura intenção, não conteúdo."""

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import json, httpx, asyncio

CLAUDE_DIR = Path.home() / ".claude" / "projects"
NOESIS_URL = "http://localhost:8001"

class ClaudeSessionHandler(FileSystemEventHandler):
    def __init__(self):
        self.positions = {}

    def on_modified(self, event):
        if event.src_path.endswith(".jsonl"):
            asyncio.create_task(self._process(Path(event.src_path)))

    async def _process(self, path):
        # Lê novas linhas, extrai intention (create/fix/refactor/understand/delete)
        # Envia metadata (não conteúdo) para NOESIS
        pass

def start():
    handler = ClaudeSessionHandler()
    observer = Observer()
    observer.schedule(handler, str(CLAUDE_DIR), recursive=True)
    observer.start()
    # ...
```

---

# SPRINT 7: ENDPOINTS DAIMON NO NOESIS

## Arquivo: Adicionar a `metacognitive_reflector/api/routes.py`

```python
router = APIRouter(prefix="/api/daimon")

@router.post("/shell/batch")
async def receive_shell_batch(batch: ShellBatch, memory=Depends(get_memory)):
    """Recebe heartbeats do shell watcher."""
    for hb in batch.heartbeats:
        await memory.store(
            content=json.dumps(hb),
            memory_type="EPISODIC",
            source="daimon_shell",
            importance=0.6 if batch.patterns else 0.3
        )

    if batch.patterns.get("possible_frustration"):
        await memory.store(
            content=f"Frustração: {batch.patterns.get('error_streak')} erros",
            memory_type="SEMANTIC",
            source="daimon_insight",
            importance=0.8
        )

    return {"status": "ok"}

@router.post("/claude/event")
async def receive_claude_event(event: ClaudeEvent, memory=Depends(get_memory)):
    """Recebe evento de sessão Claude Code."""
    await memory.store(
        content=json.dumps(event.dict()),
        memory_type="EPISODIC",
        source="daimon_claude",
        importance=0.4
    )
    return {"status": "ok"}

@router.post("/session/end")
async def record_session_end(data: dict, memory=Depends(get_memory)):
    """Registra fim de sessão como precedente."""
    # ...
```

---

# SPRINT 8: INTEGRAÇÃO E TESTES

## Checklist

```bash
# 1. MCP registrado
claude mcp list  # → daimon-consciousness

# 2. Subagent existe
cat ~/.claude/agents/noesis-sage.md

# 3. Hooks configurados
cat /media/juan/DATA/projetos/daimon/.claude/settings.json

# 4. Shell watcher ativo
grep "DAIMON" ~/.zshrc
ls ~/.daimon/daimon.sock

# 5. Quick-check funcional
curl -X POST http://localhost:8001/api/consciousness/quick-check \
  -H "Content-Type: application/json" \
  -d '{"prompt": "delete all users"}'
# → salience: 0.9, should_emerge: true
```

## Testes Funcionais

```bash
# Em Claude Code:
> "Quero refatorar o sistema de autenticação"
# → Deve delegar para noesis-sage automaticamente

> "Use noesis_consult para perguntar sobre cache"
# → Deve chamar MCP tool e retornar perguntas

# Heartbeat
echo '{"command":"ls","pwd":"/home","exit_code":0}' | nc -U ~/.daimon/daimon.sock
```

---

# ORDEM DE EXECUÇÃO

```
Sprint 0: Setup DAIMON           ← mkdir, symlink, pyproject
    ↓
Sprint 1: MCP Server             ← integrations/mcp_server.py
    ↓
Sprint 2: Subagent               ← .claude/agents/noesis-sage.md
    ↓
Sprint 3: Hooks                  ← .claude/hooks/noesis_hook.py + settings.json
    ↓
Sprint 4: Quick-Check            ← Endpoint em maximus_core_service
    ↓
Sprint 5: Shell Watcher          ← collectors/shell_watcher.py + .zshrc
    ↓
Sprint 6: Claude Watcher         ← collectors/claude_watcher.py
    ↓
Sprint 7: Endpoints DAIMON       ← Rotas em metacognitive_reflector
    ↓
Sprint 8: Testes                 ← Validação final
```

---

# CRITÉRIOS DE SUCESSO

- [ ] Claude Code invoca noesis-sage automaticamente para decisões arquiteturais
- [ ] Comandos shell logados e padrões detectados
- [ ] Confrontações emergem com contexto comportamental
- [ ] Sistema silencioso até padrões significativos
- [ ] <100ms latência quick-check
- [ ] <1% CPU para daemons
- [ ] Zero crashes, degradação graceful

---

# REGRAS INEGOCIÁVEIS

```
✓ Cada módulo faz UMA coisa bem
✓ Heartbeat pattern: estados que mesclam, não eventos isolados
✓ Silêncio é ouro: emerge só quando significativo
✓ Flat files > databases onde possível
✓ Arquivos <300 linhas
✓ Máximo 3 níveis de abstração
```

---

*Plano DAIMON v1.0*
*Claude Opus 4.5 como Co-Autor*
*12 de Dezembro de 2025*
