# UMAKit — Universal Material Application Calculator

A VASP-compatible CLI / TUI / Python API for FAIRChem UMA machine-learning interatomic potentials.

## Quick Start

```bash
# Install
uv pip install -e .

# Launch interactive TUI
uma_calc tui

# Single-point energy
uma_calc sp structure.cif --model uma-s-1.pt --task omat --device cuda

# Geometry optimization
uma_calc opt POSCAR --model uma-s-1.pt --fmax 0.02 --cell-opt

# Molecular dynamics (NVT @ 300K, 10 ps)
uma_calc md POSCAR --model uma-s-1.pt --ensemble NVT --temp 300 --steps 10000

# Batch processing
uma_calc batch structures/ --model uma-s-1.pt --pattern "*.cif"

# Background jobs
uma_calc jobs               # list all jobs
uma_calc kill <job_id>      # kill a job
uma_calc clean              # clean completed/failed jobs
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
