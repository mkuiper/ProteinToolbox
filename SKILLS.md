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

## ESMFold Skill (`esm_fold_skill`)

### `predict_structure_esmfold(sequence) -> str`
*   **Description**: Predicts protein 3D structure via the ESMFold REST API (ESM Atlas / Meta). No local GPU required.
*   **Inputs**: `sequence` — single-letter AA string (case-insensitive, max ~400 aa recommended).
*   **Outputs**: PDB-format string of the predicted structure.

### `get_esmfold_confidence(pdb_string) -> dict`
*   **Description**: Extracts per-residue pLDDT confidence scores from an ESMFold PDB string (encoded in B-factor column).
*   **Inputs**: `pdb_string` — PDB text returned by `predict_structure_esmfold`.
*   **Outputs**: Dict with `per_residue`, `mean_plddt`, `high_confidence_fraction`.

## Structure Prediction Skills (`structure_prediction_skills`)

### `check_tools_available() -> dict`
*   **Description**: Reports which structure prediction tools (Boltz-1, AlphaFold3, local ESMFold, ColabFold) are installed.
*   **Outputs**: Dict mapping tool name → `True` (installed) or install hint string.

### `predict_with_boltz(fasta_path, output_dir) -> dict`
*   **Description**: Wrapper for the Boltz-1 CLI. Runs real prediction when installed; returns informative dry-run dict otherwise.
*   **Inputs**: `fasta_path`, `output_dir`.
*   **Outputs**: Dict with `status` ('success' | 'dry_run' | 'error'), `command`, `message`.

### `predict_with_af3(fasta_path, output_dir) -> dict`
*   **Description**: Wrapper for the AlphaFold3 CLI. Runs real prediction when installed; returns informative dry-run dict otherwise.
*   **Inputs**: `fasta_path`, `output_dir`.
*   **Outputs**: Dict with `status` ('success' | 'dry_run' | 'error'), `command`, `message`.

## AMP Design Skills (`amp_skills`)

### `score_amp_potential(sequence) -> dict`
*   **Description**: Computes a heuristic Antimicrobial Peptide (AMP) potential score (0–100) based on net charge, hydrophobic moment (Eisenberg scale), length, and amphipathicity.
*   **Inputs**: `sequence` — single-letter AA string.
*   **Outputs**: Dict with `score`, `grade`, `net_charge`, `hydrophobic_moment`, `amphipathicity_index`, `length`, `sub_scores`, `explanation`.

### `generate_amp_variants(sequence, n=5) -> list[tuple[str, float]]`
*   **Description**: Generates AMP-optimized sequence variants by substituting charged/hydrophobic residues for improved AMP profile.
*   **Inputs**: `sequence`, `n` (number of top variants to return).
*   **Outputs**: List of `(variant_sequence, amp_score)` tuples sorted by score descending.
