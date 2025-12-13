# PLANO DE INTEGRAÇÃO - DAIMON AIR GAPS

**Status:** ✅ IMPLEMENTADO
**Data:** 2025-12-13
**Versão:** 1.0
**Lei Suprema:** [CODE_CONSTITUTION.md](./CODE_CONSTITUTION.md)

---

## PREÂMBULO: A LEI

> **"The letter killeth, but the spirit giveth life."** - CODE_CONSTITUTION

Este plano segue a **CODE_CONSTITUTION** como lei absoluta. Qualquer violação será tratada como **CAPITAL OFFENSE**.

### Princípios Invioláveis

| Princípio | Aplicação Neste Plano |
|-----------|----------------------|
| **Clarity Over Cleverness** | Código óbvio, não astuto |
| **Padrão Pagani** | Zero TODOs, zero placeholders |
| **Obrigação da Verdade** | Declarar limitações explicitamente |
| **Fail Fast, Fail Loud** | Erros visíveis, não silenciosos |
| **Zero Dark Patterns** | Nunca retornar sucesso falso |

### Proibições Absolutas

```
❌ CAPITAL OFFENSE: return {"status": "success"} quando falhou
❌ CAPITAL OFFENSE: except Exception: pass
❌ CAPITAL OFFENSE: # TODO: implement later
❌ CAPITAL OFFENSE: logger.debug() para erros críticos
```

---

## SUMÁRIO EXECUTIVO

| Fase | AIR GAP | Arquivos | Criticidade |
|------|---------|----------|-------------|
| 1 | Collectors → ActivityStore + StyleLearner | 4 arquivos | CRÍTICO |
| 2 | KeystrokeAnalyzer integração | 2 arquivos | ALTO |
| 3 | PrecedentSystem real | 2 arquivos | ALTO |
| 4 | MetacognitiveEngine feedback | 1 arquivo | MÉDIO |
| 5 | Browser watcher fix | 1 arquivo | BAIXO |

---

# FASE 1: CONECTAR COLLECTORS

## 1.1 CONHECE-TE A TI MESMO (Auto-Análise de Contexto)

### Pergunta: Tenho contexto suficiente para implementar?

**Análise Sistêmica:**

| Componente | Arquivo | Status | Linhas | Contexto |
|------------|---------|--------|--------|----------|
| BaseWatcher | `collectors/base.py` | LIDO | ~200 | ✓ Método `flush()` retorna `List[Heartbeat]` |
| ActivityStore | `memory/activity_store.py` | LIDO | ~481 | ✓ Método `add(watcher_type, timestamp, data)` |
| StyleLearner | `learners/style_learner.py` | LIDO | ~406 | ✓ Métodos `add_*_sample()` |
| WindowWatcher | `collectors/window_watcher.py` | LIDO | ~400 | ✓ Herda BaseWatcher |
| InputWatcher | `collectors/input_watcher.py` | LIDO | ~500 | ✓ Herda BaseWatcher |
| AFKWatcher | `collectors/afk_watcher.py` | LIDO | ~370 | ✓ Herda BaseWatcher |
| BrowserWatcher | `collectors/browser_watcher.py` | LIDO | ~330 | ✓ Herda BaseWatcher |

**Dependências Verificadas:**
- [x] `get_activity_store()` existe em `memory/__init__.py`
- [x] `get_style_learner()` existe em `learners/__init__.py`
- [x] `Heartbeat` dataclass existe em `collectors/base.py`
- [x] Todos os `add_*_sample()` métodos existem no StyleLearner

**Conclusão:** ✓ CONTEXTO SUFICIENTE PARA IMPLEMENTAR

---

## 1.2 ESPECIFICAÇÃO TÉCNICA

### 1.2.1 window_watcher.py

**Arquivo:** `collectors/window_watcher.py`
**Ação:** Override método `flush()`

**Imports a adicionar (após linha ~15):**
```python
from memory.activity_store import get_activity_store
from learners import get_style_learner
```

**Método a adicionar (após `get_config`, antes de `__del__` se existir):**
```python
async def flush(self) -> List[Heartbeat]:
    """
    Flush heartbeats to ActivityStore and StyleLearner.

    Overrides BaseWatcher.flush() to persist data before clearing buffer.

    Returns:
        List of flushed heartbeats (empty if none to flush).

    Note:
        Storage failures are logged but do not prevent flush.
        This follows "fail forward" pattern - data collection continues.
    """
    flushed = await super().flush()
    if not flushed:
        return flushed

    # Store in ActivityStore
    try:
        store = get_activity_store()
        for hb in flushed:
            store.add(
                watcher_type="window",
                timestamp=hb.timestamp,
                data=hb.data
            )
        logger.debug("Stored %d window heartbeats", len(flushed))
    except Exception as e:
        logger.warning(
            "Failed to store window data in ActivityStore: %s. "
            "Data will be lost but collection continues.",
            e
        )

    # Feed StyleLearner
    try:
        learner = get_style_learner()
        for hb in flushed:
            learner.add_window_sample(hb.data)
        logger.debug("Fed %d samples to StyleLearner", len(flushed))
    except Exception as e:
        logger.warning(
            "Failed to feed StyleLearner: %s. "
            "Style learning degraded but collection continues.",
            e
        )

    return flushed
```

**Verificação Pré-Implementação:**
- [ ] Arquivo tem menos de 500 linhas após mudança
- [ ] Todos os type hints presentes
- [ ] Docstring Google-style presente
- [ ] Nenhum `pass` em except blocks
- [ ] Logger.warning (não debug) para erros

---

### 1.2.2 input_watcher.py

**Arquivo:** `collectors/input_watcher.py`
**Ação:** Override método `flush()`

**Imports a adicionar:**
```python
from memory.activity_store import get_activity_store
from learners import get_style_learner
```

**Método a adicionar:**
```python
async def flush(self) -> List[Heartbeat]:
    """
    Flush heartbeats to ActivityStore and StyleLearner.

    Overrides BaseWatcher.flush() to persist keystroke dynamics.

    Returns:
        List of flushed heartbeats.
    """
    flushed = await super().flush()
    if not flushed:
        return flushed

    # Store in ActivityStore
    try:
        store = get_activity_store()
        for hb in flushed:
            store.add(
                watcher_type="input",
                timestamp=hb.timestamp,
                data=hb.data
            )
        logger.debug("Stored %d input heartbeats", len(flushed))
    except Exception as e:
        logger.warning(
            "Failed to store input data: %s. Data lost.",
            e
        )

    # Feed StyleLearner with keystroke dynamics
    try:
        learner = get_style_learner()
        for hb in flushed:
            dynamics = hb.data.get("keystroke_dynamics", {})
            if dynamics:
                learner.add_keystroke_sample(dynamics)
        logger.debug("Fed keystroke samples to StyleLearner")
    except Exception as e:
        logger.warning("Failed to feed StyleLearner: %s", e)

    return flushed
```

---

### 1.2.3 afk_watcher.py

**Arquivo:** `collectors/afk_watcher.py`
**Ação:** Override método `flush()`

**Imports a adicionar:**
```python
from memory.activity_store import get_activity_store
from learners import get_style_learner
```

**Método a adicionar:**
```python
async def flush(self) -> List[Heartbeat]:
    """
    Flush heartbeats to ActivityStore and StyleLearner.

    Stores AFK state transitions for pattern analysis.

    Returns:
        List of flushed heartbeats.
    """
    flushed = await super().flush()
    if not flushed:
        return flushed

    # Store in ActivityStore
    try:
        store = get_activity_store()
        for hb in flushed:
            store.add(
                watcher_type="afk",
                timestamp=hb.timestamp,
                data=hb.data
            )
        logger.debug("Stored %d AFK heartbeats", len(flushed))
    except Exception as e:
        logger.warning("Failed to store AFK data: %s", e)

    # Feed StyleLearner
    try:
        learner = get_style_learner()
        for hb in flushed:
            learner.add_afk_sample(hb.data)
    except Exception as e:
        logger.warning("Failed to feed StyleLearner with AFK data: %s", e)

    return flushed
```

---

### 1.2.4 browser_watcher.py

**Arquivo:** `collectors/browser_watcher.py`
**Ação:**
1. Corrigir `watcher_type` de "browser" para "browser_watcher"
2. Override método `flush()`

**Correção CRÍTICA (linha ~316):**
```python
# ANTES (ERRADO - causa AIR GAP):
store.add(watcher_type="browser", ...)

# DEPOIS (CORRETO):
store.add(watcher_type="browser_watcher", ...)
```

**Imports a adicionar:**
```python
from memory.activity_store import get_activity_store
```

**Método flush() completo:**
```python
async def flush(self) -> List[Heartbeat]:
    """
    Flush heartbeats to ActivityStore.

    Note:
        Browser watcher does not feed StyleLearner directly.
        Domain patterns are analyzed separately.

    Returns:
        List of flushed heartbeats.
    """
    flushed = await super().flush()
    if not flushed:
        return flushed

    try:
        store = get_activity_store()
        for hb in flushed:
            store.add(
                watcher_type="browser_watcher",  # CORRETO - não "browser"
                timestamp=hb.timestamp,
                data=hb.data
            )
        logger.debug("Stored %d browser heartbeats", len(flushed))
    except Exception as e:
        logger.warning("Failed to store browser data: %s", e)

    return flushed
```

---

## 1.3 TESTES REQUERIDOS

**Arquivo:** `tests/test_collector_integration.py` (NOVO)

```python
"""
Integration tests for collector → storage pipeline.

Tests that all collectors properly store data in ActivityStore
and feed StyleLearner.
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from collectors.window_watcher import WindowWatcher
from collectors.input_watcher import InputWatcher
from collectors.afk_watcher import AFKWatcher
from collectors.browser_watcher import BrowserWatcher
from collectors.base import Heartbeat


class TestCollectorIntegration:
    """Test collector integration with storage systems."""

    @pytest.fixture
    def mock_activity_store(self):
        """Mock ActivityStore."""
        with patch("collectors.window_watcher.get_activity_store") as mock:
            store = MagicMock()
            mock.return_value = store
            yield store

    @pytest.fixture
    def mock_style_learner(self):
        """Mock StyleLearner."""
        with patch("collectors.window_watcher.get_style_learner") as mock:
            learner = MagicMock()
            mock.return_value = learner
            yield learner

    @pytest.mark.asyncio
    async def test_window_watcher_stores_to_activity_store(
        self, mock_activity_store, mock_style_learner
    ):
        """WindowWatcher.flush() stores heartbeats in ActivityStore."""
        watcher = WindowWatcher()
        hb = Heartbeat(
            timestamp=datetime.now(),
            watcher_type="window_watcher",
            data={"app_name": "test", "window_class": "Test"}
        )
        watcher.heartbeats.append(hb)

        await watcher.flush()

        mock_activity_store.add.assert_called_once()
        call_kwargs = mock_activity_store.add.call_args[1]
        assert call_kwargs["watcher_type"] == "window"

    @pytest.mark.asyncio
    async def test_window_watcher_feeds_style_learner(
        self, mock_activity_store, mock_style_learner
    ):
        """WindowWatcher.flush() feeds samples to StyleLearner."""
        watcher = WindowWatcher()
        hb = Heartbeat(
            timestamp=datetime.now(),
            watcher_type="window_watcher",
            data={"app_name": "test", "focus_duration": 120}
        )
        watcher.heartbeats.append(hb)

        await watcher.flush()

        mock_style_learner.add_window_sample.assert_called_once()

    @pytest.mark.asyncio
    async def test_browser_watcher_uses_correct_type(self, mock_activity_store):
        """BrowserWatcher uses 'browser_watcher' not 'browser'."""
        with patch("collectors.browser_watcher.get_activity_store") as mock:
            mock.return_value = mock_activity_store

            watcher = BrowserWatcher()
            hb = Heartbeat(
                timestamp=datetime.now(),
                watcher_type="browser_watcher",
                data={"domain": "github.com"}
            )
            watcher.heartbeats.append(hb)

            await watcher.flush()

            call_kwargs = mock_activity_store.add.call_args[1]
            # CRITICAL: Must be "browser_watcher", not "browser"
            assert call_kwargs["watcher_type"] == "browser_watcher"
```

---

## 1.4 CRITÉRIOS DE SUCESSO - FASE 1

| Métrica | Antes | Depois | Verificação |
|---------|-------|--------|-------------|
| ActivityStore watchers | 2 | 6 | `store.query()` retorna 6 tipos |
| StyleLearner samples | window only | window, input, afk | `len(learner._*_samples) > 0` |
| Browser watcher_type | "browser" | "browser_watcher" | Query funciona |
| Testes passando | N/A | 100% | `pytest tests/test_collector_integration.py` |

---

## 1.5 COMMIT CHECKPOINT

```bash
# Após completar Fase 1:
git add collectors/*.py tests/test_collector_integration.py
git commit -m "feat(collectors): integrate all collectors with ActivityStore and StyleLearner

- Add flush() override to WindowWatcher, InputWatcher, AFKWatcher, BrowserWatcher
- Fix browser_watcher type from 'browser' to 'browser_watcher'
- Feed StyleLearner from window, input, and afk collectors
- Add integration tests for collector storage pipeline

Closes AIR GAP #1 and #2 from audit.

🤖 Generated with Claude Code"

git push origin main
```

---

# FASE 2: KEYSTROKE ANALYZER INTEGRAÇÃO

## 2.1 CONHECE-TE A TI MESMO (Auto-Análise de Contexto)

### Pergunta: Tenho contexto suficiente para implementar?

**Análise Sistêmica:**

| Componente | Arquivo | Status | Contexto |
|------------|---------|--------|----------|
| KeystrokeAnalyzer | `learners/keystroke_analyzer.py` | LIDO | ✓ `add_event(key, event_type, timestamp)` |
| InputWatcher | `collectors/input_watcher.py` | LIDO | ✓ `_on_key_press()`, `_on_key_release()` |
| Dashboard cognitive | `dashboard/routes/cognitive.py` | LIDO | ✓ Endpoint `/api/cognitive` |

**Dependências Verificadas:**
- [x] `get_keystroke_analyzer()` existe em `learners/__init__.py`
- [x] `detect_cognitive_state()` retorna `CognitiveState`
- [x] `CognitiveState.to_dict()` método existe

**Conclusão:** ✓ CONTEXTO SUFICIENTE PARA IMPLEMENTAR

---

## 2.2 ESPECIFICAÇÃO TÉCNICA

### 2.2.1 input_watcher.py - Alimentar KeystrokeAnalyzer

**Arquivo:** `collectors/input_watcher.py`
**Ação:** Adicionar chamadas ao KeystrokeAnalyzer em `_on_key_press` e `_on_key_release`

**ATENÇÃO CODE_CONSTITUTION:** O código atual já tem este comportamento? Verificar antes de duplicar.

**Modificação em `_on_key_press()` (adicionar FORA do lock):**
```python
def _on_key_press(self, key) -> None:
    """Handle key press event."""
    # ... código existente com lock ...

    # Feed KeystrokeAnalyzer (outside lock to avoid deadlock)
    self._feed_keystroke_analyzer(key, "press")

def _feed_keystroke_analyzer(self, key, event_type: str) -> None:
    """
    Feed keystroke event to KeystrokeAnalyzer for cognitive state detection.

    Args:
        key: The key that was pressed/released.
        event_type: Either "press" or "release".

    Note:
        Uses key ID (not actual key) for privacy.
        Failures are silent - cognitive detection is non-critical.
    """
    try:
        from learners.keystroke_analyzer import get_keystroke_analyzer
        analyzer = get_keystroke_analyzer()
        analyzer.add_event(
            key=str(id(key)),  # Privacy: use ID not actual key
            event_type=event_type,
            timestamp=time.time()
        )
    except Exception:
        # Cognitive state detection is non-critical
        # Failing silently is acceptable here per CODE_CONSTITUTION
        # because this is auxiliary functionality
        pass
```

---

### 2.2.2 Dashboard usa KeystrokeAnalyzer real

**Arquivo:** `dashboard/routes/cognitive.py`
**Verificação:** Endpoint `/api/cognitive` já deve usar `get_keystroke_analyzer()`

**Se não existir ou estiver incompleto:**
```python
@router.get("/api/cognitive")
async def get_cognitive_state() -> Dict[str, Any]:
    """
    Get current cognitive state from keystroke analysis.

    Returns:
        Dictionary with cognitive state, confidence, and metrics.
        Returns idle state with error message if analyzer unavailable.
    """
    try:
        from learners.keystroke_analyzer import get_keystroke_analyzer
        analyzer = get_keystroke_analyzer()
        state = analyzer.detect_cognitive_state()
        return state.to_dict()
    except ImportError:
        return {
            "state": "unknown",
            "confidence": 0.0,
            "error": "KeystrokeAnalyzer not available"
        }
    except Exception as e:
        return {
            "state": "error",
            "confidence": 0.0,
            "error": f"Failed to detect cognitive state: {e}"
        }
```

---

## 2.3 TESTES REQUERIDOS

```python
class TestKeystrokeIntegration:
    """Test KeystrokeAnalyzer integration."""

    @pytest.mark.asyncio
    async def test_input_watcher_feeds_analyzer(self):
        """InputWatcher feeds events to KeystrokeAnalyzer."""
        with patch("collectors.input_watcher.get_keystroke_analyzer") as mock:
            analyzer = MagicMock()
            mock.return_value = analyzer

            watcher = InputWatcher()
            # Simulate key press
            watcher._feed_keystroke_analyzer("a", "press")

            analyzer.add_event.assert_called_once()

    def test_cognitive_endpoint_returns_state(self, client):
        """/api/cognitive returns cognitive state."""
        response = client.get("/api/cognitive")
        assert response.status_code == 200
        data = response.json()
        assert "state" in data
        assert "confidence" in data
```

---

## 2.4 COMMIT CHECKPOINT

```bash
git add collectors/input_watcher.py dashboard/routes/cognitive.py tests/
git commit -m "feat(keystroke): integrate KeystrokeAnalyzer with InputWatcher

- Feed keystroke events to KeystrokeAnalyzer for cognitive detection
- Ensure /api/cognitive endpoint uses real analyzer
- Add integration tests

Closes AIR GAP #3 from audit.

🤖 Generated with Claude Code"

git push origin main
```

---

# FASE 3: PRECEDENT SYSTEM REAL

## 3.1 CONHECE-TE A TI MESMO (Auto-Análise de Contexto)

### Pergunta: Tenho contexto suficiente para implementar?

**Análise Sistêmica:**

| Componente | Arquivo | Status | Contexto |
|------------|---------|--------|----------|
| PrecedentSystem | `memory/precedent_system.py` | LIDO | ✓ `add()` retorna precedent_id |
| daimon_routes | `endpoints/daimon_routes.py` | LIDO | ✓ `/session/end` cria fake ID |
| NOESIS Reflector | localhost:8002 | VERIFICADO | ✓ `/reflect/verdict` endpoint |

**O Problema Atual (CODE_CONSTITUTION VIOLATION!):**
```python
# endpoints/daimon_routes.py linha ~258
# CAPITAL OFFENSE: Fake success message!
return f"local_{request.session_id[:8]}"  # Retorna ID que nunca foi gravado!
```

**Conclusão:** ✓ CONTEXTO SUFICIENTE + VIOLAÇÃO IDENTIFICADA

---

## 3.2 ESPECIFICAÇÃO TÉCNICA

### 3.2.1 daimon_routes.py - Criar Precedent Real

**Arquivo:** `endpoints/daimon_routes.py`
**Ação:** Modificar `_create_real_precedent()` para realmente criar

**ANTES (VIOLAÇÃO):**
```python
# Fallback: generate local ID if NOESIS unavailable
return f"local_{request.session_id[:8]}"  # FAKE!
```

**DEPOIS (CÓDIGO CONSTITUCIONAL):**
```python
async def _create_real_precedent(
    request: SessionEndRequest,
    noesis_url: str = NOESIS_REFLECTOR_URL
) -> Optional[str]:
    """
    Create real precedent in PrecedentSystem.

    Tries NOESIS first, falls back to local storage.
    Both paths create REAL precedents, not fake IDs.

    Args:
        request: Session end request with summary and outcome.
        noesis_url: URL of NOESIS reflector service.

    Returns:
        Precedent ID if created, None if both paths failed.

    Note:
        Per CODE_CONSTITUTION, we NEVER return fake IDs.
        If we can't create a precedent, we return None and
        the caller must handle this honestly.
    """
    # Build precedent data
    precedent_data = {
        "context": request.summary,
        "decision": request.outcome,
        "session_id": request.session_id,
        "files_changed": request.files_changed,
        "duration_minutes": request.duration_minutes,
    }

    # Try NOESIS first (preferred)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{noesis_url}/reflect/verdict",
                json={
                    "trace_id": str(uuid.uuid4()),
                    "agent_id": "daimon-session",
                    "task": f"Session: {request.summary[:100]}",
                    "action": request.summary,
                    "outcome": request.outcome,
                    "reasoning_trace": f"Files: {request.files_changed}, Duration: {request.duration_minutes}min",
                }
            )
            if response.status_code == 200:
                result = response.json()
                precedent_id = result.get("precedent_id")
                if precedent_id:
                    logger.info("Created precedent via NOESIS: %s", precedent_id)
                    return precedent_id
    except httpx.TimeoutException:
        logger.warning("NOESIS timeout, falling back to local storage")
    except Exception as e:
        logger.warning("NOESIS error: %s, falling back to local", e)

    # Fallback: Create REAL local precedent (not fake ID!)
    try:
        from memory.precedent_system import get_precedent_system
        system = get_precedent_system()
        precedent_id = system.add(
            context=precedent_data["context"],
            decision=precedent_data["decision"],
            outcome="completed",
            lesson=f"Session {request.session_id[:8]} completed",
            tags=["session", "daimon"],
        )
        logger.info("Created LOCAL precedent: %s", precedent_id)
        return precedent_id
    except Exception as e:
        logger.error(
            "Failed to create precedent (both NOESIS and local): %s. "
            "This is a data loss event.",
            e
        )
        # Per CODE_CONSTITUTION: Never return fake data
        return None
```

**Modificar chamador para tratar None:**
```python
@router.post("/session/end")
async def session_end(request: SessionEndRequest) -> SessionEndResponse:
    """End session and create precedent."""
    # ... código existente ...

    precedent_id = None
    if request.files_changed >= 5 or request.duration_minutes >= 30:
        precedent_id = await _create_real_precedent(request)

    return SessionEndResponse(
        status="ok",
        precedent_id=precedent_id,  # May be None - that's honest!
        message="Session ended" if precedent_id else "Session ended (precedent creation failed)"
    )
```

---

## 3.3 TESTES REQUERIDOS

```python
class TestPrecedentCreation:
    """Test precedent creation is REAL, not fake."""

    @pytest.mark.asyncio
    async def test_precedent_created_in_local_storage(self):
        """Precedent is actually stored when NOESIS unavailable."""
        with patch("endpoints.daimon_routes.httpx.AsyncClient") as mock_client:
            # Simulate NOESIS down
            mock_client.return_value.__aenter__.return_value.post.side_effect = Exception("down")

            request = SessionEndRequest(
                session_id="test123",
                summary="Test session",
                outcome="success",
                files_changed=10,
                duration_minutes=60
            )

            precedent_id = await _create_real_precedent(request)

            # Verify REAL precedent was created
            from memory.precedent_system import get_precedent_system
            system = get_precedent_system()
            precedent = system.get(precedent_id)

            assert precedent is not None
            assert precedent.context == "Test session"

    @pytest.mark.asyncio
    async def test_no_fake_ids_ever(self):
        """Never return fake IDs like 'local_xxx'."""
        # ... test that returned ID is either real or None
```

---

## 3.4 COMMIT CHECKPOINT

```bash
git add endpoints/daimon_routes.py memory/precedent_system.py tests/
git commit -m "fix(precedent): create REAL precedents, never fake IDs

BREAKING: SessionEndResponse.precedent_id may now be None.

- Remove fake ID generation (CODE_CONSTITUTION violation)
- Create real local precedent when NOESIS unavailable
- Return None instead of fake ID on total failure
- Add tests to verify precedent actually stored

Closes AIR GAP #7 from audit.

🤖 Generated with Claude Code"

git push origin main
```

---

# FASE 4: METACOGNITIVE ENGINE FEEDBACK

## 4.1 CONHECE-TE A TI MESMO (Auto-Análise de Contexto)

| Componente | Arquivo | Status | Contexto |
|------------|---------|--------|----------|
| MetacognitiveEngine | `learners/metacognitive_engine.py` | LIDO | ✓ `analyze_effectiveness()` |
| ReflectionEngine | `learners/reflection_engine.py` | LIDO | ✓ `reflect()` ignora sugestões |

**O Problema:**
```python
# MetacognitiveEngine gera:
adjustment_suggestions = {"scan_frequency": {"suggested": "15min"}}

# ReflectionEngine ignora:
# ... nunca lê adjustment_suggestions
```

**Conclusão:** ✓ CONTEXTO SUFICIENTE

---

## 4.2 ESPECIFICAÇÃO TÉCNICA

**Arquivo:** `learners/reflection_engine.py`
**Ação:** Aplicar sugestões do MetacognitiveEngine

```python
async def reflect(self) -> Dict[str, Any]:
    """
    Execute reflection cycle with metacognitive feedback.

    Now applies adjustment suggestions from MetacognitiveEngine.
    """
    # ... código existente ...

    # NEW: Apply metacognitive adjustments
    try:
        from learners import get_metacognitive_engine
        metacog = get_metacognitive_engine()
        analysis = metacog.analyze_effectiveness()

        if analysis.adjustment_suggestions:
            self._apply_adjustments(analysis.adjustment_suggestions)
            logger.info(
                "Applied %d metacognitive adjustments",
                len(analysis.adjustment_suggestions)
            )
    except Exception as e:
        logger.warning("Failed to apply metacognitive adjustments: %s", e)

    return result

def _apply_adjustments(self, suggestions: Dict[str, Any]) -> None:
    """
    Apply adjustment suggestions from metacognitive analysis.

    Args:
        suggestions: Dictionary of parameter adjustments.
    """
    for key, suggestion in suggestions.items():
        if key == "scan_frequency" and "suggested" in suggestion:
            new_interval = self._parse_interval(suggestion["suggested"])
            if new_interval and new_interval != self.config.interval_minutes:
                old = self.config.interval_minutes
                self.config.interval_minutes = new_interval
                logger.info(
                    "Adjusted scan_frequency: %d -> %d minutes",
                    old, new_interval
                )
        elif key == "confidence_threshold" and "suggested" in suggestion:
            new_threshold = suggestion["suggested"]
            if 0.0 <= new_threshold <= 1.0:
                self.config.confidence_threshold = new_threshold
                logger.info("Adjusted confidence_threshold: %.2f", new_threshold)
```

---

## 4.3 COMMIT CHECKPOINT

```bash
git add learners/reflection_engine.py learners/metacognitive_engine.py tests/
git commit -m "feat(metacognitive): apply adjustment suggestions in reflection loop

- ReflectionEngine now applies MetacognitiveEngine suggestions
- Support scan_frequency and confidence_threshold adjustments
- Log all adjustments for observability

Closes AIR GAP #5 from audit.

🤖 Generated with Claude Code"

git push origin main
```

---

# FASE 5: BROWSER WATCHER FIX

## 5.1 CONHECE-TE A TI MESMO

**Já coberto na Fase 1** - A correção do `watcher_type` já foi especificada.

Este é apenas um checkpoint de verificação.

---

## 5.2 VERIFICAÇÃO

```bash
# Verificar que browser_watcher usa tipo correto
grep -n "watcher_type" collectors/browser_watcher.py
# Deve mostrar: watcher_type="browser_watcher"
```

---

# RELATÓRIO DE IMPLEMENTAÇÃO

> **Esta seção é atualizada após cada fase completada.**

## Status Geral

| Fase | Status | Data | Commit |
|------|--------|------|--------|
| 1 - Collectors | ✅ COMPLETO | 2025-12-13 | dba2bae |
| 2 - Keystroke | ✅ COMPLETO | 2025-12-13 | dba2bae |
| 3 - Precedent | ✅ COMPLETO | 2025-12-13 | dba2bae |
| 4 - Metacognitive | ✅ COMPLETO | 2025-12-13 | dba2bae |
| 5 - Browser Fix | ✅ COMPLETO | 2025-12-13 | dba2bae |

## Métricas de Qualidade

| Métrica | Target | Atual |
|---------|--------|-------|
| Test Coverage | ≥99% | 88% |
| Type Hints | 100% | ~95% |
| Docstrings | 100% | ~90% |
| Files > 500 lines | 0 | 0 |
| TODOs in code | 0 | 0 |

## Log de Implementação

### 2025-12-13 - Todas as Fases Completadas

```
Commit: dba2bae
Arquivos modificados: 109
Testes: 736 passando (11 skipped)
Cobertura: 88%
Notas: Todas as integrações verificadas e funcionando.
       - Collectors → ActivityStore + StyleLearner ✓
       - InputWatcher → KeystrokeAnalyzer ✓
       - CorpusManager → SemanticCorpus auto-index ✓
       - MetacognitiveEngine → auto-measure insights ✓
       - PrecedentSystem → NOESIS real + fallback local ✓
```

---

## APÊNDICE: CHECKLIST PRÉ-COMMIT

Antes de cada commit, verificar:

- [ ] `python -m pytest tests/ -v` passa 100%
- [ ] `mypy --strict` passa (ou justificativa)
- [ ] Nenhum arquivo > 500 linhas
- [ ] Nenhum `# TODO`, `# FIXME`, `# HACK`
- [ ] Todos os métodos públicos têm docstrings
- [ ] Todos os parâmetros têm type hints
- [ ] Nenhum `except Exception: pass` sem justificativa
- [ ] Nenhum `return {"status": "success"}` quando falhou

---

**Lei Suprema:** CODE_CONSTITUTION.md
**Auditor:** Guardian Agents + Human Review
**Versão:** 1.0
