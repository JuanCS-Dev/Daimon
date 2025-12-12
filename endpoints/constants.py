"""
DAIMON Constants - Shared Risk Keywords
=======================================

Centralized constants for DAIMON risk classification.

Follows CODE_CONSTITUTION: Single Source of Truth.
"""

from __future__ import annotations

from typing import List

# High-risk keywords that trigger emergence (salience 0.9)
HIGH_RISK_KEYWORDS: List[str] = [
    "delete",
    "drop",
    "rm -rf",
    "truncate",
    "production",
    "destroy",
    "wipe",
    "purge",
    "credential",
    "secret",
    "password",
]

# Medium-risk keywords for subtle mode (salience 0.6)
MEDIUM_RISK_KEYWORDS: List[str] = [
    "refactor",
    "migrate",
    "architecture",
    "auth",
    "security",
    "payment",
    "deploy",
    "database",
    "schema",
    "api",
]
