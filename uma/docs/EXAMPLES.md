# UMA Calculator Examples

This document provides practical examples for using UMA Calculator.

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Materials Calculations](#materials-calculations)
3. [Molecular Calculations](#molecular-calculations)
4. [Molecular Dynamics](#molecular-dynamics)
5. [Batch Processing](#batch-processing)
6. [Advanced Workflows](#advanced-workflows)

## Basic Examples

### Example 1: Simple Single Point Calculation

Calculate energy and forces for a crystal structure:

```bash
# Using command line
uma_calc sp Li2O.cif --model uma-s-1.pt --task omat --device cpu

# Output files created:
# - OUTCAR: Detailed results
# - CONTCAR: Structure file
# - uma_results.json: JSON results
```

### Example 2: Using INCAR File

Create `INCAR.uma`:
```
CALC_TYPE = SP
TASK = omat
MODEL_PATH = /home/user/models/uma-s-1.pt
DEVICE = cpu
WRITE_FORCES = .TRUE.
WRITE_STRESS = .TRUE.
```

Run calculation:
```bash
uma_calc run -i INCAR.uma -s Li2O.cif
```

### Example 3: Generate Template

Generate a template INCAR for geometry optimization:

```bash
uma_calc template opt -o INCAR.opt
```

## Materials Calculations

### Example 4: Geometry Optimization of a Bulk Material

Optimize atomic positions of a bulk material:

```bash
uma_calc opt POSCAR --model uma-s-1.pt --task omat \
    --fmax 0.05 --max-steps 500 --optimizer FIRE
```

### Example 5: Cell Optimization (Constant Pressure)

Optimize both atomic positions and cell parameters:

```bash
uma_calc opt structure.cif --model uma-s-1.pt --task omat \
    --cell-opt --fmax 0.02 --max-steps 1000
```

**Note**: Cell optimization requires a task that supports stress (omat, oc20, etc.).

### Example 6: Catalysis Surface Calculation

Calculate a surface adsorption system:

```bash
uma_calc sp Pt_surface_with_adsorbate.cif --model uma-s-1.pt --task oc20
```

## Molecular Calculations

### Example 7: Single Point for a Molecule

For molecules, you need to specify charge and spin:

```python
# prepare_molecule.py
from ase.io import read, write

# Read molecule
atoms = read("water.xyz")

# Set charge and spin for neutral singlet
atoms.info["charge"] = 0
atoms.info["spin"] = 1  # Singlet = 2*0 + 1

# Save with info
write("water_prepared.xyz", atoms)
```

```bash
uma_calc sp water_prepared.xyz --model uma-s-1.pt --task omol
```

### Example 8: Molecular Geometry Optimization

Optimize a drug-like molecule:

```bash
uma_calc opt molecule.xyz --model uma-s-1.pt --task omol \
    --fmax 0.01 --optimizer LBFGS
```

## Molecular Dynamics

### Example 9: NVT Equilibration

Run NVT simulation at 300K:

```bash
uma_calc md structure.cif --model uma-s-1.pt --task omat \
    --ensemble NVT --temp 300 --timestep 1.0 --steps 10000 \
    --device cuda --save-interval 10
```

Output files:
- `XDATCAR`: Trajectory in VASP format
- `trajectory.traj`: ASE trajectory
- `OUTCAR`: Summary with final temperature

### Example 10: NVE Production Run

After NVT equilibration, run NVE:

```bash
# First, equilibrate with NVT
uma_calc md structure.cif --model uma-s-1.pt \
    --ensemble NVT --temp 300 --steps 5000 \
    --device cuda

# Use CONTCAR from NVT as starting point for NVE
uma_calc md CONTCAR --model uma-s-1.pt \
    --ensemble NVE --temp 300 --steps 50000 \
    --device cuda --save-interval 50
```

### Example 11: High-Temperature MD

Study diffusion at elevated temperature:

```bash
uma_calc md Li_conductor.cif --model uma-s-1.pt --task omat \
    --ensemble NVT --temp 1000 --timestep 1.0 --steps 50000 \
    --device cuda --friction 0.002
```

## Batch Processing

### Example 12: Screen Multiple Structures

Process a directory of CIF files:

```bash
# Directory structure:
# structures/
#   ├── structure_1.cif
#   ├── structure_2.cif
#   └── structure_3.cif

uma_calc batch structures/ --model uma-s-1.pt \
    --calc-type sp --output batch_results/

# Results:
# batch_results/
#   ├── structure_1/
#   │   ├── OUTCAR
#   │   └── uma_results.json
#   ├── structure_2/
#   └── structure_3/
#   └── batch_summary.json
```

### Example 13: Batch Optimization

Optimize multiple candidate structures:

```bash
uma_calc batch candidates/ --model uma-s-1.pt \
    --calc-type opt --pattern "*.cif" --output optimized/
```

### Example 14: Analyze Batch Results

```python
# analyze_results.py
import json

with open("batch_results/batch_summary.json") as f:
    data = json.load(f)

# Find lowest energy structure
results = data["results"]
energies = [(r["filename"], r["energy"]) for r in results if r["success"]]
lowest = min(energies, key=lambda x: x[1])

print(f"Lowest energy structure: {lowest[0]}")
print(f"Energy: {lowest[1]:.6f} eV")
```

## Advanced Workflows

### Example 15: Equation of State (EOS)

Calculate energy vs volume curve:

```python
# eos_workflow.py
from ase.io import read, write
import numpy as np
import subprocess

# Read initial structure
atoms = read("Li2O.cif")

# Create volume scaling factors
scales = np.linspace(0.9, 1.1, 11)

for i, scale in enumerate(scales):
    # Scale cell
    atoms_scaled = atoms.copy()
    atoms_scaled.set_cell(atoms.cell * scale, scale_atoms=True)

    # Write structure
    write(f"eos_{i:02d}.cif", atoms_scaled)

    # Run calculation
    subprocess.run([
        "uma_calc", "sp", f"eos_{i:02d}.cif",
        "--model", "uma-s-1.pt",
        "--task", "omat",
        "--output", f"eos_{i:02d}_results"
    ])

# Collect results and fit EOS
```

### Example 16: NEB Calculation Preparation

Generate intermediate images for NEB:

```python
# neb_setup.py
from ase.io import read, write
from ase.neb import NEB

# Read initial and final states
initial = read("initial.cif")
final = read("final.cif")

# Create NEB images
images = [initial]
images += [initial.copy() for _ in range(3)]
images += [final]

neb = NEB(images)
neb.interpolate()

# Save images
for i, image in enumerate(images):
    write(f"neb_{i:02d}.cif", image)

# Run optimization on each image
import subprocess
for i in range(len(images)):
    subprocess.run([
        "uma_calc", "opt", f"neb_{i:02d}.cif",
        "--model", "uma-s-1.pt",
        "--output", f"neb_{i:02d}_opt"
    ])
```

### Example 17: Phonon Calculation (with phonopy)

```python
# phonon_workflow.py
from ase.io import read, write
import subprocess
import numpy as np

# Read structure
atoms = read("structure.cif")

# Generate displacements (using phonopy)
from phonopy import Phonopy
from phonopy.structure.atoms import PhonopyAtoms

# Convert to phonopy atoms
ph_atoms = PhonopyAtoms(
    symbols=atoms.get_chemical_symbols(),
    positions=atoms.positions,
    cell=atoms.cell,
)

phonopy = Phonopy(ph_atoms, [[2, 0, 0], [0, 2, 0], [0, 0, 2]])
phonopy.generate_displacements(distance=0.03)

# Get supercells with displacements
supercells = phonopy.supercells_with_displacements

# Calculate forces for each displacement
forces = []
for i, supercell in enumerate(supercells):
    # Write supercell
    write(f"disp_{i:03d}.cif", supercell)

    # Run UMA calculation
    subprocess.run([
        "uma_calc", "sp", f"disp_{i:03d}.cif",
        "--model", "uma-s-1.pt",
        "--output", f"disp_{i:03d}_results"
    ])

    # Read forces from results
    import json
    with open(f"disp_{i:03d}_results/uma_results.json") as f:
        result = json.load(f)
    forces.append(result["calculation"]["results"]["forces"])

# Set forces and produce force constants
phonopy.forces = forces
phonopy.produce_force_constants()

# Calculate DOS and band structure
phonopy.run_mesh([20, 20, 20])
phonopy.run_total_dos()
phonopy.run_band_structure(
    [[[0, 0, 0], [0.5, 0, 0]],
     [[0.5, 0, 0], [0.5, 0.5, 0]]]
)
```

### Example 18: Formation Energy Calculation

Calculate formation energy from elemental references:

```python
# formation_energy.py
from ase.io import read
import json

# Read structure
compound = read("Li2O.cif")
formula = compound.get_chemical_formula()

# Run calculation
import subprocess
subprocess.run([
    "uma_calc", "sp", "Li2O.cif",
    "--model", "uma-s-1.pt",
    "--task", "omat",
    "--output", "Li2O_results"
])

# Read results
with open("Li2O_results/uma_results.json") as f:
    result = json.load(f)

e_total = result["calculation"]["results"]["energy"]

# Elemental reference energies (would need to calculate separately)
e_ref = {
    "Li": -1.9,  # eV/atom (example values)
    "O": -4.9,
}

# Count atoms
from collections import Counter
atom_counts = Counter(compound.get_chemical_symbols())

# Calculate formation energy
e_form = e_total
for element, count in atom_counts.items():
    e_form -= count * e_ref[element]

e_form_per_atom = e_form / len(compound)

print(f"Total energy: {e_total:.4f} eV")
print(f"Formation energy: {e_form:.4f} eV")
print(f"Formation energy per atom: {e_form_per_atom:.4f} eV/atom")
```

## Tips and Best Practices

### Performance Optimization

1. **Use GPU for large systems**:
   ```bash
   uma_calc sp large_structure.cif --model uma-s-1.pt --device cuda
   ```

2. **Use turbo mode for MD**:
   Set `INFERENCE_MODE = turbo` in INCAR or use for repeated calculations

3. **Batch processing**:
   Process multiple structures overnight using batch mode

### Troubleshooting Common Issues

**Issue**: "Model file not found"
- Solution: Use absolute path to model file

**Issue**: "CUDA out of memory"
- Solution: Use `--device cpu` or reduce system size

**Issue**: Optimization not converging
- Solution: Check initial structure, try different optimizer, increase max steps

**Issue**: MD simulation blows up
- Solution: Reduce timestep, check initial temperature, energy minimize first

### Recommended Settings

| System Type | Recommended Settings |
|-------------|---------------------|
| Small molecules (1-50 atoms) | `--optimizer LBFGS --fmax 0.01` |
| Bulk materials | `--optimizer FIRE --fmax 0.05` |
| Surfaces | `--optimizer FIRE --fmax 0.03` |
| MD equilibration | `--ensemble NVT --timestep 1.0` |
| MD production | `--ensemble NVE --timestep 1.0` |
| High temperature MD | `--timestep 0.5 --friction 0.002` |
