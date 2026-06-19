"""
Copyright (c) Meta Platforms, Inc. and affiliates.

This source code is licensed under the MIT license found in the
LICENSE file in the root directory of this source tree.

Unified execution engine for UMA calculations.

Provides CalculationEngine as the single entry point for CLI, TUI, and API.
"""

from __future__ import annotations

import asyncio
import contextlib
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from umakit.calculator import UMACalculator
from umakit.protocols import ProgressCallback, ProgressEvent

if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from typing import Any, Literal

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

    VALID_CALC_TYPES: ClassVar[set[str]] = {"sp", "opt", "md", "batch"}

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
            "ensemble",
            "temperature",
            "timestep",
            "steps",
            "friction",
            "save_interval",
            "pre_relax",
            "pre_relax_steps",
            "pre_relax_fmax",
        }
        known_batch = {"pattern", "sub_calc_type", "parallel", "max_workers"}
        known_all = known_sp | known_opt | known_md | known_batch
        unknown = set(self.config.options.keys()) - known_all
        for key in unknown:
            warnings.warn(
                f"Unknown option '{key}' for calc_type '{self.config.calc_type}'"
            )

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
        from umakit.runners.md import MDRunner  # noqa: PLC0415
        from umakit.runners.optimization import OptimizationRunner  # noqa: PLC0415
        from umakit.runners.singlepoint import SinglePointRunner  # noqa: PLC0415

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
            try:
                return self.run(atoms, progress_callback=progress_callback)
            except Exception as exc:
                event = ProgressEvent(
                    phase="error",
                    message=f"Calculation failed: {exc}",
                )
                loop.call_soon_threadsafe(queue.put_nowait, event)
                raise

        task = loop.run_in_executor(None, blocking_work)

        try:
            while True:
                event = await queue.get()
                yield event
                if event.phase in ("done", "error"):
                    break
        except asyncio.CancelledError:
            task.cancel()
            # Don't yield here — async generators shouldn't yield
            # during CancelledError. The caller handles cleanup.
        finally:
            with contextlib.suppress(asyncio.CancelledError, Exception):
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
        from umakit.runners.batch import BatchRunner  # noqa: PLC0415

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
            progress_callback=progress_callback,
        )
        return runner.run_from_files(files)
