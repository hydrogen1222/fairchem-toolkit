# UMAKit — Universal Material Application Calculator

A VASP-compatible CLI / TUI / Python API for FAIRChem UMA machine-learning interatomic potentials.

## Quick Start

```bash
# 1. Install fairchem-core first (NOT on PyPI — install from local packages/)
cd ../packages/fairchem-core
uv pip install -e ".[dev]"

# 2. Install UMAKit
cd ../../uma
uv pip install -e .

# 3. Run
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
