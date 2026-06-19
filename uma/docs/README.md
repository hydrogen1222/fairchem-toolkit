# UMA Calculator

A VASP-like command-line interface for FAIRChem's Universal Material Application (UMA) models.

## Overview

UMA Calculator provides a familiar interface for running machine learning interatomic potential (MLIP) calculations using Meta's FAIRChem UMA models. It follows VASP-style conventions for input/output files while leveraging the power of FAIRChem's ASE calculator integration.

## Features

- **Calculation Types**: Single point, geometry optimization, molecular dynamics, batch processing
- **Output Formats**: VASP-style (OUTCAR, OSZICAR, CONTCAR, XDATCAR), JSON, ASE trajectory
- **Input Methods**: INCAR-style configuration files or command-line arguments
- **Multiple Tasks**: Support for omat, omol, oc20, odac, omc tasks
- **Flexible Device**: CPU or CUDA computation

## Installation

```bash
# Ensure you have fairchem-core installed
pip install fairchem-core

# Add uma_calc to your PATH
export PATH=$PATH:/path/to/uma_package
```

## Quick Start

### 1. Generate a Template

```bash
# Generate template for single point calculation
uma_calc template sp -o INCAR.uma

# Or for geometry optimization
uma_calc template opt -o INCAR.uma
```

### 2. Edit INCAR.uma

```
CALC_TYPE = SP
TASK = omat
MODEL_PATH = /path/to/uma-s-1.pt
DEVICE = cpu
```

### 3. Run Calculation

```bash
# With INCAR file
uma_calc run

# Or use command-line directly
uma_calc sp structure.cif --model uma-s-1.pt --task omat
```

## Commands

| Command | Description |
|---------|-------------|
| `uma_calc run` | Run from INCAR.uma configuration file |
| `uma_calc sp` | Single point calculation |
| `uma_calc opt` | Geometry optimization |
| `uma_calc md` | Molecular dynamics |
| `uma_calc batch` | Batch processing multiple structures |
| `uma_calc template` | Generate template INCAR files |

## Output Files

| File | Description |
|------|-------------|
| `OUTCAR` | Main output with detailed results (VASP-style) |
| `CONTCAR` | Final/optimized structure |
| `OSZICAR` | Optimization progress log |
| `XDATCAR` | MD trajectory |
| `uma_results.json` | Machine-readable JSON output |
| `trajectory.traj` | ASE trajectory file |

## Documentation

- **[中文文档 (Chinese)](README_CN.md)** - 完整的中文使用手册
- **[English Documentation](README_EN.md)** - Complete English user manual
- [User Guide](USER_GUIDE.md) - Original usage instructions
- [Examples](EXAMPLES.md) - Example calculations
- [Report V2](REPORT_V2.md) - Version 2.0 refactoring report

## License

MIT License - See LICENSE file for details.
