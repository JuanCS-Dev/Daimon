"""Consciousness API Package.

FastAPI endpoints for consciousness system monitoring.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from maximus_core_service.consciousness.system import ConsciousnessSystem

from .router import create_consciousness_api

__all__ = ["create_consciousness_api", "set_consciousness_components", "get_consciousness_dict"]

# Global consciousness system dict for API endpoints
_global_consciousness_dict: dict[str, Any] = {}


def set_consciousness_components(system: "ConsciousnessSystem") -> None:
    """Populate consciousness_system dict with real components after initialization.
    
    This function is called from main.py lifespan after ConsciousnessSystem.start().
    It bridges the gap between the system initialization and the router creation.
    
    Args:
        system: Initialized ConsciousnessSystem instance
    """
    global _global_consciousness_dict
    # FIX: Add full system object so endpoints can access all attributes including orchestrator
    _global_consciousness_dict["system"] = system
    _global_consciousness_dict["tig"] = system.tig_fabric
    _global_consciousness_dict["esgt"] = system.esgt_coordinator
    _global_consciousness_dict["arousal"] = system.arousal_controller
    _global_consciousness_dict["safety"] = system.safety_protocol
    _global_consciousness_dict["reactive"] = system.orchestrator
    _global_consciousness_dict["pfc"] = system.prefrontal_cortex
    _global_consciousness_dict["tom"] = system.tom_engine
    _global_consciousness_dict["metacog"] = system.metacog_monitor


def get_consciousness_dict() -> dict[str, Any]:
    """Get global consciousness system dict.
    
    Returns:
        Dictionary with consciousness system components
    """
    return _global_consciousness_dict
