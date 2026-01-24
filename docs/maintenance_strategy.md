# ProteinToolbox Maintenance & Update Strategy

To ensure `ProteinToolbox` remains a reliable and cutting-edge suite for protein design, we adhere to the following maintenance strategy.

## 1. Dependency Management & Installation

### The "Hub and Spoke" Model
*   **Hub (Main Environment)**: Contains the `ProteinToolbox` code, `Streamlit` GUI, `CrewAI` agents, and lightweight libraries (`BioPython`, `OpenMM`, `protpy`, `vina`).
*   **Spokes (Isolated Environments)**: Heavy, complex AI tools with conflicting dependencies (e.g., `RFdiffusion`, `AlphaFold`, `Boltz-2`) should be installed in **separate Conda environments** or **Docker containers**.
    *   *Implementation*: Our "Skills" wrappers (`src/proteintoolbox/skills/`) will use `subprocess` to call these tools.
    *   *Example*: `generate_backbone` skill calls `conda run -n rfdiffusion python run_inference.py ...`.

### Version Pinning
*   Use `pyproject.toml` for abstract dependencies.
*   Generate lockfiles (e.g., `requirements.lock`) to ensure reproducible builds for users.

## 2. Testing Strategy

### Automated Skill Verification
We run a suite of integration tests (`tests/`) that execute every "Skill" in a dry-run or lightweight mode.
*   **Frequency**: Weekly (via CI/CD) and before every release.
*   **Scope**:
    *   Verify `import` statements work (catches breaking API changes in deps).
    *   Run small jobs (e.g., minimize a 5-residue peptide) to verify binary execution (OpenMM, Vina).
    *   Check for CLI tool presence (`which vina`, check env vars).

### GUI Testing
*   Use `playwright` or `selenium` to load the Streamlit app and verifying the main page loads (HTTP 200).

## 3. Update & Scouting Protocol

### Tool Registry Updates
The `data/tool_registry.json` is the source of truth.
*   **Routine Check (Monthly)**:
    1.  Check GitHub releases for key tools (RFdiffusion, Boltz).
    2.  Check PyPI for updates to core libraries (`openmm`, `biopython`).
    3.  Review "Awesome Protein Design" lists for new emerging tools.

### Adding New Tools
1.  **Evaluate**: Is it open source? Does it have a Python API or CLI?
2.  **Categorize**: Design, Analysis, Docking, etc.
3.  **Wrap**: Create a python function in `src/proteintoolbox/skills/` that handles inputs/outputs.
4.  **Register**: Add to `tool_registry.json`.
5.  **Document**: Add to `SKILLS.md`.

## 4. User-Defined Projects
Users should work within "Projects" to keep data organized. The `ProjectManager` class ensures that metadata (creation date, description) travels with the data, facilitating reproducibility.
