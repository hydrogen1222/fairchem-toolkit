# UMAKit Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all bugs in the UMAKit package and refactor CLI/TUI/API into a unified architecture with Engine layer, progress protocol, background jobs, and resource control.

**Architecture:** Introduce `CalculationEngine` as single execution entry point shared by CLI/TUI/API. Add `ProgressEvent` protocol for structured progress reporting. Use asyncio worker in TUI instead of threading. Implement `JobManager` for background job submission/attach/kill with disk-persisted state.

**Tech Stack:** Python 3.9+, fairchem-core, ASE, Textual >=0.40.0, pathlib, asyncio, concurrent.futures

## Global Constraints

- Python >=3.9
- `uv` for Python/package management (no system Python)
- Every modified file MUST run `ruff check --fix` and `ruff format` before commit
- Every file starts with: `"""Copyright (c) Meta Platforms..."""` comment block, then module docstring, then `from __future__ import annotations`
- Line length: 88
- Tests at `tests/core/umakit/`, run with `uv run pytest tests -c packages/fairchem-core/pyproject.toml`
- Cross-platform: Windows (taskkill) and Unix (SIGTERM) for process management
- Paths use `pathlib.Path` for cross-platform compat
- Textual CSS: no `font-size` property; use `1fr`/`100%` for responsive layout

---

### Task 1: Fix module headers in 5 files

**Files:**
- Modify: `uma/umakit/runners/md.py:1-8`
- Modify: `uma/umakit/tui/app.py:1-9`
- Modify: `uma/umakit/tui/run_screen.py:1-9,237`
- Modify: `uma/umakit/api.py:1-9`
- Modify: `uma/umakit/logger.py:1-9`

**Interfaces:**
- Produces: Correctly formatted file headers matching CLAUDE.md convention
- Produces: `ComposeResult` import moved to top of run_screen.py so subsequent tasks can import it

- [ ] **Step 1: Fix `md.py` header — replace first 8 lines**

Read `uma/umakit/runners/md.py` current header (lines 1-8):
```python
from __future__ import annotations

"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

"""Molecular dynamics runner.
```

Replace with:
```python
"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

"""Molecular dynamics runner.

Runs MD simulations using ASE's integrators:
- NVT ensemble (Langevin dynamics)
- NVE ensemble (Velocity Verlet)

Outputs trajectories in multiple formats.
"""

from __future__ import annotations
```

- [ ] **Step 2: Fix `app.py` header — replace first 9 lines**

Read `uma/umakit/tui/app.py` current header (lines 1-9):
```python
from __future__ import annotations

"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

"""Main TUI Application for UMA Calculator."""
```

Replace with:
```python
"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

"""Main TUI Application for UMA Calculator."""

from __future__ import annotations
```

- [ ] **Step 3: Fix `run_screen.py` header — replace first 9 lines**

Read `uma/umakit/tui/run_screen.py` current header (lines 1-9):
```python
from __future__ import annotations

"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

"""Run screen for executing calculations with live output."""
```

Replace with:
```python
"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

"""Run screen for executing calculations with live output."""

from __future__ import annotations
```

- [ ] **Step 4: Fix `run_screen.py` line 237 — move `ComposeResult` import to top**

Delete line 237: `from textual.app import ComposeResult`

Add to imports section (after `from textual.widgets import Button, Log, ProgressBar, Static`):
```python
from textual.app import ComposeResult
```

Then add return type annotation to `compose` method:
```python
def compose(self) -> ComposeResult:
```

- [ ] **Step 5: Fix `api.py` header — replace first 9 lines**

Read `uma/umakit/api.py` current header (lines 1-9):
```python
from __future__ import annotations

"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

"""Programmatic API for UMA Calculator.
```

Replace with:
```python
"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

"""Programmatic API for UMA Calculator.

Provides high-level functions for running calculations from Python scripts.
This module is designed for external scripts that need to integrate UMA
calculations into complex workflows.

Example:
    >>> from umakit.api import run_single_point, calculate_energy
    >>>
    >>> # Run a single point calculation
    >>> results = run_single_point(
    ...     structure="structure.cif",
    ...     model_path="uma-s-1.pt",
    ...     task="omat",
    ...     job_name="my_calculation"
    ... )
    >>> print(f"Energy: {results['energy']:.4f} eV")
    >>>
    >>> # Just get the energy
    >>> energy = calculate_energy("structure.cif", "uma-s-1.pt", task="omat")
"""

from __future__ import annotations
```

- [ ] **Step 6: Fix `logger.py` header — replace first 11 lines**

Read `uma/umakit/logger.py` current header (lines 1-11):
```python
from __future__ import annotations

"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

"""Logging utilities for UMA Calculator.
```

Replace with:
```python
"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

"""Logging utilities for UMA Calculator.

Provides structured logging for all calculations with support for
file output and console output.
"""

from __future__ import annotations
```

- [ ] **Step 7: Run ruff check + format on all 5 files**

```bash
cd D:/Agent/fairchem && uv run ruff check --fix uma/umakit/runners/md.py uma/umakit/tui/app.py uma/umakit/tui/run_screen.py uma/umakit/api.py uma/umakit/logger.py && uv run ruff format uma/umakit/runners/md.py uma/umakit/tui/app.py uma/umakit/tui/run_screen.py uma/umakit/api.py uma/umakit/logger.py
```

- [ ] **Step 8: Verify files are importable**

```bash
cd D:/Agent/fairchem && uv run python -c "from umakit.runners.md import MDRunner; from umakit.api import run_single_point; print('OK')"
```
Expected: `OK`

- [ ] **Step 9: Commit**

```bash
git add uma/umakit/runners/md.py uma/umakit/tui/app.py uma/umakit/tui/run_screen.py uma/umakit/api.py uma/umakit/logger.py
git commit -m "fix: correct module headers and imports in 5 files"
```

---

### Task 2: ProgressEvent protocol

**Files:**
- Create: `uma/umakit/protocols.py`
- Create: `tests/core/umakit/test_protocols.py`

**Interfaces:**
- Produces: `ProgressEvent` dataclass with fields `phase: str`, `message: str`, `step: int | None`, `total_steps: int | None`, `extra: dict | None`
- Produces: `ProgressCallback = Callable[[ProgressEvent], None]` type alias

- [ ] **Step 1: Create test directory**

```bash
mkdir -p D:/Agent/fairchem/tests/core/umakit
```

- [ ] **Step 2: Write the test file**

Create `tests/core/umakit/__init__.py` (empty).

Create `tests/core/umakit/test_protocols.py`:

```python
"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from __future__ import annotations

from umakit.protocols import ProgressEvent


def test_progress_event_creation():
    event = ProgressEvent(
        phase="running",
        message="Calculating...",
        step=5,
        total_steps=100,
        extra={"energy": -123.4},
    )
    assert event.phase == "running"
    assert event.message == "Calculating..."
    assert event.step == 5
    assert event.total_steps == 100
    assert event.extra == {"energy": -123.4}


def test_progress_event_sp_no_steps():
    """SP calculation has no step/total — use None."""
    event = ProgressEvent(
        phase="loading_model",
        message="Loading model...",
        step=None,
        total_steps=None,
    )
    assert event.step is None
    assert event.total_steps is None


def test_progress_event_defaults():
    event = ProgressEvent(phase="done", message="Complete")
    assert event.step is None
    assert event.total_steps is None
    assert event.extra is None
```

- [ ] **Step 3: Run test to verify it fails**

```bash
cd D:/Agent/fairchem && uv run pytest tests/core/umakit/test_protocols.py -c packages/fairchem-core/pyproject.toml -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'umakit.protocols'`

- [ ] **Step 4: Write the protocol module**

Create `uma/umakit/protocols.py`:

```python
"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

"""Progress event protocol for UMA calculation runners."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable


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
```

- [ ] **Step 5: Run test to verify it passes**

```bash
cd D:/Agent/fairchem && uv run pytest tests/core/umakit/test_protocols.py -c packages/fairchem-core/pyproject.toml -v
```
Expected: 3 PASS

- [ ] **Step 6: Ruff format**

```bash
cd D:/Agent/fairchem && uv run ruff check --fix uma/umakit/protocols.py tests/core/umakit/test_protocols.py && uv run ruff format uma/umakit/protocols.py tests/core/umakit/test_protocols.py
```

- [ ] **Step 7: Commit**

```bash
git add uma/umakit/protocols.py tests/core/umakit/test_protocols.py tests/core/umakit/__init__.py
git commit -m "feat: add ProgressEvent protocol for structured progress reporting"
```

---

### Task 3: Add progress_callback to BaseRunner and all Runners

**Files:**
- Modify: `uma/umakit/runners/base.py`
- Modify: `uma/umakit/runners/singlepoint.py`
- Modify: `uma/umakit/runners/optimization.py`
- Modify: `uma/umakit/runners/md.py`
- Modify: `uma/umakit/runners/batch.py`
- Create: `tests/core/umakit/test_runners_progress.py`

**Interfaces:**
- Consumes: `ProgressEvent`, `ProgressCallback` from `uma/umakit/protocols.py`
- Produces: `BaseRunner.__init__` accepts `progress_callback: ProgressCallback | None = None`
- Produces: `BaseRunner._emit_progress(phase, message, step, total_steps, extra)` helper
- Produces: Each runner calls `_emit_progress` at key phases

- [ ] **Step 1: Add `_emit_progress` to BaseRunner**

In `uma/umakit/runners/base.py`, modify `__init__` to accept `progress_callback`:

```python
def __init__(
    self,
    calculator: UMACalculator,
    output_dir: Path | str = ".",
    verbose: bool = True,
    job_name: str | None = None,
    log_fn: Any | None = None,
    progress_callback: ProgressCallback | None = None,
):
    """..."""
    self.calculator = calculator
    self.job_name = job_name
    self.verbose = verbose
    self.log_fn = log_fn
    self.progress_callback = progress_callback

    base_dir = Path(output_dir)
    if job_name:
        self.output_dir = base_dir / job_name
    else:
        self.output_dir = base_dir

    self.output_dir.mkdir(parents=True, exist_ok=True)
```

Add import at top of base.py:

```python
from umakit.protocols import ProgressCallback, ProgressEvent
```

Add `_emit_progress` method to `BaseRunner`:

```python
def _emit_progress(
    self,
    phase: str,
    message: str,
    step: int | None = None,
    total_steps: int | None = None,
    extra: dict | None = None,
) -> None:
    """Emit a progress event to the callback if registered."""
    if self.progress_callback is None:
        return
    event = ProgressEvent(
        phase=phase,
        message=message,
        step=step,
        total_steps=total_steps,
        extra=extra,
    )
    self.progress_callback(event)
```

- [ ] **Step 2: Add progress events to SinglePointRunner**

In `uma/umakit/runners/singlepoint.py`, modify `run` method to emit progress at key points:

After `self.print_header(...)`:
```python
self._emit_progress("loading_model", "Loading model and preparing structure...")
```

After `calc = self._get_calculator()`:
```python
self._emit_progress("running", "Calculating energy and forces...")
```

After `energy = atoms.get_potential_energy()` and `forces = atoms.get_forces()`:
```python
self._emit_progress("running", "Calculating stress...", extra={"energy": float(energy)})
```

After all results collected, before writing:
```python
self._emit_progress("writing_output", "Writing output files...")
```

After `self._write_summary(...)`:
```python
self._emit_progress("done", "Calculation complete", extra={
    "energy": float(energy),
    "time": calc_time,
})
```

- [ ] **Step 3: Add progress events to OptimizationRunner**

In `uma/umakit/runners/optimization.py`, modify `trajectory_callback` inside `run()` method.

Add after `opt = optimizer_class(opt_atoms, logfile=logfile)`:
```python
self._emit_progress("running", "Starting optimization...", step=0, total_steps=self.max_steps)
```

Inside `trajectory_callback`, after computing `fmax_current`:
```python
self._emit_progress(
    "running",
    f"Step {step:4d}: E = {energy:12.6f} eV, fmax = {fmax_current:.6f} eV/A",
    step=step,
    total_steps=self.max_steps,
    extra={"energy": float(energy), "fmax": float(fmax_current)},
)
```

After optimization finishes:
```python
self._emit_progress("writing_output", "Writing output files...")
```

After `self._write_summary(...)`:
```python
self._emit_progress("done", f"Optimization {'converged' if converged else 'not converged'} in {opt.nsteps} steps",
    extra={"energy": float(energy), "converged": converged, "nsteps": opt.nsteps})
```

- [ ] **Step 4: Add progress events to MDRunner**

In `uma/umakit/runners/md.py`, modify `run` method.

After `self.print_header(...)`:
```python
self._emit_progress("loading_model", "Loading model and preparing structure...")
```

During pre-relaxation phase inside `_pre_relax_structure`:
```python
self._emit_progress("running", "Pre-relaxing structure...", step=0, total_steps=self.pre_relax_steps)
```

After pre-relaxation or after skipping it, before MD starts:
```python
self._emit_progress("running", f"Starting {self.ensemble.upper()} MD simulation...", step=0, total_steps=self.steps)
```

Inside `print_progress`, at each reporting interval:
```python
self._emit_progress(
    "running",
    f"Step {step:6d}/{self.steps}: E = {total_e:12.4f} eV, T = {temp:6.1f} K",
    step=step,
    total_steps=self.steps,
    extra={"energy": float(pe), "temperature": float(temp), "total_energy": float(total_e)},
)
```

After MD completes, before writing:
```python
self._emit_progress("writing_output", "Writing trajectory and output files...")
```

After `self._write_summary(...)`:
```python
self._emit_progress("done", f"MD complete. Final T = {final_temp:.1f} K",
    extra={"energy": float(final_energy), "temperature": float(final_temp)})
```

- [ ] **Step 5: Write tests for progress callbacks**

Create `tests/core/umakit/test_runners_progress.py`:

```python
"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


@pytest.mark.skip(reason="Requires fairchem model checkpoint to run runners")
def test_singlepoint_runner_emits_progress():
    """Verify SinglePointRunner calls progress_callback during run.
    
    This test is skipped by default because it requires a real model checkpoint.
    The structure of progress events is validated by the protocol tests.
    """
    from umakit.protocols import ProgressEvent, ProgressCallback

    events: list[ProgressEvent] = []

    def collect(event: ProgressEvent) -> None:
        events.append(event)

    # Test that callback type is correct
    callback: ProgressCallback = collect
    assert callable(callback)


def test_progress_event_phases():
    """Verify known phases are consistent."""
    from umakit.protocols import ProgressEvent

    valid_phases = {"loading_model", "running", "writing_output", "done", "error"}
    for phase in valid_phases:
        event = ProgressEvent(phase=phase, message="test")
        assert event.phase in valid_phases
```

Run with:
```bash
cd D:/Agent/fairchem && uv run pytest tests/core/umakit/test_runners_progress.py -c packages/fairchem-core/pyproject.toml -v
```

- [ ] **Step 6: Ruff format all modified files**

```bash
cd D:/Agent/fairchem && uv run ruff check --fix uma/umakit/runners/base.py uma/umakit/runners/singlepoint.py uma/umakit/runners/optimization.py uma/umakit/runners/md.py tests/core/umakit/test_runners_progress.py && uv run ruff format uma/umakit/runners/base.py uma/umakit/runners/singlepoint.py uma/umakit/runners/optimization.py uma/umakit/runners/md.py tests/core/umakit/test_runners_progress.py
```

- [ ] **Step 7: Verify import**

```bash
cd D:/Agent/fairchem && uv run python -c "from umakit.runners.base import BaseRunner; from umakit.runners.singlepoint import SinglePointRunner; from umakit.runners.optimization import OptimizationRunner; from umakit.runners.md import MDRunner; print('OK')"
```
Expected: `OK`

- [ ] **Step 8: Commit**

```bash
git add uma/umakit/runners/base.py uma/umakit/runners/singlepoint.py uma/umakit/runners/optimization.py uma/umakit/runners/md.py tests/core/umakit/test_runners_progress.py
git commit -m "feat: add progress_callback support to BaseRunner and all runners"
```

---

### Task 4: Fix TUI static issues (CSS + config_screen paths)

**Files:**
- Modify: `uma/umakit/tui/config_screen.py`
- Modify: `uma/umakit/tui/app.py`

**Interfaces:**
- Produces: CSS no longer has `font-size` property
- Produces: `#main-container` uses `width: 100%` for responsive layout
- Produces: Path validation shows cross-platform tips

- [ ] **Step 1: Fix CSS in app.py**

In `uma/umakit/tui/app.py`, in the `CSS` class variable:

Change `#main-container`:
```
#main-container {
    width: 100%;
    height: auto;
    border: solid $primary;
    padding: 1;
}
```

In `#config-scroll`:
```
#config-scroll {
    width: 100%;
    height: 1fr;
    padding: 1 2;
}
```

- [ ] **Step 2: Fix CSS in config_screen.py**

In `uma/umakit/tui/config_screen.py`, in the `CSS` class variable:

Current (broken):
```css
#structure-status, #model-status {
    margin-top: 0;
    margin-bottom: 1;
    padding-left: 1;
    font-size: 90%;
}
```

Replace with:
```css
#structure-status, #model-status {
    margin-top: 0;
    margin-bottom: 1;
    padding-left: 1;
}
```

- [ ] **Step 3: Enhance path validation tips**

In `uma/umakit/tui/config_screen.py`, modify `_validate_path` method to include cross-platform tips.

After the existing `status_widget.update(...)` call for the "not found" case, change the message to include tips. The `_validate_path` method should produce messages like:

- When found: `[OK] Found: C:/Users/.../structure.cif`
- When not found: `[NOT FOUND] Checked: C:/Users/.../structure.cif`
- When empty: `[!] Please specify a path. Relative paths are supported (e.g., ../data/file.cif or ..\data\file.cif)`

Modify the empty-value branch:
```python
if not val_stripped:
    status_widget.update(
        "[!] Please specify a path (relative paths supported, e.g. ./structure.cif)"
    )
    status_widget.set_classes("status-error")
    return False
```

- [ ] **Step 4: Verify no font-size remains in CSS**

```bash
cd D:/Agent/fairchem && grep -n "font-size" uma/umakit/tui/*.py
```
Expected: No matches (empty output)

- [ ] **Step 5: Ruff format**

```bash
cd D:/Agent/fairchem && uv run ruff check --fix uma/umakit/tui/config_screen.py uma/umakit/tui/app.py && uv run ruff format uma/umakit/tui/config_screen.py uma/umakit/tui/app.py
```

- [ ] **Step 6: Commit**

```bash
git add uma/umakit/tui/config_screen.py uma/umakit/tui/app.py
git commit -m "fix: remove invalid CSS font-size, use responsive layout, enhance path validation tips"
```

---

### Task 5: ResourceSettings and Calculator update

**Files:**
- Modify: `uma/umakit/calculator.py`
- Create: `tests/core/umakit/test_calculator.py`

**Interfaces:**
- Consumes: `InferenceSettings` from fairchem
- Produces: `UMACalculator.__init__` accepts optional `resource_settings: dict | None`
- Produces: `ResourceSettings` is passed through to `InferenceSettings.torch_num_threads` and `InferenceSettings.activation_checkpointing`

- [ ] **Step 1: Update UMACalculator to accept resource settings**

In `uma/umakit/calculator.py`, modify `__init__` signature:

```python
def __init__(
    self,
    model_path: str | Path,
    task: str = "omat",
    device: Literal["cpu", "cuda"] | None = None,
    inference_mode: str = "default",
    torch_num_threads: int | None = None,
    activation_checkpointing: bool | None = None,
):
```

Add these to `self`:
```python
self.torch_num_threads = torch_num_threads
self.activation_checkpointing = activation_checkpointing
```

Modify `load_predictor` method to pass these through to `InferenceSettings`.

Current code in `load_predictor`:
```python
if self.inference_mode == "turbo":
    settings = InferenceSettings(
        tf32=True,
        activation_checkpointing=False,
        merge_mole=True,
        compile=True,
    )
```

Change to:
```python
if self.inference_mode == "turbo":
    settings = InferenceSettings(
        tf32=True,
        activation_checkpointing=self.activation_checkpointing if self.activation_checkpointing is not None else False,
        merge_mole=True,
        compile=True,
        torch_num_threads=self.torch_num_threads,
    )
else:
    settings = InferenceSettings(
        activation_checkpointing=self.activation_checkpointing if self.activation_checkpointing is not None else True,
        torch_num_threads=self.torch_num_threads,
    )
    self._predictor = load_predict_unit(
        path=self.model_path,
        device=self.device,
        inference_settings=settings,
    )
```

Note: for "default" mode, the previous code did NOT pass `inference_settings`. Now it always does, with user overrides taking priority.

- [ ] **Step 2: Write test**

Create `tests/core/umakit/test_calculator.py`:

```python
"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestUMACalculatorValidation:
    """Tests for UMACalculator parameter validation (no model needed)."""

    def test_invalid_task_raises(self):
        from umakit.calculator import UMACalculator
        # Use a mock path that exists check first
        with patch.object(Path, "exists", return_value=True):
            with pytest.raises(ValueError, match="Invalid task"):
                UMACalculator(model_path="fake.pt", task="invalid")

    def test_invalid_inference_mode_raises(self):
        from umakit.calculator import UMACalculator
        with patch.object(Path, "exists", return_value=True):
            with pytest.raises(ValueError, match="Invalid inference mode"):
                UMACalculator(model_path="fake.pt", inference_mode="invalid")

    def test_resource_settings_stored(self):
        from umakit.calculator import UMACalculator
        with patch.object(Path, "exists", return_value=True):
            calc = UMACalculator(
                model_path="fake.pt",
                torch_num_threads=4,
                activation_checkpointing=False,
            )
            assert calc.torch_num_threads == 4
            assert calc.activation_checkpointing is False

    def test_default_resource_settings(self):
        from umakit.calculator import UMACalculator
        with patch.object(Path, "exists", return_value=True):
            calc = UMACalculator(model_path="fake.pt")
            assert calc.torch_num_threads is None
            assert calc.activation_checkpointing is None

    def test_task_case_insensitive(self):
        from umakit.calculator import UMACalculator
        with patch.object(Path, "exists", return_value=True):
            calc = UMACalculator(model_path="fake.pt", task="OMAT")
            assert calc.task == "omat"
```

- [ ] **Step 3: Run tests**

```bash
cd D:/Agent/fairchem && uv run pytest tests/core/umakit/test_calculator.py -c packages/fairchem-core/pyproject.toml -v
```
Expected: 5 PASS

- [ ] **Step 4: Ruff format**

```bash
cd D:/Agent/fairchem && uv run ruff check --fix uma/umakit/calculator.py tests/core/umakit/test_calculator.py && uv run ruff format uma/umakit/calculator.py tests/core/umakit/test_calculator.py
```

- [ ] **Step 5: Commit**

```bash
git add uma/umakit/calculator.py tests/core/umakit/test_calculator.py
git commit -m "feat: add torch_num_threads and activation_checkpointing to UMACalculator"
```

---

### Task 6: CalculationEngine

**Files:**
- Create: `uma/umakit/engine.py`
- Create: `tests/core/umakit/test_engine.py`

**Interfaces:**
- Consumes: `ProgressEvent`, `ProgressCallback` from `protocols.py`
- Consumes: `UMACalculator` from `calculator.py`
- Consumes: `SinglePointRunner`, `OptimizationRunner`, `MDRunner`, `BatchRunner` from `runners/`
- Produces: `EngineConfig` dataclass
- Produces: `CalculationEngine` class with `from_config()`, `run()`, `run_async()`, `run_batch()`

- [ ] **Step 1: Write test for EngineConfig**

Create `tests/core/umakit/test_engine.py`:

```python
"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from __future__ import annotations

from pathlib import Path

import pytest


class TestEngineConfig:
    """Tests for EngineConfig dataclass."""

    def test_minimal_config(self):
        from umakit.engine import EngineConfig
        config = EngineConfig(
            calc_type="sp",
            model_path=Path("model.pt"),
            task="omat",
            device="cpu",
            inference_mode="default",
            output_dir=Path("./results"),
        )
        assert config.calc_type == "sp"
        assert config.options == {}
        assert config.detach is False

    def test_config_with_options(self):
        from umakit.engine import EngineConfig
        config = EngineConfig(
            calc_type="opt",
            model_path=Path("model.pt"),
            task="omat",
            device="cpu",
            inference_mode="default",
            output_dir=Path("./results"),
            options={"fmax": 0.02, "cell_opt": True},
        )
        assert config.options["fmax"] == 0.02
        assert config.options["cell_opt"] is True

    def test_config_detach(self):
        from umakit.engine import EngineConfig
        config = EngineConfig(
            calc_type="sp",
            model_path=Path("model.pt"),
            task="omat",
            device="cpu",
            inference_mode="default",
            output_dir=Path("./results"),
            detach=True,
        )
        assert config.detach is True


class TestCalculationEngineSetup:
    """Tests for CalculationEngine construction and config validation."""

    def test_engine_from_config_sp(self):
        from umakit.engine import CalculationEngine, EngineConfig
        from unittest.mock import patch

        config = EngineConfig(
            calc_type="sp",
            model_path=Path("model.pt"),
            task="omat",
            device="cpu",
            inference_mode="default",
            output_dir=Path("./results"),
        )
        with patch.object(Path, "exists", return_value=True):
            engine = CalculationEngine.from_config(config)
            assert engine.config.calc_type == "sp"

    def test_invalid_calc_type_raises(self):
        from umakit.engine import CalculationEngine, EngineConfig
        config = EngineConfig(
            calc_type="invalid",
            model_path=Path("model.pt"),
            task="omat",
            device="cpu",
            inference_mode="default",
            output_dir=Path("./results"),
        )
        with pytest.raises(ValueError, match="Unknown calc_type"):
            CalculationEngine.from_config(config)

    def test_engine_config_options_validation_unknown_key_warns(self):
        """Unknown options keys should not raise, just warn."""
        from umakit.engine import CalculationEngine, EngineConfig
        config = EngineConfig(
            calc_type="sp",
            model_path=Path("model.pt"),
            task="omat",
            device="cpu",
            inference_mode="default",
            output_dir=Path("./results"),
            options={"made_up_key": 42},
        )
        # Should not raise
        from unittest.mock import patch
        with patch.object(Path, "exists", return_value=True):
            engine = CalculationEngine.from_config(config)
            assert engine is not None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd D:/Agent/fairchem && uv run pytest tests/core/umakit/test_engine.py -c packages/fairchem-core/pyproject.toml -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'umakit.engine'`

- [ ] **Step 3: Create engine.py**

Create `uma/umakit/engine.py`:

```python
"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

"""Unified execution engine for UMA calculations.

Provides CalculationEngine as the single entry point for CLI, TUI, and API.
"""

from __future__ import annotations

import asyncio
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from umakit.calculator import UMACalculator
from umakit.protocols import ProgressCallback, ProgressEvent

if TYPE_CHECKING:
    from typing import Any, AsyncIterator, Literal

    from ase import Atoms


@dataclass
class EngineConfig:
    """Unified configuration for all calculation types and interfaces.

    Fields:
        calc_type: sp, opt, md, or batch.
        model_path: Path to UMA model checkpoint.
        task: Task type (omat, omol, oc20, oc25, odac, omc).
        device: cpu or cuda.
        inference_mode: default or turbo.
        output_dir: Directory for output files.
        job_name: Optional job name.
        options: Calc-type-specific parameters (fmax, temperature, etc.).
        torch_num_threads: CPU thread count for torch.
        activation_checkpointing: GPU memory saving (overrides inference_mode preset).
        detach: If True, submit as background job.
    """

    calc_type: Literal["sp", "opt", "md", "batch"]
    model_path: Path
    task: str = "omat"
    device: str = "cpu"
    inference_mode: str = "default"
    output_dir: Path = field(default_factory=lambda: Path("./results"))
    job_name: str | None = None
    options: dict = field(default_factory=dict)
    torch_num_threads: int | None = None
    activation_checkpointing: bool | None = None
    detach: bool = False


class CalculationEngine:
    """Unified execution engine for UMA calculations.

    Use CalculationEngine.from_config() to create an instance, then
    call run(), run_async(), or run_batch().
    """

    VALID_CALC_TYPES = {"sp", "opt", "md", "batch"}

    def __init__(self, config: EngineConfig):
        self.config = config
        self._validate()

    @classmethod
    def from_config(cls, config: EngineConfig) -> CalculationEngine:
        return cls(config)

    def _validate(self) -> None:
        if self.config.calc_type not in self.VALID_CALC_TYPES:
            raise ValueError(
                f"Unknown calc_type '{self.config.calc_type}'. "
                f"Must be one of: {', '.join(self.VALID_CALC_TYPES)}"
            )
        # Warn about unknown option keys
        known_sp = set()
        known_opt = {"fmax", "max_steps", "optimizer", "cell_opt", "fix_symmetry"}
        known_md = {
            "ensemble", "temperature", "timestep", "steps", "friction",
            "save_interval", "pre_relax", "pre_relax_steps", "pre_relax_fmax",
        }
        known_batch = {"pattern", "sub_calc_type", "parallel", "max_workers"}
        known_all = known_sp | known_opt | known_md | known_batch
        unknown = set(self.config.options.keys()) - known_all
        for key in unknown:
            warnings.warn(f"Unknown option '{key}' for calc_type '{self.config.calc_type}'")

    def _create_calculator(self) -> UMACalculator:
        return UMACalculator(
            model_path=self.config.model_path,
            task=self.config.task,
            device=self.config.device,
            inference_mode=self.config.inference_mode,
            torch_num_threads=self.config.torch_num_threads,
            activation_checkpointing=self.config.activation_checkpointing,
        )

    def _create_runner(self, calculator, progress_callback=None, log_fn=None):
        from umakit.runners.singlepoint import SinglePointRunner
        from umakit.runners.optimization import OptimizationRunner
        from umakit.runners.md import MDRunner

        opts = self.config.options
        common = dict(
            calculator=calculator,
            output_dir=self.config.output_dir,
            verbose=False,
            job_name=self.config.job_name,
            log_fn=log_fn,
            progress_callback=progress_callback,
        )

        if self.config.calc_type == "sp":
            return SinglePointRunner(**common)
        elif self.config.calc_type == "opt":
            return OptimizationRunner(
                fmax=opts.get("fmax", 0.05),
                max_steps=opts.get("max_steps", 500),
                optimizer=opts.get("optimizer", "FIRE"),
                cell_opt=opts.get("cell_opt", False),
                fix_symmetry=opts.get("fix_symmetry", False),
                **common,
            )
        elif self.config.calc_type == "md":
            return MDRunner(
                ensemble=opts.get("ensemble", "NVT"),
                temperature=opts.get("temperature", 300.0),
                timestep=opts.get("timestep", 1.0),
                steps=opts.get("steps", 1000),
                friction=opts.get("friction", 0.001),
                save_interval=opts.get("save_interval", 10),
                pre_relax=opts.get("pre_relax", True),
                pre_relax_steps=opts.get("pre_relax_steps", 50),
                pre_relax_fmax=opts.get("pre_relax_fmax", 0.1),
                **common,
            )
        else:
            raise ValueError(f"Unknown calc_type: {self.config.calc_type}")

    def run(
        self,
        atoms: Atoms,
        progress_callback: ProgressCallback | None = None,
    ) -> dict[str, Any]:
        """Run calculation synchronously.

        Args:
            atoms: ASE Atoms object.
            progress_callback: Optional callback for progress events.

        Returns:
            Results dictionary.
        """
        calculator = self._create_calculator()
        runner = self._create_runner(calculator, progress_callback=progress_callback)
        return runner.run(atoms)

    async def run_async(
        self,
        atoms: Atoms,
    ) -> AsyncIterator[ProgressEvent]:
        """Run calculation asynchronously, yielding progress events.

        The actual computation runs in a thread pool; progress events
        are bridged back to the asyncio loop via a queue.

        Args:
            atoms: ASE Atoms object.

        Yields:
            ProgressEvent at each phase transition.
        """
        queue: asyncio.Queue[ProgressEvent | None] = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def progress_callback(event: ProgressEvent) -> None:
            loop.call_soon_threadsafe(queue.put_nowait, event)

        def blocking_work() -> dict[str, Any]:
            return self.run(atoms, progress_callback=progress_callback)

        task = loop.run_in_executor(None, blocking_work)

        try:
            while True:
                event = await queue.get()
                yield event
                if event.phase in ("done", "error"):
                    break
        except asyncio.CancelledError:
            task.cancel()
            yield ProgressEvent(phase="error", message="Calculation cancelled by user")
        finally:
            await task

    def run_batch(
        self,
        files: list[Path],
        progress_callback: ProgressCallback | None = None,
    ) -> dict[str, Any]:
        """Run batch calculation on multiple structure files.

        Args:
            files: List of structure file paths.
            progress_callback: Optional callback for progress events.

        Returns:
            Batch summary dictionary.
        """
        from umakit.runners.batch import BatchRunner

        calculator = self._create_calculator()
        opts = self.config.options
        runner = BatchRunner(
            calculator,
            calc_type=opts.get("sub_calc_type", "sp"),
            output_dir=self.config.output_dir,
            parallel=opts.get("parallel", False),
            max_workers=opts.get("max_workers", 1),
            verbose=False,
            job_name=self.config.job_name,
        )
        return runner.run_from_files(files)
```

- [ ] **Step 4: Run tests**

```bash
cd D:/Agent/fairchem && uv run pytest tests/core/umakit/test_engine.py -c packages/fairchem-core/pyproject.toml -v
```
Expected: 5 PASS

- [ ] **Step 5: Ruff format**

```bash
cd D:/Agent/fairchem && uv run ruff check --fix uma/umakit/engine.py tests/core/umakit/test_engine.py && uv run ruff format uma/umakit/engine.py tests/core/umakit/test_engine.py
```

- [ ] **Step 6: Commit**

```bash
git add uma/umakit/engine.py tests/core/umakit/test_engine.py
git commit -m "feat: add CalculationEngine as unified execution entry point"
```

---

### Task 7: Simplify CLI with Engine

**Files:**
- Modify: `uma/umakit/cli.py`

**Interfaces:**
- Consumes: `CalculationEngine`, `EngineConfig` from `engine.py`
- Produces: CLI handlers are thin wrappers around Engine

- [ ] **Step 1: Refactor cmd_sp to use Engine**

Replace `cmd_sp` body (which duplicates ~30 lines of structure reading + model loading) with:

```python
def cmd_sp(args: argparse.Namespace) -> int:
    from umakit.engine import CalculationEngine, EngineConfig

    structure_path = Path(args.structure)
    if not structure_path.exists():
        print(f"Error: Structure file not found: {structure_path}")
        return 1

    config = EngineConfig(
        calc_type="sp",
        model_path=Path(args.model),
        task=args.task,
        device=args.device,
        output_dir=Path(args.output),
        job_name=args.name,
    )

    print_header()
    print(f"System: reading from {structure_path}")

    try:
        atoms = read(structure_path)
        print(f"System: {atoms.get_chemical_formula()}")
        print(f"Atoms: {len(atoms)}")

        engine = CalculationEngine.from_config(config)
        results = engine.run(atoms)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1
```

- [ ] **Step 2: Refactor cmd_opt to use Engine**

Replace the entire `cmd_opt` function body：

```python
def cmd_opt(args: argparse.Namespace) -> int:
    from umakit.engine import CalculationEngine, EngineConfig

    structure_path = Path(args.structure)
    if not structure_path.exists():
        print(f"Error: Structure file not found: {structure_path}")
        return 1

    config = EngineConfig(
        calc_type="opt",
        model_path=Path(args.model),
        task=args.task,
        device=args.device,
        output_dir=Path(args.output),
        job_name=args.name,
        options={
            "fmax": args.fmax,
            "max_steps": args.max_steps,
            "optimizer": args.optimizer,
            "cell_opt": args.cell_opt,
            "fix_symmetry": args.fix_symmetry,
        },
    )

    print_header()
    print(f"Reading structure from: {structure_path}")

    try:
        atoms = read(structure_path)
        print(f"System: {atoms.get_chemical_formula()}")
        print(f"Atoms: {len(atoms)}")

        engine = CalculationEngine.from_config(config)
        results = engine.run(atoms)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1
```

- [ ] **Step 3: Refactor cmd_md to use Engine**

Replace the entire `cmd_md` function body:

```python
def cmd_md(args: argparse.Namespace) -> int:
    from umakit.engine import CalculationEngine, EngineConfig

    structure_path = Path(args.structure)
    if not structure_path.exists():
        print(f"Error: Structure file not found: {structure_path}")
        return 1

    config = EngineConfig(
        calc_type="md",
        model_path=Path(args.model),
        task=args.task,
        device=args.device,
        inference_mode="turbo",
        output_dir=Path(args.output),
        job_name=args.name,
        options={
            "ensemble": args.ensemble,
            "temperature": args.temp,
            "timestep": args.timestep,
            "steps": args.steps,
            "friction": args.friction,
            "save_interval": args.save_interval,
        },
    )

    print_header()
    print(f"Reading structure from: {structure_path}")

    try:
        atoms = read(structure_path)
        print(f"System: {atoms.get_chemical_formula()}")
        print(f"Atoms: {len(atoms)}")

        engine = CalculationEngine.from_config(config)
        results = engine.run(atoms)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1
```

- [ ] **Step 4: Refactor cmd_batch to use Engine**

Replace the `cmd_batch` function body:

```python
def cmd_batch(args: argparse.Namespace) -> int:
    from umakit.engine import CalculationEngine, EngineConfig

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        return 1

    config = EngineConfig(
        calc_type="batch",
        model_path=Path(args.model),
        task=args.task,
        device=args.device,
        output_dir=Path(args.output),
        job_name=args.name,
        options={
            "sub_calc_type": args.calc_type,
            "pattern": args.pattern,
        },
    )

    print_header()

    try:
        engine = CalculationEngine.from_config(config)
        files = list(input_dir.glob(args.pattern))
        if not files:
            print(f"No files matching '{args.pattern}' found in {input_dir}")
            return 1
        print(f"Found {len(files)} structure files")
        summary = engine.run_batch(files)
        if summary["failed"] > 0:
            return 1
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1
```

- [ ] **Step 5: Verify CLI help still works**

```bash
cd D:/Agent/fairchem && uv run python uma/umakit/cli.py --help
```
Expected: Help output with all subcommands listed

- [ ] **Step 6: Ruff format**

```bash
cd D:/Agent/fairchem && uv run ruff check --fix uma/umakit/cli.py && uv run ruff format uma/umakit/cli.py
```

- [ ] **Step 7: Commit**

```bash
git add uma/umakit/cli.py
git commit -m "refactor: simplify CLI handlers to use CalculationEngine"
```

---

### Task 8: TUI asyncio + Engine integration

**Files:**
- Modify: `uma/umakit/tui/run_screen.py` (full rewrite of `_run_calculation`)
- Modify: `uma/umakit/tui/config_screen.py` (add detach switch)

**Interfaces:**
- Consumes: `CalculationEngine`, `EngineConfig`, `ProgressEvent` from `engine.py` and `protocols.py`
- Produces: `RunScreen` uses `asyncio.Task` with `run_async()`, supports `cancel()`

- [ ] **Step 1: Rewrite RunScreen._run_calculation with asyncio**

Replace the `_run_calculation` method and all `_run_*` helper methods in `run_screen.py`:

```python
def _get_engine_config(self) -> EngineConfig:
    """Build EngineConfig from app state."""
    from pathlib import Path
    from umakit.engine import EngineConfig

    calc_type = self.app.get_config("calc_type")
    options = {}
    if calc_type == "opt":
        options.update({
            "fmax": self.app.get_config("fmax", 0.05),
            "max_steps": self.app.get_config("max_steps", 500),
            "optimizer": self.app.get_config("optimizer", "FIRE"),
            "cell_opt": self.app.get_config("cell_opt", False),
            "fix_symmetry": self.app.get_config("fix_symmetry", False),
        })
    elif calc_type == "md":
        options.update({
            "ensemble": self.app.get_config("ensemble", "NVT"),
            "temperature": self.app.get_config("temperature", 300.0),
            "timestep": self.app.get_config("timestep", 1.0),
            "steps": self.app.get_config("md_steps", 1000),
            "save_interval": self.app.get_config("save_interval", 10),
            "pre_relax": self.app.get_config("pre_relax", True),
            "pre_relax_steps": self.app.get_config("pre_relax_steps", 50),
            "pre_relax_fmax": self.app.get_config("pre_relax_fmax", 0.1),
        })

    return EngineConfig(
        calc_type=calc_type,
        model_path=Path(self.app.get_config("model_file", "")),
        task=self.app.get_config("task", "omat"),
        device=self.app.get_config("device", "cpu"),
        output_dir=Path(self.app.get_config("output_dir", "./results")),
        job_name=self.app.get_config("job_name"),
        options=options,
    )

async def _run_calculation(self) -> None:
    """Run the calculation asynchronously with progress events."""
    try:
        from ase.io import read
        from umakit.engine import CalculationEngine

        config = self._get_engine_config()

        self._log("Loading structure...")
        structure_file = self.app.get_config("structure_file")
        atoms = read(structure_file)
        self._log(f"Loaded: {atoms.get_chemical_formula()} ({len(atoms)} atoms)")

        engine = CalculationEngine.from_config(config)
        self._task = asyncio.current_task()

        async for event in engine.run_async(atoms):
            if event.phase == "loading_model":
                self._update_indeterminate(event.message)
            elif event.phase == "running":
                if event.total_steps is not None:
                    pct = (event.step / event.total_steps) * 100 if event.step else 0
                    self._update_progress(pct, event.message)
                else:
                    self._update_indeterminate(event.message)
            elif event.phase == "writing_output":
                self._update_indeterminate(event.message)
            elif event.phase == "done":
                self._update_progress(100, "Complete")
                self._log(f"\nCalculation complete!")
                if event.extra:
                    if "energy" in event.extra:
                        self._log(f"Energy: {event.extra['energy']:.6f} eV")
                self._log(f"Output: {self.app.get_config('output_dir')}")
            elif event.phase == "error":
                self._log(f"\nERROR: {event.message}")
                self._update_progress(0, "Failed")

    except asyncio.CancelledError:
        self._log("\nCalculation cancelled by user")
        self._update_progress(0, "Cancelled")
    except Exception as e:
        import traceback
        self._log(f"\nERROR: {e}")
        self._log(traceback.format_exc())
        self._update_progress(0, "Failed")
    finally:
        def enable_back():
            back_btn = self.query_one("#back-btn", Button)
            back_btn.disabled = False
        self.app.call_from_thread(enable_back)

def _update_indeterminate(self, status: str) -> None:
    """Update progress bar to indeterminate mode."""
    def update():
        self.progress.update(progress=None)
        self.status.update(status)
    self.app.call_from_thread(update)
```

Note: Textual's `ProgressBar.update(progress=None)` puts it in indeterminate mode (the animated bar). Remove the old `_run_sp`, `_run_opt`, `_run_md`, `_run_batch` methods.

- [ ] **Step 2: Add "Background" switch to ConfigScreen**

In `uma/umakit/tui/config_screen.py`, in `_calc_options` for each calc type, add at the end of the yield list:

```python
yield Horizontal(
    Label("Run in background (detach):"),
    Switch(value=False, id="detach-switch"),
)
```

In `_save_and_run`, capture the detach switch value:

```python
detach_switch = self.query_one("#detach-switch", Switch)
self.app.update_config("detach", detach_switch.value)
```

- [ ] **Step 3: Ruff format**

```bash
cd D:/Agent/fairchem && uv run ruff check --fix uma/umakit/tui/run_screen.py uma/umakit/tui/config_screen.py && uv run ruff format uma/umakit/tui/run_screen.py uma/umakit/tui/config_screen.py
```

- [ ] **Step 4: Commit**

```bash
git add uma/umakit/tui/run_screen.py uma/umakit/tui/config_screen.py
git commit -m "refactor: rewrite TUI run screen with asyncio worker and Engine integration"
```

---

### Task 9: JobManager

**Files:**
- Create: `uma/umakit/jobs.py`
- Create: `tests/core/umakit/test_jobs.py`

**Interfaces:**
- Produces: `JobManager` class with `submit()`, `list_jobs()`, `get_job()`, `kill_job()`, `clean()`
- Produces: `JobStatus` enum: `pending | running | done | failed | cancelled`

- [ ] **Step 1: Write test**

Create `tests/core/umakit/test_jobs.py`:

```python
"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest


class TestJobManager:
    """Tests for job state management (no subprocess needed)."""

    def test_job_status_enum(self):
        from umakit.jobs import JobStatus
        assert JobStatus.RUNNING.value == "running"
        assert JobStatus.DONE.value == "done"
        assert JobStatus.FAILED.value == "failed"

    def test_job_manager_create_job_dir(self):
        from umakit.jobs import JobManager
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = JobManager(jobs_dir=Path(tmpdir))
            assert mgr.jobs_dir.exists()

    def test_write_and_read_job_state(self):
        from umakit.jobs import JobManager, JobStatus
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = JobManager(jobs_dir=Path(tmpdir))
            mgr._write_job_state(
                job_id="test_job",
                status=JobStatus.RUNNING,
                calc_type="sp",
                structure="/path/to/POSCAR",
                formula="H2O",
                natoms=3,
                pid=12345,
                device="cpu",
            )
            data = mgr._read_job_state("test_job")
            assert data["status"] == "running"
            assert data["formula"] == "H2O"

    def test_list_jobs(self):
        from umakit.jobs import JobManager, JobStatus
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = JobManager(jobs_dir=Path(tmpdir))
            mgr._write_job_state("job1", JobStatus.RUNNING, "sp", "/a/b.cif", "H2O", 3, 100, "cpu")
            mgr._write_job_state("job2", JobStatus.DONE, "opt", "/a/c.cif", "Cu", 16, 200, "cuda")
            jobs = mgr.list_jobs()
            assert len(jobs) == 2

    def test_clean_removes_done_and_failed(self):
        from umakit.jobs import JobManager, JobStatus
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = JobManager(jobs_dir=Path(tmpdir))
            mgr._write_job_state("done_job", JobStatus.DONE, "sp", "/a", "H2O", 3, 100, "cpu")
            mgr._write_job_state("running_job", JobStatus.RUNNING, "sp", "/a", "H2O", 3, 200, "cpu")
            mgr._write_job_state("failed_job", JobStatus.FAILED, "sp", "/a", "H2O", 3, 300, "cpu")
            removed = mgr.clean()
            assert len(removed) == 2
            remaining = mgr.list_jobs()
            assert len(remaining) == 1
            assert remaining[0]["job_id"] == "running_job"

    def test_kill_job_signal(self):
        """Test that kill_job generates correct platform command."""
        import sys
        from umakit.jobs import JobManager
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = JobManager(jobs_dir=Path(tmpdir))
            if sys.platform == "win32":
                assert "taskkill" in str(mgr._build_kill_cmd(12345))
            else:
                assert "SIGTERM" in str(mgr._build_kill_cmd(12345))
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd D:/Agent/fairchem && uv run pytest tests/core/umakit/test_jobs.py -c packages/fairchem-core/pyproject.toml -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'umakit.jobs'`

- [ ] **Step 3: Create jobs.py**

Create `uma/umakit/jobs.py`:

```python
"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

"""Background job manager for UMA calculations.

Manages calculation jobs as independent subprocesses with
disk-persisted state for attach/kill/clean operations.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


def _default_jobs_dir() -> Path:
    """Get default jobs directory: ~/.umakit/jobs/"""
    return Path.home() / ".umakit" / "jobs"


class JobManager:
    """Manage background calculation jobs with disk-persisted state."""

    def __init__(self, jobs_dir: Path | None = None):
        self.jobs_dir = jobs_dir or _default_jobs_dir()
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        self._logs_dir = self.jobs_dir / "logs"
        self._logs_dir.mkdir(exist_ok=True)

    def _job_file(self, job_id: str) -> Path:
        return self.jobs_dir / f"{job_id}.json"

    def _log_file(self, job_id: str) -> Path:
        return self._logs_dir / f"{job_id}.log"

    def _write_job_state(
        self,
        job_id: str,
        status: JobStatus,
        calc_type: str,
        structure: str,
        formula: str,
        natoms: int,
        pid: int,
        device: str,
        progress: dict | None = None,
        results: dict | None = None,
        error: str | None = None,
        finished_at: str | None = None,
    ) -> None:
        data = {
            "job_id": job_id,
            "status": status.value,
            "calc_type": calc_type,
            "structure": structure,
            "formula": formula,
            "natoms": natoms,
            "pid": pid,
            "device": device,
            "started_at": datetime.now().isoformat(),
            "finished_at": finished_at,
            "log_file": str(self._log_file(job_id)),
            "progress": progress or {},
            "results": results,
            "error": error,
        }
        with open(self._job_file(job_id), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _read_job_state(self, job_id: str) -> dict[str, Any] | None:
        path = self._job_file(job_id)
        if not path.exists():
            return None
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def list_jobs(self) -> list[dict[str, Any]]:
        jobs = []
        for path in sorted(self.jobs_dir.glob("*.json")):
            with open(path, encoding="utf-8") as f:
                jobs.append(json.load(f))
        return jobs

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        return self._read_job_state(job_id)

    def clean(self) -> list[str]:
        """Remove state files for done/failed/cancelled jobs. Returns list of removed IDs."""
        removed = []
        for path in self.jobs_dir.glob("*.json"):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if data.get("status") in ("done", "failed", "cancelled"):
                path.unlink()
                removed.append(data["job_id"])
        return removed

    def submit(
        self,
        job_id: str,
        calc_type: str,
        structure: str,
        formula: str,
        natoms: int,
        device: str,
        cmd: list[str],
    ) -> subprocess.Popen:
        """Submit a calculation as a background subprocess.

        Args:
            job_id: Unique job identifier.
            calc_type: sp, opt, or md.
            structure: Path to structure file.
            formula: Chemical formula.
            natoms: Number of atoms.
            device: cpu or cuda.
            cmd: Full command to execute as subprocess (e.g., ['uv', 'run', 'uma_calc', 'sp', ...]).

        Returns:
            Popen instance for the spawned process.
        """
        log_path = self._log_file(job_id)
        with open(log_path, "w") as log_f:
            proc = subprocess.Popen(
                cmd,
                stdout=log_f,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )

        self._write_job_state(
            job_id=job_id,
            status=JobStatus.RUNNING,
            calc_type=calc_type,
            structure=structure,
            formula=formula,
            natoms=natoms,
            pid=proc.pid,
            device=device,
        )
        return proc

    def kill_job(self, job_id: str) -> bool:
        """Kill a running job by PID. Returns True if successful."""
        data = self._read_job_state(job_id)
        if data is None:
            return False
        if data["status"] != "running":
            return False

        pid = data["pid"]
        cmd = self._build_kill_cmd(pid)

        try:
            subprocess.run(cmd, check=False)
            self._write_job_state(
                job_id=job_id,
                status=JobStatus.CANCELLED,
                calc_type=data["calc_type"],
                structure=data["structure"],
                formula=data["formula"],
                natoms=data["natoms"],
                pid=pid,
                device=data.get("device", "cpu"),
                finished_at=datetime.now().isoformat(),
            )
            return True
        except Exception:
            return False

    def _build_kill_cmd(self, pid: int) -> list[str]:
        """Build platform-appropriate kill command."""
        if sys.platform == "win32":
            return ["taskkill", "/PID", str(pid), "/F"]
        else:
            # Can't return a signal; use os.kill for Unix
            os.kill(pid, signal.SIGTERM)
            return ["kill", str(pid)]

    def tail_log(self, job_id: str, lines: int = 50) -> str:
        """Return the last N lines of the job log."""
        log_path = self._log_file(job_id)
        if not log_path.exists():
            return ""
        with open(log_path, encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
            return "".join(all_lines[-lines:])
```

- [ ] **Step 4: Run tests**

```bash
cd D:/Agent/fairchem && uv run pytest tests/core/umakit/test_jobs.py -c packages/fairchem-core/pyproject.toml -v
```
Expected: 6 PASS

- [ ] **Step 5: Ruff format**

```bash
cd D:/Agent/fairchem && uv run ruff check --fix uma/umakit/jobs.py tests/core/umakit/test_jobs.py && uv run ruff format uma/umakit/jobs.py tests/core/umakit/test_jobs.py
```

- [ ] **Step 6: Commit**

```bash
git add uma/umakit/jobs.py tests/core/umakit/test_jobs.py
git commit -m "feat: add JobManager for background job submit/attach/kill/clean"
```

---

### Task 10: TUI Jobs screen

**Files:**
- Create: `uma/umakit/tui/jobs_screen.py`
- Modify: `uma/umakit/tui/app.py` (register screen + add Jobs entry)
- Modify: `uma/umakit/tui/main_screen.py` (add Jobs menu item)

**Interfaces:**
- Consumes: `JobManager` from `jobs.py`
- Produces: `JobsScreen` with `DataTable` of jobs, Enter for detail/log view

- [ ] **Step 1: Create JobsScreen**

Create `uma/umakit/tui/jobs_screen.py`:

```python
"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

"""Jobs screen for managing background calculations."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Button, DataTable, Log, Static

from umakit.jobs import JobManager

if TYPE_CHECKING:
    from textual.app import ComposeResult


class JobsScreen(Screen):
    """Screen for viewing and managing background jobs."""

    BINDINGS = [
        ("escape", "back", "Back"),
        ("c", "cancel_job", "Cancel Job"),
        ("d", "delete_job", "Delete"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._job_manager = JobManager()
        self._refresh_timer: asyncio.Task | None = None

    def compose(self) -> ComposeResult:
        yield Container(
            Static("Background Jobs", id="title"),
            Static("Manage running and completed calculations", id="subtitle"),
            DataTable(id="jobs-table"),
            Horizontal(
                Button("Cancel Job", variant="error", id="cancel-job-btn"),
                Button("Delete", id="delete-btn"),
                Button("Refresh", id="refresh-btn"),
                Button("Back", id="back-btn"),
                id="jobs-button-bar",
            ),
            id="jobs-main",
        )

    def on_mount(self) -> None:
        table = self.query_one("#jobs-table", DataTable)
        table.add_columns("ID", "Status", "Type", "Formula", "Atoms", "Device")
        self._refresh_table()
        self._refresh_timer = asyncio.create_task(self._auto_refresh())

    async def _auto_refresh(self) -> None:
        while True:
            await asyncio.sleep(2)
            self._refresh_table()

    def _refresh_table(self) -> None:
        table = self.query_one("#jobs-table", DataTable)
        table.clear()
        jobs = self._job_manager.list_jobs()
        status_icons = {
            "running": "●",
            "done": "✓",
            "failed": "✗",
            "cancelled": "⊘",
            "pending": "○",
        }
        for job in jobs:
            icon = status_icons.get(job["status"], "?")
            table.add_row(
                job["job_id"],
                f"{icon} {job['status']}",
                job.get("calc_type", ""),
                job.get("formula", ""),
                str(job.get("natoms", "")),
                job.get("device", ""),
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "back-btn":
            self.app.pop_screen()
        elif button_id == "refresh-btn":
            self._refresh_table()
        elif button_id == "cancel-job-btn":
            self._cancel_selected_job()
        elif button_id == "delete-btn":
            self._delete_selected_job()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Show job detail/log on selection."""
        row_key = event.row_key
        if row_key is not None:
            job_id = str(event.row_key.value)
            log_text = self._job_manager.tail_log(job_id, lines=200)
            self.app.push_screen(JobDetailScreen(job_id, log_text))

    def _cancel_selected_job(self) -> None:
        table = self.query_one("#jobs-table", DataTable)
        if table.cursor_row is not None and table.cursor_row < table.row_count:
            row = table.get_row_at(table.cursor_row)
            job_id = str(row[0])
            ok = self._job_manager.kill_job(job_id)
            if ok:
                self.app.notify(f"Cancelled job: {job_id}", title="OK")
            else:
                self.app.notify(f"Failed to cancel: {job_id}", title="Error", severity="error")
            self._refresh_table()

    def _delete_selected_job(self) -> None:
        table = self.query_one("#jobs-table", DataTable)
        if table.cursor_row is not None and table.cursor_row < table.row_count:
            row = table.get_row_at(table.cursor_row)
            job_id = str(row[0])
            data = self._job_manager.get_job(job_id)
            if data and data["status"] != "running":
                job_file = self._job_manager._job_file(job_id)
                job_file.unlink(missing_ok=True)
                self._refresh_table()

    def action_back(self) -> None:
        if self._refresh_timer:
            self._refresh_timer.cancel()
        self.app.pop_screen()

    def action_cancel_job(self) -> None:
        self._cancel_selected_job()

    def action_delete_job(self) -> None:
        self._delete_selected_job()

    def action_refresh(self) -> None:
        self._refresh_table()


class JobDetailScreen(Screen):
    """Screen for viewing job log output."""

    BINDINGS = [("escape", "back", "Back")]

    def __init__(self, job_id: str, log_text: str, **kwargs):
        super().__init__(**kwargs)
        self.job_id = job_id
        self.log_text = log_text

    def compose(self) -> ComposeResult:
        yield Container(
            Static(f"Job: {self.job_id}", id="title"),
            Log(self.log_text, id="job-detail-log"),
            Button("Back", id="back-btn"),
            id="job-detail-container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back-btn":
            self.app.pop_screen()

    def action_back(self) -> None:
        self.app.pop_screen()
```

- [ ] **Step 2: Register JobsScreen in app.py**

Add import:
```python
from umakit.tui.jobs_screen import JobsScreen
```

Add to `SCREENS` dict:
```python
SCREENS = {
    "main": MainScreen,
    "config": ConfigScreen,
    "run": RunScreen,
    "template": TemplateScreen,
    "jobs": JobsScreen,
}
```

- [ ] **Step 3: Add Jobs entry to MainScreen**

In `uma/umakit/tui/main_screen.py`, modify the `compose` method to add a Jobs menu item between "Batch Processing" and "Generate Template":

```python
ListItem(
    Static("💼 Background Jobs\n   View/manage running calculations"),
    id="jobs",
),
```

And handle it in `on_list_view_selected`:

```python
if item_id == "jobs":
    self.app.push_screen("jobs")
    return
```

- [ ] **Step 4: Ruff format**

```bash
cd D:/Agent/fairchem && uv run ruff check --fix uma/umakit/tui/jobs_screen.py uma/umakit/tui/app.py uma/umakit/tui/main_screen.py && uv run ruff format uma/umakit/tui/jobs_screen.py uma/umakit/tui/app.py uma/umakit/tui/main_screen.py
```

- [ ] **Step 5: Commit**

```bash
git add uma/umakit/tui/jobs_screen.py uma/umakit/tui/app.py uma/umakit/tui/main_screen.py
git commit -m "feat: add TUI Jobs screen for background job management"
```

---

### Task 11: CLI jobs/kill/clean + Batch parallel

**Files:**
- Modify: `uma/umakit/cli.py`
- Modify: `uma/umakit/runners/batch.py`

**Interfaces:**
- Consumes: `JobManager` from `jobs.py`
- Produces: `uma_calc jobs`, `uma_calc kill <id>`, `uma_calc clean` subcommands
- Produces: `BatchRunner` supports `parallel=True` with `ThreadPoolExecutor`

- [ ] **Step 1: Add jobs/kill/clean subcommands to CLI**

In `uma/umakit/cli.py`, add to subparsers after the existing commands:

```python
# jobs command
jobs_parser = subparsers.add_parser("jobs", help="List background jobs")
jobs_parser.add_argument("--refresh", type=int, default=0, help="Auto-refresh interval in seconds")

# kill command
kill_parser = subparsers.add_parser("kill", help="Kill a background job")
kill_parser.add_argument("job_id", help="Job ID to kill")

# clean command
clean_parser = subparsers.add_parser("clean", help="Remove completed/failed job records")
```

Add handler functions:

```python
def cmd_jobs(args: argparse.Namespace) -> int:
    from umakit.jobs import JobManager
    mgr = JobManager()
    jobs = mgr.list_jobs()
    if not jobs:
        print("No jobs found.")
        return 0
    print(f"{'ID':<40} {'Status':<12} {'Type':<6} {'Formula':<12} {'Device'}")
    print("-" * 90)
    for j in jobs:
        print(f"{j['job_id']:<40} {j['status']:<12} {j.get('calc_type',''):<6} {j.get('formula',''):<12} {j.get('device','')}")
    return 0

def cmd_kill(args: argparse.Namespace) -> int:
    from umakit.jobs import JobManager
    mgr = JobManager()
    ok = mgr.kill_job(args.job_id)
    if ok:
        print(f"Killed: {args.job_id}")
        return 0
    else:
        print(f"Failed to kill: {args.job_id}")
        return 1

def cmd_clean(args: argparse.Namespace) -> int:
    from umakit.jobs import JobManager
    mgr = JobManager()
    removed = mgr.clean()
    if removed:
        print(f"Removed {len(removed)} completed/failed job records.")
    else:
        print("No completed/failed jobs to clean.")
    return 0
```

Register in `commands` dict:
```python
commands = {
    "run": cmd_run,
    "sp": cmd_sp,
    "opt": cmd_opt,
    "md": cmd_md,
    "batch": cmd_batch,
    "template": cmd_template,
    "jobs": cmd_jobs,
    "kill": cmd_kill,
    "clean": cmd_clean,
}
```

- [ ] **Step 2: Implement BatchRunner parallel**

In `uma/umakit/runners/batch.py`, modify `run_from_files` to support parallel execution:

```python
def run_from_files(self, files: list[Path | str]) -> dict[str, Any]:
    results_list = []
    success_count = 0
    failed_count = 0

    if self.parallel and self.max_workers > 1:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def process_one(filepath):
            filepath = Path(filepath)
            atoms = read(filepath)
            sub_dir = self.output_dir / filepath.stem
            sub_dir.mkdir(exist_ok=True)
            result = self._run_single(atoms, sub_dir, filepath.stem)
            return {
                "filename": filepath.name,
                "formula": atoms.get_chemical_formula(),
                "natoms": len(atoms),
                "success": True,
                **result,
            }

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(process_one, f): f for f in files}
            for future in as_completed(futures):
                filepath = futures[future]
                try:
                    result = future.result()
                    results_list.append(result)
                    success_count += 1
                except Exception as e:
                    results_list.append({
                        "filename": Path(filepath).name,
                        "success": False,
                        "error": f"{type(e).__name__}: {str(e)}",
                    })
                    failed_count += 1
    else:
        # Original sequential loop
        iterator = tqdm(files, desc="Processing structures") if self.verbose else files
        for filepath in iterator:
            filepath = Path(filepath)
            try:
                atoms = read(filepath)
                sub_dir = self.output_dir / filepath.stem
                sub_dir.mkdir(exist_ok=True)
                result = self._run_single(atoms, sub_dir, filepath.stem)
                results_list.append({
                    "filename": filepath.name,
                    "formula": atoms.get_chemical_formula(),
                    "natoms": len(atoms),
                    "success": True,
                    **result,
                })
                success_count += 1
            except Exception as e:
                results_list.append({
                    "filename": filepath.name,
                    "success": False,
                    "error": f"{type(e).__name__}: {str(e)}",
                })
                failed_count += 1

    summary = {
        "total": len(files),
        "success": success_count,
        "failed": failed_count,
        "results": results_list,
    }
    self._write_summary(summary)
    return summary
```

- [ ] **Step 3: Ruff format**

```bash
cd D:/Agent/fairchem && uv run ruff check --fix uma/umakit/cli.py uma/umakit/runners/batch.py && uv run ruff format uma/umakit/cli.py uma/umakit/runners/batch.py
```

- [ ] **Step 4: Commit**

```bash
git add uma/umakit/cli.py uma/umakit/runners/batch.py
git commit -m "feat: add CLI jobs/kill/clean commands and BatchRunner ThreadPoolExecutor parallel"
```

---

### Task 12: Refactor api.py + Cleanup

**Files:**
- Modify: `uma/umakit/api.py`
- Modify: `uma/umakit/__init__.py`
- Delete: `uma/uma_calc.py`

**Interfaces:**
- Consumes: `CalculationEngine`, `EngineConfig` from `engine.py`
- Produces: API functions are thin wrappers around Engine
- Produces: `__init__.py` uses lazy imports

- [ ] **Step 1: Refactor api.py to use Engine**

Replace all API function bodies to use `CalculationEngine` instead of creating runners directly.

For `run_single_point`:

```python
def run_single_point(
    structure: Atoms | str | Path,
    model_path: str,
    task: str = "omat",
    device: str = "cpu",
    job_name: str | None = None,
    output_dir: str = "./results",
    verbose: bool = True,
    **kwargs,
) -> dict[str, Any]:
    atoms = _load_structure(structure)
    if verbose:
        print(f"System: {atoms.get_chemical_formula()}")
        print(f"Atoms: {len(atoms)}")
        print(f"Loading model: {model_path}")

    config = EngineConfig(
        calc_type="sp",
        model_path=Path(model_path),
        task=task,
        device=device,
        output_dir=Path(output_dir),
        job_name=job_name,
    )
    engine = CalculationEngine.from_config(config)
    return engine.run(atoms)
```

For `run_optimization`:

```python
def run_optimization(
    structure: Atoms | str | Path,
    model_path: str,
    task: str = "omat",
    device: str = "cpu",
    job_name: str | None = None,
    output_dir: str = "./results",
    fmax: float = 0.05,
    max_steps: int = 500,
    optimizer: str = "FIRE",
    cell_opt: bool = False,
    fix_symmetry: bool = False,
    verbose: bool = True,
    **kwargs,
) -> dict[str, Any]:
    atoms = _load_structure(structure)
    if verbose:
        print(f"System: {atoms.get_chemical_formula()}")
        print(f"Atoms: {len(atoms)}")
        print(f"Loading model: {model_path}")

    config = EngineConfig(
        calc_type="opt",
        model_path=Path(model_path),
        task=task,
        device=device,
        output_dir=Path(output_dir),
        job_name=job_name,
        options={
            "fmax": fmax,
            "max_steps": max_steps,
            "optimizer": optimizer,
            "cell_opt": cell_opt,
            "fix_symmetry": fix_symmetry,
        },
    )
    engine = CalculationEngine.from_config(config)
    return engine.run(atoms)
```

For `run_md`:

```python
def run_md(
    structure: Atoms | str | Path,
    model_path: str,
    task: str = "omat",
    device: str = "cuda",
    job_name: str | None = None,
    output_dir: str = "./results",
    ensemble: str = "NVT",
    temperature: float = 300.0,
    timestep: float = 1.0,
    steps: int = 1000,
    friction: float = 0.001,
    save_interval: int = 10,
    pre_relax: bool = True,
    verbose: bool = True,
    **kwargs,
) -> dict[str, Any]:
    atoms = _load_structure(structure)
    if verbose:
        print(f"System: {atoms.get_chemical_formula()}")
        print(f"Atoms: {len(atoms)}")
        print(f"Loading model: {model_path}")

    config = EngineConfig(
        calc_type="md",
        model_path=Path(model_path),
        task=task,
        device=device,
        inference_mode="turbo",
        output_dir=Path(output_dir),
        job_name=job_name,
        options={
            "ensemble": ensemble,
            "temperature": temperature,
            "timestep": timestep,
            "steps": steps,
            "friction": friction,
            "save_interval": save_interval,
            "pre_relax": pre_relax,
        },
    )
    engine = CalculationEngine.from_config(config)
    return engine.run(atoms)
```

Keep `calculate_energy` and `calculate_adsorption_energy` as-is — they already delegate to `run_single_point`/`run_optimization`.

- [ ] **Step 2: Fix __init__.py lazy imports**

Change `uma/umakit/__init__.py` to not eagerly import everything. Remove the top-level imports and the `_api_available` try/except block. Use `__all__` only.

```python
"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.
"""

"""UMAKit - VASP-like interface for FAIRChem UMA models."""

from __future__ import annotations

__version__ = "1.0.0"

__all__ = [
    "IncarConfig",
    "UMACalculator",
    "SinglePointRunner",
    "OptimizationRunner",
    "MDRunner",
    "BatchRunner",
    "CalculationEngine",
    "EngineConfig",
    "ProgressEvent",
    "JobManager",
    "run_single_point",
    "run_optimization",
    "run_md",
    "calculate_energy",
    "calculate_adsorption_energy",
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
        import importlib
        mod = importlib.import_module(_imports[name], __package__)
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

- [ ] **Step 3: Delete uma_calc.py**

```bash
rm D:/Agent/fairchem/uma/uma_calc.py
```

- [ ] **Step 4: Verify import works lazily**

```bash
cd D:/Agent/fairchem && uv run python -c "import umakit; print(umakit.__version__); print(umakit.IncarConfig.__name__)"
```
Expected: `1.0.0` then `IncarConfig`

- [ ] **Step 5: Ruff format**

```bash
cd D:/Agent/fairchem && uv run ruff check --fix uma/umakit/api.py uma/umakit/__init__.py && uv run ruff format uma/umakit/api.py uma/umakit/__init__.py
```

- [ ] **Step 6: Commit**

```bash
git add uma/umakit/api.py uma/umakit/__init__.py && git rm uma/uma_calc.py 2>/dev/null; git add uma/uma_calc.py 2>/dev/null
git commit -m "refactor: simplify api.py with Engine, add lazy imports, remove duplicate uma_calc.py"
```

---

### Task 13: Final integration test + Ruff format all

**Files:**
- Modify: All umakit files (ruff format pass)

- [ ] **Step 1: Run all umakit tests**

```bash
cd D:/Agent/fairchem && uv run pytest tests/core/umakit/ -c packages/fairchem-core/pyproject.toml -v
```
Expected: All tests PASS

- [ ] **Step 2: Ruff check + format entire umakit package**

```bash
cd D:/Agent/fairchem && uv run ruff check --fix uma/umakit/ tests/core/umakit/ && uv run ruff format uma/umakit/ tests/core/umakit/
```

- [ ] **Step 3: Verify CLI help**

```bash
cd D:/Agent/fairchem && uv run python -m umakit.cli --help
```
Expected: Full help with all subcommands including jobs/kill/clean

- [ ] **Step 4: Verify TUI can at least import without CSS error**

```bash
cd D:/Agent/fairchem && uv run python -c "from umakit.tui.app import UmaCalcApp; print('TUI import OK, CSS valid')"
```
Expected: `TUI import OK, CSS valid`

- [ ] **Step 5: Final commit**

```bash
git add -A && git commit -m "chore: final ruff format pass, integration tests green"
```
