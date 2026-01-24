# ProteinToolbox Skills

This document defines the "Skills" available to the AI agents. Each skill is a specialized function or workflow wrapper.

## Biological Data Skills (`bio_skills`)

### `fetch_pdb_structure(pdb_id, output_dir)`
*   **Description**: Downloads a protein structure from the RCSB PDB.
*   **Inputs**: `pdb_id` (4-letter code), `output_dir`.
*   **Outputs**: Path to the downloaded PDB file.

### `get_sequence_from_pdb(pdb_path)`
*   **Description**: Extracts the amino acid sequence from a PDB file.
*   **Inputs**: `pdb_path`.
*   **Outputs**: String of amino acid sequence.

## Simulation Skills (`sim_skills`)

### `run_minimization(pdb_path, output_path)`
*   **Description**: Performs energy minimization on a protein structure using OpenMM (Amber14 forcefield). Adds missing hydrogens automatically.
*   **Inputs**: `pdb_path`, `output_path`.
*   **Outputs**: Status message and saved PDB file.

## Design Skills (`design_skills`)

### `generate_backbone(prompt, output_dir)`
*   **Description**: Wrapper for RFdiffusion. Generates a protein backbone based on a prompt (e.g., binder design).
*   **Inputs**: `prompt`, `output_dir`.
*   **Outputs**: Path to generated PDB or dry-run command.
*   **Env**: Requires `RFDIFFUSION_PATH` set.

### `design_sequence(pdb_path, output_dir)`
*   **Description**: Wrapper for ProteinMPNN. Designs sequences for a given backbone.
*   **Inputs**: `pdb_path`, `output_dir`.
*   **Outputs**: Path to FASTA or dry-run command.
*   **Env**: Requires `PROTEINMPNN_PATH` set.

## Docking Skills (`docking_skills`)

### `prepare_ligand(ligand_path, output_path)`
*   **Description**: Converts a ligand (SDF/MOL2) to PDBQT format for docking using Meeko.
*   **Inputs**: `ligand_path`.
*   **Outputs**: Path to PDBQT file.

### `run_docking(receptor_pdbqt, ligand_pdbqt, center, size, output_path)`
*   **Description**: Runs AutoDock Vina to dock a ligand into a receptor.
*   **Inputs**: Receptor/Ligand PDBQTs, Box center [x,y,z], Box size [x,y,z].
*   **Outputs**: Path to docked poses (PDBQT).

## Analysis Skills (`analysis_skills`)

### `analyze_sequence(sequence)`
*   **Description**: Calculates physicochemical properties (MW, pI, Gravy, etc.).
*   **Inputs**: `sequence` (str).
*   **Outputs**: Dictionary of properties.
