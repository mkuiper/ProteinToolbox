# BORG: Biologic Optimization & Recursive Growth Log

## Iteration 0: Initialization
- **Date**: 2026-01-24
- **Status**: Baseline established.
- **Features**:
    - Skills: BioPython, OpenMM, Vina, ProtPy, RFdiffusion (wrapper), ProteinMPNN (wrapper).
    - GUI: Streamlit with Mol* and Project Management.
    - Agents: CrewAI with specialized roles (Librarian, Architect, etc.).
    - Config: Multi-LLM support.

## Iteration 1: Documentation & Reporting
- **New Skill**: `docs_skills.py`.
- **Feature**: `generate_project_report` function to create Markdown summaries of project data.
- **GUI**: Integrated "Generate Project Report" button in Workspace.

## Iteration 2: Structural Descriptors (SASA)
- **New Skill**: `structure_skills.py`.
- **Integration**: Added `freesasa` wrapper for Solvent Accessible Surface Area calculation.
- **GUI**: Added "Structure Analysis" tab (initial).

## Iteration 3: Structural Validation
- **New Skill**: `validation_skills.py`.
- **Feature**: Steric clash detection and backbone continuity (peptide bond) checks using Bio.PDB.
- **GUI**: Enhanced "Analysis & Validation" tab with specific issue reporting (expanders).

## Iteration 4: UX & Tutorialization
- **GUI**: Added "Tutorial Mode" toggle in sidebar.
- **Feature**: Contextual help boxes (st.info) explaining scientific concepts and tool usage.

## Iteration 5: Design Constraints & Heuristics
- **New Skill**: `logic_skills.py`.
- **Feature**: Automated checking of MW, pI, stability, and solubility preferences.
- **Agent Integration**: Updated Technician to use heuristic checks.

## Iteration 6: Mutagenesis & Sequence Analysis (Awesome Protein Design)
- **Skill Enhancement**: Refactored `analysis_skills.py` for BioPython-native property calculation.
- **New Design Skill**: Added `generate_alanine_scan` and `generate_saturation_library` to `design_skills.py`.
- **GUI Update**: Added "Mutagenesis & Analysis" tab with **Variant Scanner**.
- **Testing**: Added `tests/test_design_analysis.py`.

## Bugfix (Post-Iteration 6): Dependency Management
- **Issue**: Missing `freesasa` module caused GUI crash.
- **Fix**: Installed `freesasa` in `.venv` and updated `pyproject.toml`.
- **Status**: GUI verified healthy.

## Iteration 7: Advanced LLM Configuration & Model Expansion
- **Date**: 2026-01-25
- **Feature**: Expanded LLM support to include latest models from OpenAI (o1, o3-mini), Anthropic (Claude 3.5), Gemini (2.0 Flash), and Ollama (Llama 3.3, DeepSeek R1).
- **GUI**: Added dynamic model selection UI with "Other..." option for custom models.
- **Code**: Refactored `crew.py` to clean up duplication and improve `LLM` initialization logic for multi-provider support.
- **Status**: GUI verified healthy.