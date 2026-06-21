# UMAKit — Universal Material Application Calculator

A VASP-compatible CLI / TUI / Python API for FAIRChem UMA machine-learning interatomic potentials.

## Quick Start

```bash
# 1. Detect your GPU and get the matching PyTorch command (CPU-only users can skip).
uv run uma_calc setup

# 2. Create a pinned venv (Python 3.12) + install everything from the lockfile.
#    uv auto-creates .venv. Do NOT use `pip install -r requirements.txt`
#    (that's the upstream CI snapshot, torch 2.8 — conflicts with this fork).
uv sync

# 3. Verify & run
uv run uma_calc doctor              # comprehensive environment diagnostic
uv run uma_calc --help              # show all commands
uv run uma_calc tui                 # launch interactive TUI
uv run uma_calc template sp         # generate INCAR template
```

> **Note:** All commands use `uv run` prefix which auto-detects the `.venv`. Alternatively, activate the venv first: `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows), then run `uma_calc` directly.

### CUDA vs CPU Installation

| Machine | fairchem-core install | UMAKit usage |
|---------|----------------------|--------------|
| **CUDA GPU** | Install fairchem-core with CUDA PyTorch | `--device cuda` (auto-detected) |
| **CPU only** | fairchem-core uses CPU PyTorch by default | `--device cpu` (default) |

UMAKit itself does not ship PyTorch — it inherits whatever PyTorch fairchem-core provides. Verify CUDA availability:
```bash
uv run python -c "import torch; print('CUDA OK' if torch.cuda.is_available() else 'CPU only')"
```

> **GPU install guidance (supports GTX 900 series and newer):** The right PyTorch build depends on your GPU's compute capability. Run this **before** installing torch — it uses `nvidia-smi` and works even with no PyTorch installed yet:
> ```bash
> uv run uma_calc setup      # detect GPU + print the exact torch install command
> uv run uma_calc doctor     # verify after install
> ```
> Supported floor is **Maxwell (GTX 900 series, e.g. GTX 960)**; Kepler (GTX 700/600) is not supported (no prebuilt PyTorch wheel). The recommendation table:
>
> | GPU family | CC | Recommended torch |
> |---|---|---|
> | Maxwell (GTX 750/9xx) | sm_50/52 | `torch==2.6.0+cu124` |
> | Pascal (GTX 10xx, P104-100) | sm_60/61 | `torch==2.6.0+cu124` |
> | Volta–Hopper (V100…H100, RTX 20/30/40) | sm_70–90 | `torch==2.6.0+cu124` |
> | Blackwell (RTX 50) | sm_100/120 | `torch==2.8.0+cu128` |
> | Kepler (GTX 700/600) | sm_30/37 | not supported |
>
> Why: PyTorch 2.7+ dropped `sm_50`/`sm_60` from its prebuilt CUDA wheels, so old cards (Maxwell/Pascal) must stay on `torch 2.6.0+cu124`; its `sm_50`/`sm_60` kernels are binary-compatible with `sm_52`/`sm_61`. The workspace already pins `torch==2.6.0+cu124` by default, so `uv sync` works out of the box for Maxwell–Hopper; only Blackwell needs an override. If the download fails, enable a proxy first: `clashctl on`.


## Interfaces

| Interface | How to use | Best for |
|-----------|-----------|----------|
| **CLI** | `uma_calc <command>` in terminal | Scripts, HPC jobs, automation |
| **TUI** | `uma_calc tui` | Interactive exploration, live progress |
| **Python API** | `from umakit.api import ...` | Workflows, custom analysis |

## Documentation

- 📖 **[English User Manual](docs/README_EN.md)** — Complete reference: all commands, INCAR keywords, output files, task types, troubleshooting, performance guide
- 📖 **[中文用户手册](docs/README_CN.md)** — 完整中文参考手册
- 💡 **[Examples](docs/EXAMPLES.md)** — Calculation recipes

## Features

- **Calculation types:** Single-point (SP), Geometry optimization (OPT, FIRE/BFGS/LBFGS), Molecular dynamics (MD, NVT/NVE), Batch processing
- **VASP-compatible output:** OUTCAR, CONTCAR, XDATCAR, OSZICAR formats
- **Background jobs:** Submit, detach, re-attach, kill long-running calculations
- **INCAR files:** VASP-style `KEY = VALUE` configuration format
- **Cross-platform:** Windows, Linux, macOS | CPU & CUDA
- **Resource control:** CPU threads, GPU memory (activation checkpointing), inference mode (default/turbo)
- **Live progress:** Structured progress events, indeterminate spinner for SP, step counter for OPT/MD

## Package Structure

```
uma/
├── uma_calc -> umakit/cli.py:main    # CLI entry point
├── umakit/
│   ├── engine.py                     # CalculationEngine (unified execution)
│   ├── protocols.py                  # ProgressEvent protocol
│   ├── jobs.py                       # JobManager (background tasks)
│   ├── calculator.py                 # UMACalculator wrapper
│   ├── config.py                     # INCAR config parser
│   ├── api.py                        # Python API functions
│   ├── cli.py                        # CLI (argparse, 10 subcommands)
│   ├── runners/                      # SinglePoint, Optimization, MD, Batch
│   ├── tui/                          # Textual TUI (app, screens)
│   └── writers/                      # OUTCAR, CONTCAR, XDATCAR, OSZICAR, JSON
├── docs/                             # Manuals and examples
├── templates/                        # INCAR template files
└── examples/                         # Example scripts
```

## License

MIT License — Copyright (c) Meta Platforms, Inc. and affiliates.
