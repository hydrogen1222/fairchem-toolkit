"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.

UMAKit - VASP-like interface for FAIRChem UMA models.
"""

from __future__ import annotations

__version__ = "1.0.0"

__all__ = [
    "BatchRunner",
    "CalculationEngine",
    "EngineConfig",
    "IncarConfig",
    "JobManager",
    "MDRunner",
    "OptimizationRunner",
    "ProgressEvent",
    "SinglePointRunner",
    "UMACalculator",
    "calculate_adsorption_energy",
    "calculate_energy",
    "run_md",
    "run_optimization",
    "run_single_point",
]


def __getattr__(name: str):
    """Lazy import to avoid loading fairchem/torch at import time."""
    _imports = {
        "IncarConfig": ".config",
        "UMACalculator": ".calculator",
        "SinglePointRunner": ".runners.singlepoint",
        "OptimizationRunner": ".runners.optimization",
        "MDRunner": ".runners.md",
        "BatchRunner": ".runners.batch",
        "CalculationEngine": ".engine",
        "EngineConfig": ".engine",
        "ProgressEvent": ".protocols",
        "JobManager": ".jobs",
        "run_single_point": ".api",
        "run_optimization": ".api",
        "run_md": ".api",
        "calculate_energy": ".api",
        "calculate_adsorption_energy": ".api",
    }
    if name in _imports:
        import importlib  # noqa: PLC0415

        mod = importlib.import_module(_imports[name], __package__)
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
