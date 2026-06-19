# UMA Calculator User Manual

## Table of Contents

1. [Introduction](#introduction)
2. [Directory Structure](#directory-structure)
3. [Working Principles](#working-principles)
4. [Installation](#installation)
5. [Usage Guide](#usage-guide)
6. [Troubleshooting](#troubleshooting)

---

## Introduction

UMA Calculator is a materials science computational tool based on the FAIRChem UMA model, providing a VASP-like interface for running Machine Learning Interatomic Potential (MLIP) calculations. It supports various calculation types including single point energy, geometry optimization, and molecular dynamics.

### Key Features

- **Interactive Interface**: Provides both TUI (Terminal User Interface) and CLI (Command Line Interface) operation modes
- **Multiple Calculation Types**: Single Point (SP), Geometry Optimization (OPT), Molecular Dynamics (MD)
- **Intelligent Pre-relaxation**: Automatic structure pre-relaxation before MD to prevent atom explosion
- **VASP-compatible Output**: Generates standard format files like OUTCAR, CONTCAR, XDATCAR

---

## Directory Structure

```
uma/
├── uma_calc.py                 # Program entry point
├── setup.py                    # Installation configuration
├── uma-s-1.pt                  # UMA Small model (1.1GB)
├── uma-m-1p1.pt                # UMA Medium model (11GB)
│
├── structure_files/            # Example input files
│   ├── 1.cif                   # CIF format crystal structure
│   ├── POSCAR                  # VASP POSCAR format
│   └── CONTCAR                 # Optimized structure
│
├── umakit/                     # Core program package
│   ├── __init__.py
│   ├── calculator.py           # UMA calculator wrapper
│   ├── cli.py                  # Command line interface
│   ├── config.py               # INCAR configuration parser
│   ├── logger.py               # Logging system
│   ├── utils.py                # Utility functions
│   │
│   ├── runners/                # Calculation runners
│   │   ├── base.py             # Base class
│   │   ├── singlepoint.py      # Single point energy
│   │   ├── optimization.py     # Geometry optimization
│   │   ├── md.py               # Molecular dynamics
│   │   └── batch.py            # Batch processing
│   │
│   ├── tui/                    # TUI interface
│   │   ├── app.py              # TUI application main class
│   │   ├── main_screen.py      # Main menu
│   │   ├── config_screen.py    # Configuration interface
│   │   └── run_screen.py       # Run interface
│   │
│   └── writers/                # Output file writers
│       ├── outcar.py           # OUTCAR format
│       ├── contcar.py          # CONTCAR format
│       ├── xdatcar.py          # XDATCAR format (MD trajectory)
│       ├── oszicar.py          # OSZICAR format (optimization progress)
│       ├── json_writer.py      # JSON format results
│       └── trajectory.py       # ASE trajectory
│
├── docs/                       # Documentation
│   ├── README_CN.md            # Chinese documentation
│   ├── README_EN.md            # English documentation (this file)
│   ├── EXAMPLES.md             # Examples
│   └── USER_GUIDE.md           # User guide
│
└── templates/                  # INCAR templates
    ├── INCAR.sp                # Single point template
    ├── INCAR.opt               # Geometry optimization template
    └── INCAR.md                # Molecular dynamics template
```

---

## Working Principles

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface Layer                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  CLI Command │  │   TUI UI    │  │  INCAR Config File  │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Calculation Control Layer                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │  SinglePoint │ │ Optimization │ │  Molecular Dynamics  │ │
│  │    Runner    │ │    Runner    │ │       Runner         │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        Model Inference Layer                  │
│              ┌───────────────────────────┐                  │
│              │   FAIRChem UMA Model      │                  │
│              │  (uma-s-1.pt / uma-m-1p1.pt)               │
│              └───────────────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        Output Processing Layer                │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐  │
│  │ OUTCAR │ │CONTCAR │ │XDATCAR │ │  JSON  │ │trajectory│  │
│  └────────┘ └────────┘ └────────┘ └────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Calculation Workflow

1. **Structure Input**: Read atomic structures in CIF, POSCAR, XYZ, etc. formats
2. **Model Loading**: Load pre-trained UMA model (SO(3) equivariant neural network)
3. **Graph Construction**: Build atomic neighbor graphs with periodic boundary conditions
4. **Forward Calculation**: Model inference to obtain energy, forces, stress
5. **Post-processing**: Optimization or MD integration based on calculation type
6. **Result Output**: Generate output files in various formats

### MD Pre-relaxation Mechanism

Traditional MD simulations often suffer from atom explosion due to internal stress in the initial structure. This program automatically performs FIRE optimization before MD:

```python
# Pre-relaxation phase
optimizer = FIRE(atoms, logfile=None)
optimizer.run(fmax=0.1, steps=50)  # Quickly eliminate stress

# Then start MD
dyn = Langevin(atoms, ...)
dyn.run(steps)
```

---

## Installation

### System Requirements

- Python >= 3.10
- CUDA >= 11.8 (for GPU support)
- RAM >= 16GB (recommended 32GB)

### Installation Steps

```bash
# 1. Clone or download code
cd /path/to/uma

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install torch>=2.0.0
pip install ase>=3.26.0
pip install fairchem-core
pip install textual  # Required for TUI interface

# 4. Or install using uv
uv pip install -e .
```

### Model Download

```bash
# UMA Small model (recommended, 1.1GB)
# Download: https://fair-chem.github.io/models/uma/

# UMA Medium model (11GB, higher accuracy)
```

---

## Usage Guide

### Method 1: TUI Interactive Interface

```bash
# Launch TUI interface
python uma_calc.py
```

**Operation Guide:**

| Key | Function |
|------|------|
| `↑/↓` | Select menu items |
| `Enter` | Confirm selection |
| `Tab` | Switch to next input field |
| `Esc` | Return to previous level |
| `Q` | Exit program |
| `↑/↓/PgUp/PgDn` | Scroll page |

**Workflow:**

1. **Select Calculation Type**: SP / OPT / MD / Batch / Template
2. **Configure Parameters**:
   - Structure File: Input structure file path (e.g., `1.cif`)
   - Model File: Input model path (e.g., `uma-s-1.pt`)
   - Output Directory: Output directory (default `./results`)
   - Task Type: Select task type (omat/oc20/omol, etc.)
   - Device: CPU or CUDA
3. **Calculation Options**: Set specific parameters based on calculation type
4. **Click Run**: Start calculation

### Method 2: CLI Command Line

#### Single Point Energy (SP)

```bash
# Basic usage
python uma_calc.py sp structure.cif --model uma-s-1.pt --task omat

# Specify device and output directory
python uma_calc.py sp POSCAR \
    --model uma-s-1.pt \
    --task omat \
    --device cuda \
    --output ./results
```

#### Geometry Optimization (OPT)

```bash
# Basic optimization
python uma_calc.py opt structure.cif --model uma-s-1.pt

# Tight convergence with cell optimization
python uma_calc.py opt POSCAR \
    --model uma-s-1.pt \
    --fmax 0.02 \
    --max-steps 1000 \
    --cell-opt \
    --optimizer FIRE
```

**Parameter Description:**
- `--fmax`: Force convergence threshold (eV/Å), default 0.05
- `--max-steps`: Maximum optimization steps, default 500
- `--optimizer`: Optimization algorithm (FIRE/BFGS/LBFGS)
- `--cell-opt`: Enable cell optimization
- `--fix-symmetry`: Preserve symmetry

#### Molecular Dynamics (MD)

```bash
# NVT ensemble @ 300K
python uma_calc.py md structure.cif \
    --model uma-s-1.pt \
    --ensemble NVT \
    --temp 300 \
    --steps 10000 \
    --timestep 1.0

# NVE ensemble
python uma_calc.py md POSCAR \
    --model uma-s-1.pt \
    --ensemble NVE \
    --temp 300 \
    --steps 5000
```

**Parameter Description:**
- `--ensemble`: Ensemble type (NVT/NVE)
- `--temp`: Temperature (K), default 300
- `--timestep`: Time step (fs), default 1.0
- `--steps`: Simulation steps, default 1000
- `--save-interval`: Save interval, default 10

**Note:** MD automatically performs pre-relaxation to eliminate stress.

#### Batch Processing

```bash
# Batch single point calculations
python uma_calc.py batch structures/ \
    --model uma-s-1.pt \
    --calc-type sp \
    --pattern "*.cif" \
    --output batch_results
```

#### Generate Templates

```bash
# Generate INCAR templates
python uma_calc.py template sp -o INCAR.sp
python uma_calc.py template opt -o INCAR.opt
python uma_calc.py template md -o INCAR.md
```

#### Run from INCAR File

```bash
# Run from INCAR file
python uma_calc.py run -i INCAR.uma -s structure.cif -o results/
```

**INCAR File Example:**

```bash
# INCAR.uma - Geometry optimization configuration
CALC_TYPE = OPT
TASK = omat
MODEL_PATH = uma-s-1.pt
DEVICE = cuda

OPT_ALGO = FIRE
FMAX = 0.05
MAX_STEPS = 500
CELL_OPT = .TRUE.
```

---

## Output Files

### Standard Output

| File | Description |
|------|-------------|
| `OUTCAR` | VASP format detailed output, containing energy, forces, stress |
| `CONTCAR` | Final/optimized structure |
| `uma_results.json` | JSON format results for program reading |
| `calculation.log` | Calculation log |

### MD-specific Output

| File | Description |
|------|-------------|
| `XDATCAR` | MD trajectory (VASP format) |
| `trajectory.traj` | ASE trajectory file |

### Optimization-specific Output

| File | Description |
|------|-------------|
| `OSZICAR` | Optimization progress log |
| `optimization.log` | ASE optimizer log |

---

## Task Type Description

| Task | Applicable Systems | Charge/Spin | Stress | Usage |
|------|-------------------|-------------|--------|-------|
| `omat` | Inorganic materials | Optional | ✓ | Bulk materials, battery materials |
| `omol` | Molecules | **Required** | ✗ | Organic molecules, chemical reactions |
| `oc20` | Catalytic surfaces | Optional | ✓ | Surface adsorption, catalysis |
| `oc25` | Catalysis (extended) | Optional | ✓ | Extended catalysis datasets |
| `odac` | MOFs | Optional | ✓ | Metal-organic frameworks |
| `omc` | Molecular crystals | Optional | ✓ | Organic crystals |

**Notes for Molecular Calculations:**

For `omol` tasks, charge and spin must be specified in the structure file:

```python
from ase.io import read, write

atoms = read("molecule.xyz")
atoms.info["charge"] = 0   # Total charge
atoms.info["spin"] = 1     # Spin multiplicity (2S+1)
write("molecule_with_charge.xyz", atoms)
```

---

## Troubleshooting

### Common Issues

#### 1. Atom Explosion in MD

**Symptom:** MD fails after a few steps with error "No edges found"

**Solution:**
- Pre-relaxation is built-in, usually no action needed
- If problem persists, run OPT first to optimize structure
- Lower initial temperature: `--temp 100`

```bash
# Optimize first
python uma_calc.py opt structure.cif --model uma-s-1.pt --max-steps 100
# Then run MD with optimized structure
python uma_calc.py md CONTCAR --model uma-s-1.pt --temp 100
```

#### 2. CUDA Out of Memory

**Symptom:** `RuntimeError: CUDA out of memory`

**Solution:**
- Use CPU calculation: `--device cpu`
- Use smaller model: `uma-s-1.pt` instead of `uma-m-1p1.pt`
- Reduce batch size (handled automatically in current version)

#### 3. TUI Input Not Working

**Symptom:** Input field cannot receive focus

**Solution:**
- Use `Tab` key to switch focus
- Ensure terminal window is large enough (recommended at least 80x24)
- Use arrow keys or PgUp/PgDn to scroll

#### 4. Structure File Read Failure

**Symptom:** `Error reading structure`

**Solution:**
- Check file format (CIF, POSCAR, XYZ, etc.)
- Check file encoding (should be UTF-8)
- Test reading with ASE directly:

```python
from ase.io import read
try:
    atoms = read("structure.cif")
    print(f"Success: {atoms}")
except Exception as e:
    print(f"Error: {e}")
```

---

## Performance Optimization Suggestions

### GPU Acceleration

```bash
# Use CUDA device
python uma_calc.py sp structure.cif --model uma-s-1.pt --device cuda

# For MD, automatically uses turbo mode
python uma_calc.py md structure.cif --model uma-s-1.pt --device cuda
```

### Batch Calculations

```bash
# Use batch mode to process multiple structures
python uma_calc.py batch structures/ \
    --model uma-s-1.pt \
    --calc-type sp \
    --pattern "*.cif"
```

---

## Contact Us

For questions or suggestions, please contact us through:

- GitHub Issues: [fairchem](https://github.com/FAIR-Chem/fairchem)
- Documentation: [fair-chem.github.io](https://fair-chem.github.io)

---

## License

This project is open source under the MIT License.

Copyright (c) Meta Platforms, Inc. and affiliates.
