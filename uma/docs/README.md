# UMAKit — Universal Material Application Calculator

A VASP-compatible interface for FAIRChem's UMA machine-learning interatomic potential models.

> **Documentation:**
> - **[中文用户手册 (Chinese Manual)](README_CN.md)** — 完整的中文使用手册，含所有命令参考、INCAR 配置、故障排除
> - **[English User Manual](README_EN.md)** — Complete reference manual with all commands, INCAR keys, troubleshooting
> - [Examples](EXAMPLES.md) — Example calculation recipes
> - [User Guide](USER_GUIDE.md) — Original usage instructions

## Quick Start

```bash
# Install
cd uma && uv pip install -e .

# Interactive TUI mode
uma_calc tui

# CLI: single-point energy
uma_calc sp structure.cif --model uma-s-1.pt --task omat

# CLI: geometry optimization
uma_calc opt POSCAR --model uma-s-1.pt --fmax 0.02

# CLI: molecular dynamics
uma_calc md POSCAR --model uma-s-1.pt --ensemble NVT --temp 300 --steps 10000

# CLI: batch processing
uma_calc batch structures/ --model uma-s-1.pt --pattern "*.cif"

# Background job management
uma_calc jobs       # list jobs
uma_calc kill <id>  # kill a job
uma_calc clean      # clean completed jobs
```

## Features

- **CLI + TUI + Python API** — Three interfaces sharing one execution engine
- **Calculation Types** — Single point, geometry optimization (FIRE/BFGS/LBFGS), molecular dynamics (NVT/NVE), batch processing
- **VASP-compatible Output** — OUTCAR, CONTCAR, XDATCAR, OSZICAR formats
- **Background Jobs** — Submit, detach, re-attach, and kill long-running calculations
- **Cross-platform** — Windows, Linux, macOS | CPU & CUDA
- **Resource Control** — CPU threads, GPU memory, inference mode selection

## License

MIT License — Copyright (c) Meta Platforms, Inc. and affiliates.
