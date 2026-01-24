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
*   **Description**: Performs energy minimization on a protein structure using OpenMM (Amber14 forcefield).
*   **Inputs**: `pdb_path`, `output_path`.
*   **Outputs**: Status message and saved PDB file.

## Design Skills (`design_skills`)
*(Planned)*
*   `generate_backbone(prompt)`: Uses RFdiffusion.
*   `design_sequence(pdb_path)`: Uses ProteinMPNN.
