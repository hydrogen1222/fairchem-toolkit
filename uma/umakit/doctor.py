# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Environment diagnostic tool for UMA Calculator.

Checks Python, PyTorch, CUDA, GPU compatibility, and model files.
Provides exact fix commands when problems are found.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


def run_diagnostics(
    model_path: str | Path | None = None,
) -> tuple[list[dict[str, Any]], int]:
    """Run all environment checks.

    Args:
        model_path: Optional path to model checkpoint to check.

    Returns:
        Tuple of (results list, number of failures).
    """
    checks: list[dict[str, Any]] = []
    failures = 0

    # 1. Python version
    py_ver = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    if sys.version_info >= (3, 9):
        checks.append({"name": "Python", "value": py_ver, "status": "ok"})
    else:
        checks.append(
            {
                "name": "Python",
                "value": py_ver,
                "status": "fail",
                "detail": f"Python >= 3.9 required, found {py_ver}",
            }
        )
        failures += 1

    # 2. PyTorch
    try:
        import torch

        torch_ver = torch.__version__
        checks.append({"name": "PyTorch", "value": torch_ver, "status": "ok"})
    except ImportError:
        checks.append(
            {
                "name": "PyTorch",
                "value": "not installed",
                "status": "fail",
                "detail": "Install: uv pip install torch",
            }
        )
        failures += 1
        # Can't continue without PyTorch
        if model_path:
            checks.append(
                {"name": "Model file", "value": str(model_path), "status": "skip"}
            )
        return checks, failures + 1

    # 3. CUDA
    cuda_available = torch.cuda.is_available()
    cuda_suffix = (
        f" (CUDA {torch.version.cuda})"
        if hasattr(torch.version, "cuda") and torch.version.cuda
        else ""
    )

    if cuda_available:
        checks.append(
            {"name": "CUDA available", "value": f"True{cuda_suffix}", "status": "ok"}
        )
    else:
        checks.append(
            {
                "name": "CUDA available",
                "value": "False",
                "status": "warn",
                "detail": "No CUDA GPU detected. Calculations will run on CPU (--device cpu).",
            }
        )

    # 4. GPU compatibility (only if CUDA is available)
    if cuda_available:
        for i in range(torch.cuda.device_count()):
            gpu_name = torch.cuda.get_device_name(i)
            props = torch.cuda.get_device_properties(i)
            vram_gb = props.total_memory / (1024**3)
            major, minor = torch.cuda.get_device_capability(i)
            gpu_cc = f"sm_{major}{minor}"

            arch_list = torch.cuda.get_arch_list()
            arch_ok = (not arch_list) or (gpu_cc in arch_list)

            value_str = f"{gpu_name} ({vram_gb:.0f} GB, CC {major}.{minor})"

            if arch_ok:
                checks.append(
                    {
                        "name": f"GPU {i}",
                        "value": value_str,
                        "status": "ok",
                    }
                )
            else:
                cuda_ver = torch.version.cuda or "unknown"
                py_major = sys.version_info.major
                py_minor = sys.version_info.minor
                py_supported_26 = (py_major, py_minor) <= (3, 12)

                if py_supported_26:
                    fixes = [
                        "# torch 2.6.0+cu126 is the last build with Pascal (sm_6x) support.",
                        "# fairchem-core requires torch~=2.8.0, so we override it.",
                        "# Add this to [tool.uv] in uma/pyproject.toml, then: uv sync",
                        'override-dependencies = ["torch==2.6.0+cu126"]',
                    ]
                else:
                    fixes = [
                        f"Python {py_major}.{py_minor} only supports torch>=2.8, which dropped",
                        "sm_6x across ALL CUDA variants (cu126/cu128/cu129 are identical).",
                        "torch 2.6.0 (last with sm_6x) has no Python 3.13 wheels.",
                        "",
                        "Workable options:",
                        "  1. Use CPU mode: --device cpu  (works immediately)",
                        "  2. Downgrade Python to 3.12, then use torch==2.6.0+cu126",
                        '  3. Build torch from source: TORCH_CUDA_ARCH_LIST="6.1"',
                    ]

                checks.append(
                    {
                        "name": f"GPU {i}",
                        "value": value_str,
                        "status": "fail",
                        "detail": (
                            f"Architecture {gpu_cc} — NOT in PyTorch build ({', '.join(arch_list)}).\n"
                            f"  PyTorch {torch_ver} (CUDA {cuda_ver}) dropped Pascal/Maxwell kernels.\n"
                            f"\n" + "\n".join(f"  {f}" for f in fixes) + "\n"
                            "  After fixing, re-run: uv run uma_calc doctor"
                        ),
                    }
                )
                failures += 1
    else:
        checks.append({"name": "GPU", "value": "none (CPU only)", "status": "warn"})

    # 5. fairchem-core
    try:
        import importlib.util

        fc_spec = importlib.util.find_spec("fairchem.core")
        if fc_spec is not None:
            checks.append(
                {"name": "fairchem-core", "value": "installed", "status": "ok"}
            )
        else:
            raise ImportError("fairchem-core not found")
    except ImportError:
        checks.append(
            {
                "name": "fairchem-core",
                "value": "not installed",
                "status": "fail",
                "detail": "Install: cd packages/fairchem-core && uv pip install -e '.[dev]'",
            }
        )
        failures += 1

    # 6. UMAKit
    try:
        from umakit import __version__ as uma_ver

        checks.append({"name": "UMAKit", "value": f"v{uma_ver}", "status": "ok"})
    except ImportError:
        checks.append(
            {
                "name": "UMAKit",
                "value": "not installed",
                "status": "fail",
                "detail": "Install: cd uma && uv pip install -e .",
            }
        )
        failures += 1

    # 7. Model file (optional)
    if model_path:
        mp = Path(model_path)
        if mp.exists():
            size_gb = mp.stat().st_size / (1024**3)
            checks.append(
                {
                    "name": "Model file",
                    "value": f"{mp.name} ({size_gb:.1f} GB)",
                    "status": "ok",
                }
            )
        else:
            checks.append(
                {
                    "name": "Model file",
                    "value": f"{mp} — not found",
                    "status": "warn",
                    "detail": "Download from https://fair-chem.github.io/models/uma/",
                }
            )
    else:
        checks.append(
            {
                "name": "Model file",
                "value": "not specified",
                "status": "warn",
                "detail": "Pass --model <path> or specify MODEL_PATH in INCAR",
            }
        )

    # 8. Summary recommendation
    if failures == 0:
        checks.append(
            {
                "name": "Verdict",
                "value": "Ready" if cuda_available else "Ready (CPU mode)",
                "status": "ok",
            }
        )
    else:
        checks.append(
            {
                "name": "Verdict",
                "value": f"{failures} issue(s) to resolve",
                "status": "fail",
            }
        )

    return checks, failures


def format_diagnostics(checks: list[dict[str, Any]]) -> str:
    """Format diagnostic results as a readable text table.

    Args:
        checks: List of check result dicts from run_diagnostics().

    Returns:
        Formatted string ready for display.
    """
    icons = {"ok": "✓", "fail": "✗", "warn": "!", "skip": "-"}

    lines = []
    lines.append("")
    lines.append("=" * 68)
    lines.append(" UMAKit Environment Diagnostic")
    lines.append("=" * 68)
    lines.append("")

    max_name = max(len(c["name"]) for c in checks)

    for c in checks:
        icon = icons.get(c["status"], "?")
        name_padded = c["name"].ljust(max_name)
        value = c.get("value", "")

        if c["status"] == "fail":
            lines.append(f"  {name_padded}  {value:30s}  {icon} FAIL")
        elif c["status"] == "warn":
            lines.append(f"  {name_padded}  {value:30s}  {icon} WARN")
        elif c["status"] == "skip":
            lines.append(f"  {name_padded}  {value:30s}  {icon} SKIP")
        else:
            lines.append(f"  {name_padded}  {value:30s}  {icon}")

        if c.get("detail"):
            for detail_line in c["detail"].split("\n"):
                lines.append(f"    {detail_line}")

    lines.append("")
    lines.append("=" * 68)

    total_fails = sum(1 for c in checks if c["status"] == "fail")
    total_warns = sum(1 for c in checks if c["status"] == "warn")

    if total_fails == 0 and total_warns == 0:
        lines.append(" All checks passed. Ready to run calculations.")
    elif total_fails == 0:
        lines.append(f" All required checks passed ({total_warns} warning(s)).")
    else:
        lines.append(
            f" {total_fails} issue(s) found. Fix before running CUDA calculations."
        )
        lines.append(" After fixing, re-run: uv run uma_calc doctor")

    lines.append("=" * 68)

    return "\n".join(lines)
