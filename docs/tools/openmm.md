# OpenMM

**Category**: Simulation
**Website**: [openmm.org](https://openmm.org/)

## Description
OpenMM is a high-performance toolkit for molecular simulation. It allows us to perform energy minimization, equilibration, and production MD runs.

## Usage in ProteinToolbox
We use OpenMM primarily as a "Skill" (`sim_skills.py`) for:
1.  **Preparation**: Cleaning PDBs, adding hydrogens.
2.  **Minimization**: Relaxing structures after design (e.g., from RFdiffusion) to fix steric clashes.
3.  **Dynamics**: Short MD simulations to test stability.

## Standard Commands
```python
from proteintoolbox.skills import sim_skills
sim_skills.run_minimization("input.pdb", "output.pdb")
```

## Requirements
*   CUDA-enabled GPU (recommended for performance).
*   `openmm` python package.
*   Forcefield XML files (included with OpenMM).
