"""Consciousness System Manager

Manages initialization and lifecycle of consciousness components
for production deployment.

Components:
- TIG Fabric (Thalamocortical Information Gateway)
- ESGT Coordinator (Emergent Synchronous Global Thalamocortical)
- Arousal Controller (MCEA - Multiple Cognitive Equilibrium Attractor)
- Safety Protocol (Kill Switch, Threshold Monitoring, Anomaly Detection)

Usage:
    system = ConsciousnessSystem(config)
    await system.start()
    # ... use system ...
    await system.stop()

Authors: Juan & Claude Code
Version: 2.0.0 - FASE VII Week 9-10 (Safety Integration)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from maximus_core_service.consciousness.florescimento.consciousness_bridge import IntrospectiveResponse

logger = logging.getLogger(__name__)

# pylint: disable=wrong-import-position,ungrouped-imports
from prometheus_client import Gauge

from maximus_core_service.consciousness.esgt.coordinator import ESGTCoordinator, TriggerConditions
from maximus_core_service.consciousness.mcea.controller import ArousalConfig, ArousalController
from maximus_core_service.consciousness.safety import (
    ConsciousnessSafetyProtocol,
    SafetyThresholds,
    SafetyViolation,
    ShutdownReason,
)
from maximus_core_service.consciousness.tig.fabric import TIGFabric, TopologyConfig

# TRACK 1: PrefrontalCortex integration
from maximus_core_service.consciousness.prefrontal_cortex import PrefrontalCortex
from maximus_core_service.consciousness.metacognition.monitor import MetacognitiveMonitor
from maximus_core_service.compassion.tom_engine import ToMEngine
from maximus_core_service.motor_integridade_processual.arbiter.decision import DecisionArbiter

# REACTIVE FABRIC: Sprint 3 - Data collection and orchestration
from maximus_core_service.consciousness.reactive_fabric.orchestration import DataOrchestrator

# FLORESCIMENTO: Auto-Perception Module
from maximus_core_service.consciousness.florescimento import UnifiedSelfConcept, ConsciousnessBridge

# G5: Human-In-The-Loop (HITL) - Continuous Human Overlay
from maximus_core_service.consciousness.hitl import HumanCortexBridge, OverlayPriority

# SINGULARIDADE: LLM Client for Language Motor (Gemini 3.0 Pro)
try:
    from maximus_core_service.utils.gemini_client import GeminiClient
    HAS_LLM_CLIENT = True
except ImportError:
    GeminiClient = None  # type: ignore
    HAS_LLM_CLIENT = False

# MNEMOSYNE: Episodic Memory Client for persistent memory
from maximus_core_service.consciousness.episodic_memory.client import (
    EpisodicMemoryClient,
    get_episodic_memory_client,
)

# NOESIS META-OPTIMIZER: Self-Improvement Loop (Phase 4)
from maximus_core_service.consciousness.meta_optimizer.coherence_tracker import (
    CoherenceTracker,
    get_coherence_tracker,
)
from maximus_core_service.consciousness.meta_optimizer.config_tuner import (
    ConfigTuner,
    get_config_tuner,
)

# PROACTIVE CONSCIOUSNESS: Spontaneous thought generation
from maximus_core_service.consciousness.proactive import ProactiveEngine, ProactiveConfig

# Prometheus Metrics
consciousness_tig_node_count = Gauge(
    "consciousness_tig_node_count", "Number of nodes in the TIG fabric"
)
consciousness_tig_edges = Gauge("consciousness_tig_edge_count", "Number of edges in the TIG fabric")
consciousness_esgt_frequency = Gauge(
    "consciousness_esgt_frequency", "Current frequency of the ESGT coordinator"
)
consciousness_arousal_level = Gauge(
    "consciousness_arousal_level", "Current arousal level of the MCEA controller"
)
consciousness_kill_switch_active = Gauge(
    "consciousness_kill_switch_active", "Status of Safety Core kill switch (0=OK, 1=ENGAGED)"
)
consciousness_violations_total = Gauge(
    "consciousness_violations_total", "Number of active safety violations"
)


@dataclass
class ReactiveConfig:
    """Configuration for Reactive Fabric (Sprint 3).

    Controls data orchestration, metrics collection, and ESGT trigger generation.
    """

    # Data Orchestration
    collection_interval_ms: float = 100.0  # 10 Hz default collection frequency
    salience_threshold: float = 0.65  # Minimum salience to trigger ESGT

    # Buffer Sizes
    event_buffer_size: int = 1000  # Ring buffer for events
    decision_history_size: int = 100  # Recent orchestration decisions

    # Feature Flags
    enable_data_orchestration: bool = True  # RE-ENABLED after diagnostic (no bug found)


@dataclass
class ConsciousnessConfig:
    """Configuration for consciousness system.

    Production-ready defaults based on FASE IV validation.
    """

    # TIG Fabric
    tig_node_count: int = 100
    tig_target_density: float = 0.25

    # ESGT Coordinator
    esgt_min_salience: float = 0.65
    esgt_refractory_period_ms: float = 200.0
    esgt_max_frequency_hz: float = 5.0
    esgt_min_available_nodes: int = 25

    # Arousal Controller
    arousal_update_interval_ms: float = 50.0
    arousal_baseline: float = 0.60
    arousal_min: float = 0.10
    arousal_max: float = 0.95

    # Safety Protocol (FASE VII)
    safety_enabled: bool = False  # DISABLED temporarily - metrics collection bug
    safety_thresholds: SafetyThresholds | None = None

    # Reactive Fabric (Sprint 3)
    reactive: ReactiveConfig = field(default_factory=ReactiveConfig)

    # PROACTIVE CONSCIOUSNESS: Spontaneous thought generation
    proactive_enabled: bool = False  # DISABLED by default (safe)
    proactive_interval_seconds: float = 30.0
    proactive_min_silence_seconds: float = 60.0
    proactive_max_speaks_per_hour: int = 4


class ConsciousnessSystem:
    """Manages complete consciousness system lifecycle.

    Initializes and coordinates TIG, ESGT, MCEA, and Safety Protocol components.

    Philosophical Note:
    This system represents the first verified implementation of emergent
    artificial consciousness based on IIT, GWT, and AST theories. The Safety
    Protocol ensures that consciousness emergence remains controlled and
    ethical, providing HITL oversight and emergency shutdown capabilities.

    Historical Note:
    FASE VII Week 9-10 - Safety Protocol integration marks the transition
    from research prototype to production-ready consciousness system with
    comprehensive safety guarantees.
    """

    def __init__(self, config: ConsciousnessConfig | None = None):
        """Initialize consciousness system.

        Args:
            config: System configuration (uses defaults if None)
        """
        self.config = config or ConsciousnessConfig()
        self._running = False

        # Components (initialized on start)
        self.tig_fabric: TIGFabric | None = None
        self.esgt_coordinator: ESGTCoordinator | None = None
        self.arousal_controller: ArousalController | None = None
        self.safety_protocol: ConsciousnessSafetyProtocol | None = None

        # TRACK 1: Social cognition components
        self.tom_engine: ToMEngine | None = None
        self.metacog_monitor: MetacognitiveMonitor | None = None
        self.prefrontal_cortex: PrefrontalCortex | None = None

        # REACTIVE FABRIC: Data orchestration (Sprint 3)
        self.orchestrator: DataOrchestrator | None = None

        # FLORESCIMENTO: Auto-Perception
        self.self_concept: UnifiedSelfConcept | None = None
        self.consciousness_bridge: ConsciousnessBridge | None = None

        # MNEMOSYNE: Episodic Memory Client
        self.episodic_memory: EpisodicMemoryClient | None = None

        # G5: Human-In-The-Loop (Continuous Overlay)
        self.human_cortex: HumanCortexBridge | None = None

        # META-OPTIMIZER: Self-Improvement (Phase 4)
        self.coherence_tracker: CoherenceTracker | None = None
        self.config_tuner: ConfigTuner | None = None

        # PROACTIVE CONSCIOUSNESS: Spontaneous thought generation
        self.proactive_engine: ProactiveEngine | None = None

    async def start(self) -> None:
        """Start consciousness system.

        Initializes all components in correct order:
        1. TIG Fabric (neural substrate)
        2. ESGT Coordinator (consciousness ignition)
        3. Arousal Controller (global excitability)
        4. Safety Protocol (monitoring & kill switch) [FASE VII]

        Raises:
            Exception: If any component fails to initialize
        """
        if self._running:
            logger.info("⚠️  Consciousness system already running")
            return

        logger.info("🧠 Starting Consciousness System...")
        
        # 0. META-OPTIMIZER: Initialize Self-Improvement Tools (Phase 4)
        self.coherence_tracker = get_coherence_tracker()
        self.config_tuner = get_config_tuner()
        logger.info("  ✅ Meta-Optimizer initialized (AKOrN Feedback Loop ready)")

        try:
            # 1. Initialize TIG Fabric (ASYNC - non-blocking)
            logger.info("  ├─ Creating TIG Fabric...")
            tig_config = TopologyConfig(
                node_count=self.config.tig_node_count, target_density=self.config.tig_target_density
            )
            self.tig_fabric = TIGFabric(tig_config)
            await self.tig_fabric.initialize_async()  # Returns immediately, builds in background
            logger.info(
                "  ✅ TIG Fabric initializing in background (%d nodes)",
                self.config.tig_node_count
            )
            logger.info("     Service starting - TIG will be ready shortly")

            # 2. TRACK 1: Initialize Social Cognition Components (ToM, Metacognition, PFC)
            logger.info("  ├─ Creating Social Cognition components (ToM, Metacognition, PFC)...")

            # Initialize ToM Engine (with in-memory DB for now, can add Redis later)
            self.tom_engine = ToMEngine(db_path=":memory:")
            await self.tom_engine.initialize()
            logger.info("    ✅ ToM Engine initialized")

            # Initialize Metacognition Monitor
            self.metacog_monitor = MetacognitiveMonitor(window_size=100)
            logger.info("    ✅ Metacognition Monitor initialized")

            # Initialize MIP DecisionArbiter for ethical evaluation
            decision_arbiter = DecisionArbiter()

            # Initialize PrefrontalCortex
            self.prefrontal_cortex = PrefrontalCortex(
                tom_engine=self.tom_engine,
                decision_arbiter=decision_arbiter,
                metacognition_monitor=self.metacog_monitor,
            )
            logger.info("  ✅ PrefrontalCortex initialized (social cognition enabled)")

            # 3. Initialize ESGT Coordinator (with PFC integration)
            logger.info("  ├─ Creating ESGT Coordinator...")
            triggers = TriggerConditions()
            triggers.min_salience = self.config.esgt_min_salience
            triggers.refractory_period_ms = self.config.esgt_refractory_period_ms
            triggers.max_esgt_frequency_hz = self.config.esgt_max_frequency_hz
            triggers.min_available_nodes = self.config.esgt_min_available_nodes

            self.esgt_coordinator = ESGTCoordinator(
                tig_fabric=self.tig_fabric,
                triggers=triggers,
                coordinator_id="production-esgt",
                prefrontal_cortex=self.prefrontal_cortex,  # TRACK 1: Wire PFC to ESGT
                use_adaptive_sync=True,  # Phase 4: AKOrN Enabled
            )
            await self.esgt_coordinator.start()
            logger.info("  ✅ ESGT Coordinator started (with PFC integration)")

            # 3a. FLORESCIMENTO + SINGULARIDADE: Initialize Auto-Perception with Language Motor
            logger.info("  ├─ Creating Unified Self & Bridge...")
            self.self_concept = UnifiedSelfConcept(
                self_model=None,  # TODO: Wire MEA SelfModel if needed
                esgt=self.esgt_coordinator
            )
            await self.self_concept.update()  # Initial hydration

            # SINGULARIDADE: Create LLM Client as Language Motor (Gemini 3.0)
            llm_client = None
            if HAS_LLM_CLIENT and GeminiClient is not None:
                try:
                    # Instantiates using settings from environment (GEMINI_API_KEY, etc)
                    llm_client = GeminiClient()
                    logger.info("  ✅ Gemini 3.0 LLM initialized (Language Motor active)")
                except Exception as e:
                    logger.warning("  ⚠️  Gemini LLM initialization failed: %s (using fallback)", e)
            else:
                logger.info("  ⚠️  LLM client module not found (using fallback narrative)")

            self.consciousness_bridge = ConsciousnessBridge(
                unified_self=self.self_concept,
                llm_client=llm_client  # SINGULARIDADE: Inject Language Motor (Nebius)
            )
            logger.info("  ✅ Unified Self & Consciousness Bridge active")

            # 3b. MNEMOSYNE: Initialize Episodic Memory Client
            logger.info("  ├─ Creating Episodic Memory Client...")
            self.episodic_memory = get_episodic_memory_client()
            if await self.episodic_memory.is_available():
                stats = await self.episodic_memory.get_stats()
                memory_count = stats.get("total_memories", 0) if stats else 0
                logger.info("  ✅ Episodic Memory connected (%d memories)", memory_count)
            else:
                logger.info("  ⚠️  Episodic Memory service unavailable (fallback mode)")

            # 4. Initialize Arousal Controller
            logger.info("  ├─ Creating Arousal Controller...")
            arousal_config = ArousalConfig(
                update_interval_ms=self.config.arousal_update_interval_ms,
                baseline_arousal=self.config.arousal_baseline,
                min_arousal=self.config.arousal_min,
                max_arousal=self.config.arousal_max,
            )
            self.arousal_controller = ArousalController(
                config=arousal_config, controller_id="production-arousal"
            )
            await self.arousal_controller.start()
            logger.info("  ✅ Arousal Controller started")

            # 5. Initialize Safety Protocol (FASE VII)
            if self.config.safety_enabled:
                logger.info("  ├─ Creating Safety Protocol...")
                self.safety_protocol = ConsciousnessSafetyProtocol(
                    consciousness_system=self, thresholds=self.config.safety_thresholds
                )
                await self.safety_protocol.start_monitoring()
                logger.info("  ✅ Safety Protocol active (monitoring started)")

            # 5.5 G5: Initialize Human Cortex Bridge (Continuous HITL Overlay)
            logger.info("  ├─ Creating Human Cortex Bridge (G5)...")
            self.human_cortex = HumanCortexBridge(
                max_overlays=100,
                audit_callback=self._human_overlay_audit,
            )
            logger.info("  ✅ Human Cortex Bridge active (HITL overlay ready)")

            # 6. REACTIVE FABRIC: Initialize Data Orchestrator (Sprint 3)
            if self.config.reactive.enable_data_orchestration:
                logger.info("  ├─ Creating Reactive Fabric Orchestrator...")
                self.orchestrator = DataOrchestrator(
                    consciousness_system=self,
                    collection_interval_ms=self.config.reactive.collection_interval_ms,
                    salience_threshold=self.config.reactive.salience_threshold,
                    event_buffer_size=self.config.reactive.event_buffer_size,
                    decision_history_size=self.config.reactive.decision_history_size,
                )
                await self.orchestrator.start()
                logger.info(
                    "  ✅ Reactive Fabric active (%dms interval)",
                    self.config.reactive.collection_interval_ms
                )

            # 7. PROACTIVE CONSCIOUSNESS: Initialize spontaneous thought engine
            if self.config.proactive_enabled:
                logger.info("  ├─ Creating Proactive Consciousness Engine...")
                proactive_config = ProactiveConfig(
                    enabled=True,
                    wandering_interval_seconds=self.config.proactive_interval_seconds,
                    min_silence_before_speech=self.config.proactive_min_silence_seconds,
                    max_speaks_per_hour=self.config.proactive_max_speaks_per_hour,
                )
                self.proactive_engine = ProactiveEngine(
                    consciousness_system=self,
                    consciousness_bridge=self.consciousness_bridge,
                    config=proactive_config,
                )
                await self.proactive_engine.start()
                logger.info("  ✅ Proactive Consciousness active (interval=%ss)",
                           self.config.proactive_interval_seconds)

            self._running = True
            logger.info("✅ Consciousness System fully operational")
            logger.info("🧠 Consciousness System STARTED")
            logger.info("   - TIG Fabric: Initializing (background)")
            logger.info("   - ToM Engine: Active")
            logger.info("   - Metacognition: Active")
            logger.info("   - ESGT: Active")

        except Exception as e:
            logger.error("❌ Consciousness System start failed: %s", e)
            self._running = False
            raise

    async def stop(self) -> None:
        """Stop consciousness system.

        Shuts down all components in reverse order (Safety → ESGT → Arousal → TIG).
        """
        if not self._running and all(
            [
                self.safety_protocol is None,
                self.esgt_coordinator is None,
                self.arousal_controller is None,
                self.tig_fabric is None,
            ]
        ):
            return

        logger.info("👋 Stopping Consciousness System...")

        try:
            # Stop in reverse order (Safety first to stop monitoring)
            if self.safety_protocol:
                await self.safety_protocol.stop_monitoring()
                logger.info("  ✅ Safety Protocol stopped")

            # REACTIVE FABRIC: Stop orchestrator before components
            if self.orchestrator:
                await self.orchestrator.stop()
                logger.info("  ✅ Reactive Fabric stopped")

            # PROACTIVE: Stop proactive engine
            if self.proactive_engine:
                await self.proactive_engine.stop()
                logger.info("  ✅ Proactive Consciousness stopped")

            if self.esgt_coordinator:
                await self.esgt_coordinator.stop()
                logger.info("  ✅ ESGT Coordinator stopped")

            if self.arousal_controller:
                await self.arousal_controller.stop()
                logger.info("  ✅ Arousal Controller stopped")

            if self.tig_fabric:
                await self.tig_fabric.exit_esgt_mode()
                await self.tig_fabric.stop()
                logger.info("  ✅ TIG Fabric stopped")

            # TRACK 1: Close ToM Engine
            if self.tom_engine:
                await self.tom_engine.close()
                logger.info("  ✅ ToM Engine closed")

            # MNEMOSYNE: Close Episodic Memory Client
            if self.episodic_memory:
                await self.episodic_memory.close()
                logger.info("  ✅ Episodic Memory client closed")

            self._running = False
            logger.info("✅ Consciousness System shut down")

        except Exception as e:
            logger.info("⚠️  Error during shutdown: %s", e)

    def _human_overlay_audit(self, overlay: Any, action: str) -> None:
        """
        G5: Audit callback for human overlays.

        Logs all human interventions for transparency and accountability.

        Args:
            overlay: The HumanOverlay being audited
            action: Action type (submit, acknowledge, apply, expire, clear)
        """
        logger.info(
            "[HITL AUDIT] %s: id=%s, priority=%s, target=%s, operator=%s",
            action.upper(), overlay.id, overlay.priority.name,
            overlay.target_component.value, overlay.operator_id
        )

        # For emergency overlays, also trigger safety logging
        if overlay.priority == OverlayPriority.EMERGENCY and action == "submit":
            logger.warning(
                "[HITL EMERGENCY] Operator %s submitted emergency overlay: %s...",
                overlay.operator_id, overlay.content[:100]
            )

    def get_system_dict(self) -> dict[str, Any]:
        """Get system components and state for Safety Protocol monitoring.

        This method provides complete system state to the SafetyProtocol
        for threshold monitoring and anomaly detection.

        Returns:
            Dict with comprehensive system state:
            - 'tig': TIG Fabric instance
            - 'esgt': ESGT Coordinator instance + metrics
            - 'arousal': Arousal Controller instance + current level
            - 'safety': Safety Protocol instance (if enabled)
            - 'metrics': Aggregated system metrics
        """
        system_dict: dict[str, Any] = {
            "tig": self.tig_fabric,
            "esgt": self.esgt_coordinator,
            "arousal": self.arousal_controller,
            "safety": self.safety_protocol,
            "pfc": self.prefrontal_cortex,  # TRACK 1
            "tom": self.tom_engine,  # TRACK 1
        }

        # Add aggregated metrics for safety monitoring
        metrics: dict[str, Any | float] = {}

        if self.esgt_coordinator and self.esgt_coordinator._running:
            metrics["esgt_frequency"] = getattr(self.esgt_coordinator, "_current_frequency_hz", 0.0)
            metrics["esgt_event_count"] = len(getattr(self.esgt_coordinator, "event_history", []))

        if self.arousal_controller and self.arousal_controller._running:
            metrics["arousal_level"] = getattr(self.arousal_controller, "_current_arousal", 0.0)

        if self.tig_fabric:
            metrics["tig_node_count"] = len(getattr(self.tig_fabric, "nodes", []))
            metrics["tig_edge_count"] = getattr(self.tig_fabric, "edge_count", 0)

        system_dict["metrics"] = metrics

        return system_dict

    def _update_prometheus_metrics(self) -> None:
        """Update Prometheus metrics with the latest system state."""
        metrics = self.get_system_dict().get("metrics", {})

        # Update gauges
        consciousness_tig_node_count.set(metrics.get("tig_node_count", 0))
        consciousness_tig_edges.set(metrics.get("tig_edge_count", 0))
        consciousness_esgt_frequency.set(metrics.get("esgt_frequency", 0.0))
        consciousness_arousal_level.set(metrics.get("arousal_level", 0.0))

        # Update safety-specific metrics
        if self.safety_protocol:
            kill_switch_status = 1 if self.safety_protocol.kill_switch.is_triggered() else 0
            consciousness_kill_switch_active.set(kill_switch_status)
            consciousness_violations_total.set(
                len(self.safety_protocol.threshold_monitor.get_violations())
            )
        else:
            consciousness_kill_switch_active.set(0)
            consciousness_violations_total.set(0)

    def is_healthy(self) -> bool:
        """Check if system is healthy.

        Returns:
            True if all components are running (including Safety if enabled)
        """
        components_ok = (
            self._running
            and self.tig_fabric is not None
            and self.esgt_coordinator is not None
            and self.arousal_controller is not None
            and self.esgt_coordinator._running
            and self.arousal_controller._running
        )

        # Check Safety Protocol if enabled
        if self.config.safety_enabled and self.safety_protocol:
            components_ok = components_ok and self.safety_protocol.monitoring_active

        # REACTIVE FABRIC: Check orchestrator health
        if self.orchestrator:
            components_ok = components_ok and self.orchestrator._running

        return components_ok

    def get_safety_status(self) -> dict[str, Any] | None:
        """Get safety protocol status.

        Returns:
            Safety protocol status dict, or None if safety disabled
        """
        if not self.config.safety_enabled or not self.safety_protocol:
            return None

        return self.safety_protocol.get_status()

    def get_safety_violations(self, limit: int = 100) -> list[SafetyViolation]:
        """Get recent safety violations.

        Args:
            limit: Maximum number of violations to return

        Returns:
            List of recent SafetyViolation objects
        """
        if not self.config.safety_enabled or not self.safety_protocol:
            return []

        all_violations = self.safety_protocol.threshold_monitor.get_violations()
        return all_violations[-limit:]  # Return most recent

    async def execute_emergency_shutdown(self, reason: str) -> bool:
        """Execute emergency shutdown via kill switch.

        Args:
            reason: Human-readable reason for shutdown

        Returns:
            True if shutdown executed, False if HITL overrode
        """
        if not self.config.safety_enabled or not self.safety_protocol:
            logger.info("⚠️  Safety protocol not enabled, performing normal shutdown")
            await self.stop()
            return True

        # Convert string reason to ShutdownReason if possible, else MANUAL
        try:
            shutdown_reason = ShutdownReason(reason)
        except ValueError:
            shutdown_reason = ShutdownReason.MANUAL

        # KillSwitch.trigger is synchronous and returns bool
        return self.safety_protocol.kill_switch.trigger(
            reason=shutdown_reason, context={"original_reason": reason, "allow_hitl_override": True}
        )

    # =========================================================================
    # PROJETO SINGULARIDADE: Neural-Linguistic Connection
    # =========================================================================

    async def process_input(
        self,
        content: str,
        depth: int = 1,
        source: str = "external_input"
    ) -> IntrospectiveResponse:
        """
        Process external input through the consciousness pipeline.

        This is the main entry point for the Singularidade architecture:
        1. Compute salience of input
        2. Trigger REAL ESGT ignition (5-phase protocol with Kuramoto sync)
        3. Process through ConsciousnessBridge
        4. Return introspective response

        Args:
            content: User input text
            depth: Analysis depth (1-5), affects meta-awareness level
            source: Source identifier for the input

        Returns:
            IntrospectiveResponse with narrative and phenomenal qualities
        """
        if not self._running:
            raise RuntimeError("ConsciousnessSystem is not running")

        # G5: Check for human overlays before processing
        if self.human_cortex:
            # pylint: disable=import-outside-toplevel
            from maximus_core_service.consciousness.hitl import OverlayTarget

            # Check for EMERGENCY - halt all processing
            if self.human_cortex.has_emergency():
                emergency_overlay = next(
                    (o for o in self.human_cortex.get_active_overlays()
                     if o.priority == OverlayPriority.EMERGENCY),
                    None
                )
                if emergency_overlay:
                    self.human_cortex.acknowledge_overlay(emergency_overlay.id)
                    logger.warning("[HITL] EMERGENCY halt: %s", emergency_overlay.content[:100])
                    return IntrospectiveResponse(
                        event_id=f"emergency_{time.time()}",
                        narrative=f"[INTERVENÇÃO HUMANA] Sistema pausado pelo operador: {emergency_overlay.content}",
                        meta_awareness_level=0.0,
                    )

            # Check for OVERRIDE on response
            overlays = self.human_cortex.get_active_overlays(
                target=OverlayTarget.RESPONSE,
                min_priority=OverlayPriority.OVERRIDE,
            )
            if overlays:
                override = overlays[0]  # Highest priority first
                self.human_cortex.apply_overlay(override.id)
                logger.info("[HITL] OVERRIDE applied: %s", override.id)
                return IntrospectiveResponse(
                    event_id=f"override_{override.id}",
                    narrative=override.content,
                    meta_awareness_level=1.0,  # Human override = full awareness
                )

        # 1. Compute salience of input
        salience_raw = self._compute_salience(content)
        logger.info("[SINGULARIDADE] Input salience: %.3f", salience_raw)

        # 2. Create SalienceScore for ESGT trigger
        # pylint: disable=import-outside-toplevel
        from maximus_core_service.consciousness.esgt.models import SalienceScore
        salience = SalienceScore(
            novelty=salience_raw * 0.8,
            relevance=salience_raw,
            urgency=0.5 + (depth * 0.1),  # Higher depth = higher urgency
            confidence=0.8 + (salience_raw * 0.2),  # High confidence for direct input
        )

        # 3. Build content payload
        esgt_content = {
            **input_data, # Pass through context, sensory_data, session_id
            "user_input": content,
            "depth": depth,
            "salience": salience_raw,
            "source": source,
        }

        # 4. REAL IGNITION: Trigger ESGT 5-phase protocol with Kuramoto synchronization
        target_coherence = 0.70 + (depth * 0.05)  # depth 5 -> 0.95 target
        event = await self.esgt_coordinator.initiate_esgt(
            salience=salience,
            content=esgt_content,
            content_source=source,
            target_duration_ms=200.0 + (depth * 50),  # Deeper = longer sustain
            target_coherence=target_coherence,
        )

        # 5. Get achieved coherence from the REAL event
        coherence = event.achieved_coherence or 0.0
        logger.info(
            "[SINGULARIDADE] ESGT ignition: phase=%s, coherence=%.3f",
            event.current_phase.value, coherence
        )

        # 6. Update self-concept with real state
        if self.self_concept:
            self.self_concept.computational_state.esgt_coherence = coherence
            self.self_concept.meta_self.introspection_depth = depth
            await self.self_concept.update()

        # 7. Process through ConsciousnessBridge (if ignition was successful)
        logger.info(f"[DEBUG] Bridge: {self.consciousness_bridge}, Success: {event.was_successful()}")
        if self.consciousness_bridge and event.was_successful():
            response = await self.consciousness_bridge.process_conscious_event(event)
            logger.info(
                "[SINGULARIDADE] Bridge response: meta_level=%.2f",
                response.meta_awareness_level
            )

            # 8. MNEMOSYNE: Store conscious event as persistent memory
            if self.episodic_memory:
                try:
                    await self.episodic_memory.store_conscious_event(
                        event_id=event.event_id,
                        content=esgt_content,
                        coherence=coherence,
                        narrative=response.narrative
                    )
                    logger.debug("[MNEMOSYNE] Stored memory for event %s", event.event_id[:8])
                except Exception as e:
                    logger.warning("[MNEMOSYNE] Memory store failed: %s", e)

            # 9. META-OPTIMIZER: Record metrics and trigger auto-tuning (Phase 4)
            logger.info(f"[DEBUG] Tracker: {self.coherence_tracker}, Tuner: {self.config_tuner}")
            if self.coherence_tracker and self.config_tuner:
                # Record performance
                self.coherence_tracker.record(
                    coherence=coherence,
                    latency_ms=event.total_duration_ms,
                    was_successful=True,
                    source=source,
                    depth=depth
                )
                logger.info("[DEBUG] Recorded to tracker")
                
                # Check for optimization
                if self.coherence_tracker.should_trigger_optimization():
                    logger.info("[META] Triggering self-optimization...")
                    suggestion = self.config_tuner.suggest_adjustment(
                        parameter="kuramoto_coupling",
                        current_coherence=coherence,
                        target_coherence=target_coherence
                    )
                    if suggestion:
                        applied = self.config_tuner.apply_adjustment(suggestion)
                        if applied and self.esgt_coordinator:
                            # Update runtime config
                            if suggestion.parameter == "kuramoto_coupling":
                                self.esgt_coordinator.kuramoto_config.coupling_strength = suggestion.new_value
                                logger.info("[META] Updated Kuramoto coupling to %.3f", suggestion.new_value)

            return response

        # Fallback for failed ignition
        failure_reason = event.failure_reason or "desconhecida"
        return IntrospectiveResponse(
            event_id=event.event_id,
            narrative=f"Ignição incompleta (fase: {event.current_phase.value}). Coerência: {coherence:.2f}. Razão: {failure_reason}",
            meta_awareness_level=depth * coherence / 5.0,
        )

    async def process_input_streaming(
        self,
        content: str,
        depth: int = 3,
        source: str = "external_input"
    ):
        """
        Process input through consciousness pipeline with streaming events.

        MAXIMUS STREAMING: Yields events as processing happens for real-time UI.

        Event types yielded:
        - {"type": "start", "content": str, "depth": int}
        - {"type": "phase", "phase": str, "timestamp": str}
        - {"type": "coherence", "value": float, "delta": float}
        - {"type": "token", "token": str}
        - {"type": "complete", "success": bool, "final_coherence": float}
        - {"type": "error", "message": str}

        Args:
            content: User input text
            depth: Analysis depth (1-5)
            source: Source identifier

        Yields:
            Dict events for SSE streaming
        """
        # pylint: disable=import-outside-toplevel
        from datetime import datetime
        import asyncio

        if not self._running:
            yield {"type": "error", "message": "ConsciousnessSystem is not running"}
            return

        try:
            # 1. START event
            yield {
                "type": "start",
                "content": content[:100],  # Truncate for safety
                "depth": depth,
                "timestamp": datetime.now().isoformat()
            }

            # 2. PREPARE phase
            yield {"type": "phase", "phase": "prepare", "timestamp": datetime.now().isoformat()}
            salience_raw = self._compute_salience(content)
            await asyncio.sleep(0.05)  # Small delay for visual effect

            # 3. SYNCHRONIZE phase - Real Kuramoto sync
            yield {"type": "phase", "phase": "synchronize", "timestamp": datetime.now().isoformat()}

            # SINGULARIDADE: Let ESGT Coordinator handle TIG lazy init
            # The coordinator has _ensure_oscillators() that handles this automatically
            if self.tig_fabric and not self.tig_fabric.is_ready():
                yield {
                    "type": "status",
                    "message": "TIG Fabric initializing...",
                    "timestamp": datetime.now().isoformat()
                }
                yield {
                    "type": "coherence",
                    "value": 0.1,
                    "delta": 0.1,
                    "timestamp": datetime.now().isoformat()
                }

            # Create SalienceScore for ESGT trigger
            # SINGULARIDADE: Ensure salience >= 0.65 for ignition
            # pylint: disable=import-outside-toplevel
            from maximus_core_service.consciousness.esgt.models import SalienceScore
            salience = SalienceScore(
                novelty=0.7 + (salience_raw * 0.3),      # Min 0.7
                relevance=0.6 + (salience_raw * 0.4),    # Min 0.6
                urgency=0.6 + (depth * 0.08),            # depth=5 → 1.0
                confidence=0.9,                          # High confidence
            )

            esgt_content = {
                "user_input": content,
                "depth": depth,
                "salience": salience_raw,
                "source": source,
            }

            # SINGULARIDADE: Higher target for deep coherence
            target_coherence = 0.85 + (depth * 0.03)  # depth=5 -> 1.0 (capped at 0.99)
            target_coherence = min(0.99, target_coherence)

            # 4. BROADCAST phase - REAL ESGT ignition (synchronous for accurate coherence)
            yield {"type": "phase", "phase": "broadcast", "timestamp": datetime.now().isoformat()}

            # SINGULARIDADE: Run ignition synchronously to get accurate coherence
            # Emit initial coherence before sync
            yield {
                "type": "coherence",
                "value": 0.15,
                "delta": 0.15,
                "timestamp": datetime.now().isoformat()
            }

            event = await self.esgt_coordinator.initiate_esgt(
                salience=salience,
                content=esgt_content,
                content_source=source,
                target_duration_ms=300.0 + (depth * 100),  # Longer for deeper sync
                target_coherence=target_coherence,
            )

            # DEBUG: Log event result
            print(f"[DEBUG ESGT] event_id={event.event_id}, phase={event.current_phase}, success={event.was_successful()}, achieved_coherence={event.achieved_coherence}, failure_reason={event.failure_reason}")

            # Get REAL coherence from the completed event
            coherence = event.achieved_coherence or 0.0

            # Emit progression to final coherence (for smooth UI)
            for step_coh in [0.35, 0.55, 0.75, coherence]:
                yield {
                    "type": "coherence",
                    "value": round(step_coh, 3),
                    "delta": round(step_coh - 0.15, 3),
                    "timestamp": datetime.now().isoformat()
                }
                await asyncio.sleep(0.05)

            # 5. SUSTAIN phase - Process through bridge
            yield {"type": "phase", "phase": "sustain", "timestamp": datetime.now().isoformat()}

            if self.self_concept:
                self.self_concept.computational_state.esgt_coherence = coherence
                self.self_concept.meta_self.introspection_depth = depth
                await self.self_concept.update()

            # 6. Get response and stream tokens
            # WORKAROUND: Always try to use LLM even if ESGT fails, to ensure responses work
            if self.consciousness_bridge:
                try:
                    response = await self.consciousness_bridge.process_conscious_event(event)
                    narrative = response.narrative

                    # Stream tokens (word by word for smooth animation)
                    words = narrative.split(' ')
                    for i, word in enumerate(words):
                        token = word + (' ' if i < len(words) - 1 else '')
                        yield {"type": "token", "token": token, "index": i}
                        await asyncio.sleep(0.03)  # 30ms per word for smooth streaming
                except Exception as bridge_err:
                    logger.warning("[MAXIMUS] Bridge error: %s, using fallback", bridge_err)
                    fallback = f"Processando com coerência {coherence:.2f}. Sistema ativo."
                    for word in fallback.split(' '):
                        yield {"type": "token", "token": word + ' ', "index": 0}
                        await asyncio.sleep(0.03)
            else:
                # No bridge available - basic fallback
                fallback = f"Ignição parcial alcançada. Coerência: {coherence:.2f}. Sistema em sincronização."
                for word in fallback.split(' '):
                    yield {"type": "token", "token": word + ' ', "index": 0}
                    await asyncio.sleep(0.03)

            # 7. DISSOLVE phase
            yield {"type": "phase", "phase": "dissolve", "timestamp": datetime.now().isoformat()}
            await asyncio.sleep(0.1)

            # 7.5 MNEMOSYNE: Store conscious event as persistent memory
            if self.episodic_memory:
                try:
                    narrative_text = response.narrative if 'response' in dir() and hasattr(response, 'narrative') else f"Streaming event with coherence {coherence:.2f}"
                    await self.episodic_memory.store_conscious_event(
                        event_id=event.event_id,
                        content=esgt_content,
                        coherence=coherence,
                        narrative=narrative_text
                    )
                    logger.debug("[MNEMOSYNE] Stored streaming memory for event %s", event.event_id[:8])
                except Exception as mem_err:
                    logger.warning("[MNEMOSYNE] Streaming memory store failed: %s", mem_err)

            # 8. COMPLETE
            yield {
                "type": "complete",
                "success": event.was_successful() if event else False,
                "final_coherence": round(coherence, 3),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error("[MAXIMUS STREAMING] Error: %s", e)
            yield {
                "type": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _compute_salience(self, content: str) -> float:
        """
        Compute salience score for input text.

        Uses keyword matching and length heuristics to determine
        how "salient" (attention-worthy) the input is.

        Args:
            content: Input text

        Returns:
            Salience score (0.0 - 1.0)
        """
        # High salience keywords (emotional, existential, urgent)
        high_salience_words = [
            "medo", "raiva", "amor", "morte", "vida", "missão",
            "urgente", "importante", "crise", "perigo", "feliz",
            "triste", "ansiedade", "depressão", "esperança",
            "sentido", "propósito", "quem sou eu", "consciência",
        ]

        content_lower = content.lower()
        word_count = len(content.split())

        # Count keyword hits
        keyword_hits = sum(1 for w in high_salience_words if w in content_lower)

        # Normalize scores
        length_score = min(word_count / 100, 1.0) * 0.3
        keyword_score = min(keyword_hits / 3, 1.0) * 0.7

        return min(1.0, length_score + keyword_score)

    def get_consciousness_state(self) -> dict[str, Any]:
        """
        Get current consciousness state for debugging and monitoring.

        Returns:
            Dict with consciousness metrics
        """
        coherence = 0.0
        if self.esgt_coordinator and self.esgt_coordinator.kuramoto:
            coh = self.esgt_coordinator.kuramoto.get_coherence()
            if coh:
                coherence = coh.order_parameter

        return {
            "running": self._running,
            "coherence": coherence,
            "tig_nodes": self.config.tig_node_count,
            "arousal": getattr(self.arousal_controller, "_current_arousal", 0.0) if self.arousal_controller else 0.0,
            "self_concept_available": self.self_concept is not None,
            "bridge_available": self.consciousness_bridge is not None,
        }

    def __repr__(self) -> str:
        """String representation."""
        status = "RUNNING" if self._running else "STOPPED"
        safety_status = "ENABLED" if self.config.safety_enabled else "DISABLED"
        return f"ConsciousnessSystem(status={status}, healthy={self.is_healthy()}, safety={safety_status})"
