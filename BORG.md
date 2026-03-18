# BORG: Biologic Optimization & Recursive Growth Log

# CURRENT_ITERATION=16

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

## Iteration 8: 2026 SOTA Model Update
- **Date**: 2026-01-25
- **Research**: Updated model lists to include January 2026 releases: GPT-5.2, Claude 4.5, Gemini 3, and DeepSeek V3.2.
- **Feature**: Added **DeepSeek** as a first-class provider in GUI and Agent logic.
- **GUI**: Modernized model dropdowns across all providers.
- **Status**: Ready for high-reasoning tasks.

## Iteration 7 (Part 2): Agent Logic and Reasoning
- **Date**: January 25, 2026
- **Focus**: Enhanced agent capability for self-correction and workflow validation.
- **Features**:
  - Implemented `LogicTool` in `crew.py` to allow agents to analyze their own plans.
  - Added `validate_workflow_logic` to `logic_skills.py` to detect missing dependencies.
  - Added `propose_refinements` to `logic_skills.py` to suggest best practices.
  - Updated `Architect` and `Critic` agents to utilize these new logic tools.

## Iteration 8 (Testing Focus): Testing, Validation, and Robustness
- **Testing & Validation**: Implemented property-based testing using `hypothesis` to improve system robustness.
- **New Feature**: Added `clean_and_validate_sequence` to `bio_skills.py` for robust sequence input handling.
- **Tests**: Added `tests/test_properties.py` covering sequence validation and logic heuristics with fuzzing strategies.
- **Dependencies**: Added `hypothesis` and `pytest` to project dependencies.

## Iteration 9: Workflow recipes and examples
- **Focus**: Predefined design paths for common tasks.
- **New Module**: `src/proteintoolbox/workflows.py` introducing `Workflow` and `AntibodyDesignWorkflow` / `EnzymeRefinementWorkflow` classes.
- **Features**: 
    - Standardized "Recipes" that chain skills (Validation -> Analysis -> Minimization).
    - Robust handling of missing dependencies (e.g., OpenMM) with graceful degradation (skipping steps).
- **Tests**: Added `tests/test_workflows.py`.

## Iteration 10
**Focus**: GUI Experience and Visualization (e.g. Plotly charts, Mol* enhancements)

**Changes**:
- Added `plotly` dependency for interactive charting.
- Integrated Plotly charts into the Streamlit GUI:
    - **Structure Analysis**: Added interactive bar chart for Residue SASA.
    - **Mutagenesis**: Added scatter plot for variant landscape analysis (ΔpI vs ΔInstability).
- Enhanced user experience by providing rich tooltips and interactive zooming for data exploration.

**Verification**:
- Verified GUI functionality via `curl`.
- Confirmed Plotly installation.

## Iteration 11
- **Focus**: New Skills and Integrations (SOTA protein design models)
- **Research**: Identified ESM (Evolutionary Scale Modeling) by Meta as a high-impact, installable SOTA capability for protein representation learning.
- **Implementation**:
    - Added `transformers`, `torch`, and `accelerate` to dependencies.
    - Implemented `ESMSkills` in `src/proteintoolbox/skills/esm_skills.py` using the lightweight `esm2_t6_8M_UR50D` model.
    - Added `get_embedding` capability to generate numerical representations of protein sequences.
    - Added unit test `tests/test_esm_skills.py`.
- **Status**: Integrated and Verified.

## Iteration 12: Agent Logic and Reasoning
- **Date**: January 25, 2026
- **Focus**: Specialized roles and Chain-of-Thought protocols.
- **New Agent**: `Methodologist` added to `crew.py`. Specializes in decomposing requests into rigorous scientific questions before execution.
- **New Tools**:
    - `DecompositionTool`: Uses heuristics to break down requests into steps and constraints.
    - `ReasoningTool`: Provides structured CoT templates (e.g., "Scientific Method", "Root Cause Analysis") to guide agents.
- **Skill Updates**:
    - `logic_skills.py`: Added `decompose_request` and `get_reasoning_template`.
- **Testing**: Added unit tests for new logic skills in `tests/test_logic_skills.py`.
- **Status**: Implemented and verified via unit tests.

## Iteration 7 (Graph Reasoning)
- **Date**: January 25, 2026
- **Focus**: Agent Logic and Reasoning (Graph-based Pathfinding)
- **Changes**:
    - **New Skill Module**: `graph_reasoning.py` implementing `DomainKnowledgeGraph` to model scientific dependencies (Ontology: Sequence -> Structure -> Docking).
    - **New Tool**: `PathfinderTool` added to `crew.py`, allowing agents to query the knowledge graph for valid scientific workflows.
    - **Agent Upgrades**: `Methodologist`, `Architect`, and `Critic` now use `PathfinderTool` to ground their plans in a defined scientific ontology.
    - **Registry**: Registered `graph_reasoning` in `skills/__init__.py`.

## Iteration 13 (Placeholder)
- Iteration numbering gap maintained for historical continuity.

## Iteration 14 (Placeholder)
- Iteration numbering gap maintained for historical continuity.

## Iteration 15: GUI Experience and Visualization
- **Date**: 2026-03-18
- **Focus**: Interactive Plotly visualizations, Mol* enhancements, and UX improvements.

### New Skill Additions (`analysis_skills.py`)
- `get_codon_usage(dna_sequence)`: Counts all 64 codon frequencies in a CDS/DNA sequence.
- `get_codon_usage_heatmap_data(dna_sequence)`: Returns 2D grid data (rows = first 2 bases, cols = 3rd base) for Plotly heatmap rendering. Includes amino acid labels per cell.
- Exposed `CODON_TABLE` constant for downstream use.

### GUI Enhancements (`app.py`)
- **New Mode: "Sequence Analysis"** — dedicated 4-tab section:
  1. **Physicochemical** tab: Computes MW, pI, GRAVY, instability, aromaticity, 2° structure fraction; renders interactive amino acid composition bar chart with export buttons.
  2. **Codon Usage Heatmap** tab: Renders a full 16×4 interactive Plotly heatmap of codon frequencies; includes sortable summary table and CSV download.
  3. **Sequence Comparison** tab: Side-by-side comparison of two sequences — grouped bar chart of physicochemical deltas, per-residue diff table for equal-length sequences.
  4. **ESM Embedding PCA** tab: Embeds N sequences via ESM2, performs PCA via pure NumPy (avoids scipy/sklearn ABI issues), and renders an interactive 2D scatter plot with variance-explained axis labels.
- **Export buttons**: All Plotly charts now have "Download SVG" and "Download PNG" buttons (via kaleido).
- **Mol* color-by-feature UI**: Added "Color By" selector (Chain / Secondary Structure / Hydrophobicity / Residue Type) in Workspace to inform viewer use.
- **Workflow progress indicator**: Agent Workflow mode now shows animated step-by-step progress through the 5 agent stages.
- **Tool tabs now fully implemented**: Biological Data (PDB fetch + sequence extract), Simulation (energy minimization), Analysis & Validation (SASA bar chart + validation report), Mutagenesis & Analysis (variant landscape scatter).
- **Sidebar polish**: Grouped sections with icons, expanders for LLM/project settings.

### Dependencies Added
- `scikit-learn` — for future PCA/ML utilities (PCA currently implemented in NumPy to avoid ABI conflicts).
- `kaleido` — Plotly SVG/PNG image export.
- Both added to `pyproject.toml`.

### Status
- GUI verified via syntax check.
- Existing tests pass.

## Iteration 16: New Skills and Integrations
- **Date**: 2026-03-18
- **Focus**: SOTA protein design capabilities — ESMFold, Boltz-1/AF3, AMP design.

### New Skill: ESMFold REST API Wrapper (`esm_fold_skill.py`)
- `predict_structure_esmfold(sequence)`: Calls the ESM Atlas public REST API for fast single-sequence structure prediction. Returns PDB string. No local GPU required.
- `get_esmfold_confidence(pdb_string)`: Parses per-residue pLDDT confidence from the B-factor column; returns mean pLDDT and high-confidence fraction.
- Robust error handling for API timeouts, invalid sequences, and non-PDB responses.

### New Skill: Structure Prediction Wrappers (`structure_prediction_skills.py`)
- `check_tools_available()`: Detects installed predictors — Boltz-1, AlphaFold3, local ESMFold (fair-esm), ColabFold — and returns install hints for missing tools.
- `predict_with_boltz(fasta_path, output_dir)`: Runs Boltz-1 CLI when installed; returns a dry-run dict with the exact command and install instructions otherwise.
- `predict_with_af3(fasta_path, output_dir)`: Runs AlphaFold3 CLI when installed; dry-run stub otherwise.
- Both functions return a consistent `{status, command, output_dir, message}` dict.

### New Skill: AMP Design (`amp_skills.py`)
- `score_amp_potential(sequence)`: Heuristic AMP score (0–100) based on net charge at pH 7, hydrophobic moment (Eisenberg scale), length optimality, and amphipathicity index. Returns score, grade, sub-scores, and plain-English notes.
- `generate_amp_variants(sequence, n=5)`: Generates AMP-optimized single-residue substitution variants by targeting low charge, low amphipathicity, and local sequence diversity. Returns top-N by AMP score.
- Pure-Python / NumPy — no external ML dependencies.

### GUI Enhancements (`app.py`)
- **New mode: "Structure Prediction"**: Three-tab panel (ESMFold API, Boltz-1, AlphaFold3) with live tool availability status. ESMFold tab renders pLDDT bar chart with PDB download. Boltz/AF3 tabs show dry-run commands with install instructions when not installed.
- **New tab in "Sequence Analysis": "AMP Design"**: Side-by-side score + variant panels. Scores displayed as metrics + sub-score bar chart; variants shown in ranked bar chart with CSV download.

### Registry Updates
- `esm_fold_skill`, `structure_prediction_skills`, `amp_skills` added to `skills/__init__.py` and `SKILL_REGISTRY`.

### Tests
- `tests/test_amp_skills.py` — 14 tests covering scoring, grading, variant generation, error handling.
- `tests/test_esm_fold_skill.py` — 8 tests covering confidence parsing and input validation (no live API calls).
- `tests/test_structure_prediction_skills.py` — 7 tests covering tool detection and dry-run behaviour.

### Status
- All 61 tests pass.
