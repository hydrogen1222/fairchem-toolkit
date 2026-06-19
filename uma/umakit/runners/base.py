# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""
Base runner class for UMA calculations.

Provides common functionality for all calculation runners,
including output directory management and logging.
"""

from __future__ import annotations

import sys
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from ase import Atoms

    from umakit.calculator import UMACalculator


class BaseRunner(ABC):
    """Base class for all calculation runners.

    Provides common infrastructure for running calculations,
    managing output, and handling errors.

    Attributes:
        calculator: UMA calculator wrapper
        output_dir: Directory for output files
        verbose: Whether to print verbose output
        job_name: Optional job name for the calculation

    Example:
        >>> class MyRunner(BaseRunner):
        ...     def run(self, atoms):
        ...         # Implementation
        ...         pass
    """

    def __init__(
        self,
        calculator: UMACalculator,
        output_dir: Path | str = ".",
        verbose: bool = True,
        job_name: str | None = None,
    ):
        """Initialize base runner.

        Args:
            calculator: UMA calculator wrapper
            output_dir: Directory for output files
            verbose: Whether to print progress messages
            job_name: Optional job name for organizing results
        """
        self.calculator = calculator
        self.job_name = job_name
        self.verbose = verbose

        # Build output directory path
        base_dir = Path(output_dir)
        if job_name:
            self.output_dir = base_dir / job_name
        else:
            self.output_dir = base_dir

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "info") -> None:
        """Print log message if verbose mode is enabled.

        Args:
            message: Message to print
            level: Log level (info, warning, error)
        """
        if not self.verbose:
            return

        prefix = {
            "info": "  ",
            "warning": "! ",
            "error": "ERROR: ",
        }.get(level, "  ")

        print(f"{prefix}{message}")

    def print_header(self, title: str) -> None:
        """Print section header.

        Args:
            title: Section title
        """
        if self.verbose:
            print()
            print("-" * 80)
            print(f" {title}")
            print("-" * 80)

    @abstractmethod
    def run(self, atoms: Atoms) -> dict[str, Any]:
        """Run calculation on structure.

        Args:
            atoms: ASE Atoms object

        Returns:
            Dictionary with calculation results
        """
        pass

    def _prepare_atoms(self, atoms: Atoms) -> Atoms:
        """Prepare atoms for calculation.

        Handles task-specific preparation like setting charge/spin for molecules
        and ensuring PBC is correctly set for periodic systems.

        Args:
            atoms: Input ASE Atoms object

        Returns:
            Prepared Atoms object
        """
        task = self.calculator.task

        # Ensure PBC is set correctly for periodic systems
        # For bulk materials (omat, oc20, odac, omc), PBC should be True
        if task in ("omat", "oc20", "oc25", "odac", "omc"):
            if not atoms.pbc.any():
                self.log("Setting PBC=True for periodic system", level="warning")
                atoms.pbc = True
            # Log cell info for debugging
            cell = atoms.cell
            if cell.volume > 0:
                self.log(f"Cell: {cell.lengths()[0]:.4f} x {cell.lengths()[1]:.4f} x {cell.lengths()[2]:.4f} Å")
            else:
                raise ValueError("Invalid cell: zero volume. Check input structure.")
        elif task == "omol":
            # Molecules should not have PBC
            atoms.pbc = False
            if "charge" not in atoms.info:
                self.log("Setting default charge=0 for omol task", level="warning")
                atoms.info["charge"] = 0
            if "spin" not in atoms.info:
                self.log("Setting default spin=1 for omol task", level="warning")
                atoms.info["spin"] = 1

        return atoms

    def _get_calculator(self) -> "Calculator":
        """Get ASE calculator instance.

        Returns:
            ASE Calculator
        """
        return self.calculator.get_calculator()

    def _write_summary(self, results: dict[str, Any], atoms: Atoms) -> None:
        """Write calculation summary to stdout.

        Args:
            results: Results dictionary
            atoms: ASE Atoms object
        """
        if not self.verbose:
            return

        energy = results.get("energy")
        forces = results.get("forces")

        print()
        print("=" * 80)
        if self.job_name:
            print(f" SUMMARY - {self.job_name}")
        else:
            print(" SUMMARY")
        print("=" * 80)

        if energy is not None:
            print(f"Total energy:     {energy:16.8f} eV")
            print(f"Energy per atom:  {energy / len(atoms):16.8f} eV/atom")

        if forces is not None:
            import numpy as np

            force_mags = np.linalg.norm(forces, axis=1)
            print(f"Max force:        {np.max(force_mags):16.8f} eV/Å")
            print(f"RMS force:        {np.sqrt(np.mean(force_mags**2)):16.8f} eV/Å")

        if "stress" in results and results["stress"] is not None:
            import numpy as np

            stress = results["stress"]
            pressure = -(stress[0] + stress[1] + stress[2]) / 3.0 * 160.2177
            print(f"Pressure:         {pressure:16.8f} GPa")

        calc_time = results.get("time")
        if calc_time is not None:
            print(f"Calculation time: {calc_time:16.2f} s")

        print("=" * 80)
