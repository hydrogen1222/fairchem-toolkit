# UMA Calculator User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [Input Files](#input-files)
5. [Calculation Types](#calculation-types)
6. [Output Files](#output-files)
7. [Command Reference](#command-reference)
8. [Task Types](#task-types)
9. [Troubleshooting](#troubleshooting)

## Introduction

UMA Calculator is a command-line tool that provides a VASP-like interface for running MLIP (Machine Learning Interatomic Potential) calculations using FAIRChem's UMA models. It is designed to be familiar to VASP users while providing the flexibility and performance of modern MLIP models.

## Installation

### Prerequisites

- Python 3.9+
- fairchem-core
- ASE (Atomic Simulation Environment)

### Setup

1. Ensure fairchem-core is installed:
```bash
pip install -e packages/fairchem-core[dev]
```

2. Add the uma_calc directory to your PATH:
```bash
export PATH=$PATH:/path/to/uma_package
```

## Basic Usage

### Single Point Calculation

Calculate energy, forces, and stress for a structure:

```bash
uma_calc sp structure.cif --model uma-s-1.pt --task omat
```

### Geometry Optimization

Optimize atomic positions until forces converge:

```bash
# Basic optimization
uma_calc opt structure.cif --model uma-s-1.pt

# With cell optimization
uma_calc opt structure.cif --model uma-s-1.pt --cell-opt

# Tight convergence
uma_calc opt structure.cif --model uma-s-1.pt --fmax 0.01 --max-steps 1000
```

### Molecular Dynamics

Run MD simulation:

```bash
# NVT ensemble at 300K
uma_calc md structure.cif --model uma-s-1.pt --ensemble NVT --temp 300 --steps 10000

# NVE ensemble
uma_calc md structure.cif --model uma-s-1.pt --ensemble NVE --temp 300 --steps 5000
```

## Input Files

### INCAR.uma Format

The INCAR.uma file uses VASP-style syntax:

```
# Comment lines start with #
KEY = VALUE

# Boolean values
CELL_OPT = .TRUE.
FIX_SYMMETRY = .FALSE.

# Numeric values
FMAX = 0.05
MAX_STEPS = 500
TEMPERATURE = 300.0

# String values
TASK = omat
OPT_ALGO = FIRE
```

### Required Keys

| Key | Description | Default |
|-----|-------------|---------|
| CALC_TYPE | Type of calculation (SP, OPT, MD) | SP |
| TASK | Task type (omat, omol, oc20, etc.) | omat |
| MODEL_PATH | Path to model checkpoint | uma-s-1.pt |
| DEVICE | Device (cpu, cuda) | cpu |

### Optional Keys

| Key | Description | Default |
|-----|-------------|---------|
| INFERENCE_MODE | Inference mode (default, turbo) | default |
| FMAX | Force convergence threshold (eV/Å) | 0.05 |
| MAX_STEPS | Maximum optimization/MD steps | 500 |
| OPT_ALGO | Optimizer (FIRE, BFGS, LBFGS) | FIRE |
| CELL_OPT | Optimize cell parameters | .FALSE. |
| FIX_SYMMETRY | Preserve symmetry | .FALSE. |
| TEMPERATURE | MD temperature (K) | 300 |
| TIMESTEP | MD time step (fs) | 1.0 |
| SAVE_INTERVAL | Trajectory save interval | 10 |

## Calculation Types

### Single Point (SP)

Calculates:
- Total energy (eV)
- Atomic forces (eV/Å)
- Stress tensor (eV/Å³) - if supported by task

Output files:
- OUTCAR - Detailed results
- CONTCAR - Structure (same as input)
- uma_results.json - JSON format

### Geometry Optimization (OPT)

Optimizes atomic positions to minimize forces.

Options:
- **Position optimization only**: Atoms relax, cell fixed
- **Cell optimization**: Both atoms and cell parameters relax (requires stress support)
- **Symmetry constraint**: Preserve space group symmetry

Convergence criteria:
- All forces < fmax (eV/Å)
- Maximum steps reached

Output files:
- OUTCAR - Final results
- OSZICAR - Optimization trajectory
- CONTCAR - Optimized structure
- uma_results.json - Results

### Molecular Dynamics (MD)

Simulates dynamics at constant temperature or energy.

Ensembles:
- **NVT**: Constant number, volume, temperature (Langevin thermostat)
- **NVE**: Constant number, volume, energy (microcanonical)

Output files:
- OUTCAR - Summary
- XDATCAR - VASP-style trajectory
- trajectory.traj - ASE trajectory
- uma_results.json - Results

Tips for MD:
- Use `DEVICE = cuda` for significant speedup
- Use `INFERENCE_MODE = turbo` for 1.5-2x performance
- Start with short runs (1000 steps) to test stability
- TIMESTEP of 1 fs is typical, can use 2 fs for light elements

### Batch Processing

Process multiple structures in a directory:

```bash
uma_calc batch structures/ --model uma-s-1.pt --calc-type sp --output results/
```

Creates individual output directories for each structure and a batch_summary.json file.

## Output Files

### OUTCAR

VASP-style main output containing:
- System information
- Model details
- Input structure
- Energy, forces, stress
- Optimization/MD summary
- Timing information

### OSZICAR

Optimization progress showing:
- Step number
- Energy
- Energy per atom
- Maximum force (fmax)
- RMS force
- Convergence indicator

### CONTCAR

Final structure in VASP POSCAR format. For optimization, this is the optimized geometry. For MD, this is the final snapshot.

### XDATCAR

MD trajectory in VASP format with direct coordinates.

### uma_results.json

Machine-readable JSON containing:
- System information
- Calculation results
- Force statistics
- Pressure
- Timing

## Command Reference

### Global Options

All commands support:
- `-h, --help`: Show help message
- `-v, --verbose`: Verbose output

### sp (Single Point)

```bash
uma_calc sp <structure> --model <path> [options]

Options:
  --model PATH       Model checkpoint (required)
  --task TASK        Task type [omat, omol, oc20, odac, omc]
  --device DEVICE    Device [cpu, cuda]
  -o, --output DIR   Output directory
```

### opt (Optimization)

```bash
uma_calc opt <structure> --model <path> [options]

Options:
  --model PATH          Model checkpoint (required)
  --task TASK           Task type
  --device DEVICE       Device
  --fmax FLOAT          Convergence threshold
  --max-steps INT       Maximum steps
  --optimizer ALGO      Optimizer [FIRE, BFGS, LBFGS]
  --cell-opt            Enable cell optimization
  --fix-symmetry        Preserve symmetry
  -o, --output DIR      Output directory
```

### md (Molecular Dynamics)

```bash
uma_calc md <structure> --model <path> [options]

Options:
  --model PATH          Model checkpoint (required)
  --task TASK           Task type
  --device DEVICE       Device
  --ensemble ENSEMBLE   Ensemble [NVT, NVE]
  --temp FLOAT          Temperature (K)
  --timestep FLOAT      Time step (fs)
  --steps INT           Number of steps
  --friction FLOAT      Friction coefficient (NVT)
  --save-interval INT   Save interval
  -o, --output DIR      Output directory
```

### batch (Batch Processing)

```bash
uma_calc batch <input_dir> --model <path> [options]

Options:
  --model PATH          Model checkpoint (required)
  --task TASK           Task type
  --device DEVICE       Device
  --calc-type TYPE      Calculation type [sp, opt]
  --pattern PATTERN     File pattern
  -o, --output DIR      Output directory
```

### template

```bash
uma_calc template <type> [-o FILE]

Types:
  sp    Single point template
  opt   Optimization template
  md    MD template
```

## Task Types

| Task | System Type | Charge/Spin | Stress | Use Case |
|------|-------------|-------------|--------|----------|
| omat | Inorganic materials | Optional | Yes | Bulk materials, batteries |
| omol | Molecules | Required | No | Organic molecules, drug discovery |
| oc20 | Catalysis surfaces | Optional | Yes | Surface adsorption |
| oc25 | Catalysis (extended) | Optional | Yes | Extended catalysis dataset |
| odac | MOFs | Optional | Yes | Metal-organic frameworks |
| omc | Molecular crystals | Optional | Yes | Organic crystals |

### OMOL Task Notes

For molecular calculations (omol), you must provide charge and spin multiplicity:

```python
from ase.io import read

atoms = read("molecule.xyz")
atoms.info["charge"] = 0    # Total charge
atoms.info["spin"] = 1      # Spin multiplicity (2S+1)
```

Or in XYZ file comment line:
```
2
charge=0 spin=1
H 0 0 0
H 0 0 0.74
```

## Troubleshooting

### Model Loading Errors

**Error**: `Model file not found: uma-s-1.pt`

Solution: Provide full path to model checkpoint:
```bash
uma_calc sp structure.cif --model /path/to/uma-s-1.pt
```

### CUDA Errors

**Error**: `CUDA out of memory`

Solutions:
- Use CPU: `--device cpu`
- Reduce system size
- Use turbo mode for MD

### Convergence Issues

**Problem**: Optimization doesn't converge

Solutions:
- Increase MAX_STEPS
- Check initial structure for clashes
- Try different optimizer (BFGS, LBFGS)
- Check force field suitability for system

### MD Instability

**Problem**: MD simulation crashes

Solutions:
- Reduce timestep (try 0.5 fs)
- Check initial structure
- Start with energy minimization
- Use NVT instead of NVE for equilibration
