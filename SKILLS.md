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
