"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.

Progress event protocol for UMA calculation runners.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class ProgressEvent:
    """Structured progress event emitted during calculations.

    Fields:
        phase: Current phase (loading_model, running, writing_output, done, error).
        message: Human-readable description.
        step: Current step number (None for indeterminate phases like SP).
        total_steps: Total expected steps (None for indeterminate phases).
        extra: Optional dict with phase-specific data (energy, fmax, temperature, etc.).
    """

    phase: str
    message: str
    step: int | None = None
    total_steps: int | None = None
    extra: dict | None = None


ProgressCallback = Callable[[ProgressEvent], None]
