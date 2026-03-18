# BORG Intelligence Report: 2025–2026 Protein Design Tool Landscape
**Classification**: BORG Strategic Integration Assessment
**Date**: 2026-03-18
**Author**: ProteinToolbox Autonomous Review System
**Status**: Active — feeds Iterations 17–20 roadmap

---

## Preamble

This report assesses the 2025–2026 state-of-the-art in computational protein design for integration priority into ProteinToolbox (currently at Iteration 15). The platform's existing stack — BioPython, OpenMM, AutoDock Vina, RFdiffusion (CLI wrapper), ProteinMPNN (CLI wrapper), ESM2 (embedding), CrewAI agents, Streamlit GUI — sets the baseline against which each new tool is evaluated.

Primary design context: **antifreeze proteins (AFP) and ice-binding peptides**, with secondary interest in binder and enzyme design. Integration decisions weigh scientific fit, installation complexity, inference cost, and agent-loop utility.

---

## 1. ESM3 (EvolutionaryScale, 2024–2025)

**What it does**: ESM3 is a multi-track transformer that reasons jointly over protein sequence, 3D structure, and functional annotations (GO terms, active-site labels). Unlike ESM2 (sequence-only embedding), ESM3 can generate and complete sequences conditioned on partial structure or function tracks, enabling constrained de novo design.

**Why it matters for AFP work**: AFP design requires preserving the flat β-helix scaffold and repetitive Thr/Asx ice-binding motif while varying surface residues. ESM3's structure-conditioned generation could enforce scaffold topology while exploring sequence diversity — a capability ESM2 embedding alone cannot provide.

**Current integration status**: ProteinToolbox has ESM2 (lightweight, `esm2_t6_8M_UR50D`) for embeddings only (Iteration 11). ESM3 is a separate, much larger model family.

| Attribute | Assessment |
|-----------|-----------|
| **Integration Priority** | **HIGH** |
| **Integration approach** | `pip install esm` (EvolutionaryScale SDK) + local inference for small models; API call via `esm.sh` endpoint for 98B variant |
| **Hardware requirement** | Smallest ESM3 (1.4B) fits on 16GB VRAM; larger variants need API |
| **AFP/peptide fit** | Excellent — structure-conditioned generation for ice-binding scaffold variants |
| **Recommended action** | Add `ESM3Skills` module: `generate_sequence_from_structure()`, `score_sequence_structure_compatibility()`. Use small local model for dev; API for production runs. |

---

## 2. Boltz-2 (MIT/Recursion, June 2025)

**What it does**: Boltz-2 extends Boltz-1's AlphaFold3-class structure prediction to simultaneously predict binding affinity (ΔG) between protein complexes, protein–ligand pairs, and protein–nucleic acid interactions — in seconds on consumer hardware. It outputs confidence scores, binding poses, and affinity estimates in a single forward pass.

**Why it matters for AFP work**: AFP function depends on the protein's ability to bind ice crystal surfaces — a protein–ligand-like interaction where the "ligand" is an ordered water lattice. Boltz-2's binding affinity scoring could serve as a fast proxy filter for ice-binding potential before expensive MD simulations.

| Attribute | Assessment |
|-----------|-----------|
| **Integration Priority** | **HIGH** |
| **Integration approach** | `pip install boltz` — pure Python, no structural biology environment required |
| **Hardware requirement** | CPU-capable; GPU preferred for speed; runs on laptop |
| **AFP/peptide fit** | High — affinity prediction as pre-filter before OpenMM minimization; replaces slow docking loop for protein–protein work |
| **Recommended action** | Add `Boltz2Skills`: `predict_structure_and_affinity(sequence_a, sequence_b)`. Wire into existing docking workflow as upstream screen. |

---

## 3. BoltzGen (MIT, November 2025)

**What it does**: BoltzGen couples Boltz-2's affinity model with a diffusion-based generator to perform de novo protein binder design — proposing binder sequences that are predicted to fold against a target and bind with favorable ΔG. It operates as a generate-then-score loop with end-to-end differentiability.

**Why it matters for AFP work**: Could generate novel AFP variants or ice-binding peptides conditioned on an ice-crystal surface representation (provided as a PDB fragment). Complements RFdiffusion for cases where an explicit diffusion trajectory is less important than affinity-guided generation.

| Attribute | Assessment |
|-----------|-----------|
| **Integration Priority** | **HIGH** |
| **Integration approach** | `pip install boltzgen` (depends on `boltz` base); single CLI call or Python API |
| **Hardware requirement** | GPU recommended; 8–16GB VRAM for practical throughput |
| **AFP/peptide fit** | Very high — direct application: generate ice-binding peptide candidates against cryo-EM ice surface PDB |
| **Recommended action** | Add `BoltzGenSkills`: `design_binder(target_pdb, n_candidates)`. Integrate with agent Architect for automated candidate generation pipelines. |

---

## 4. RFdiffusion2 (Baker Lab, April 2025)

**What it does**: RFdiffusion2 extends the original RFdiffusion to enzyme design — given a chemical reaction described by SMILES or a reaction SMARTS string, it designs a protein scaffold that positions catalytic residues to enable that chemistry. It integrates ligand placement directly into the diffusion trajectory.

**Why it matters for AFP work**: AFP work is primarily binding, not catalysis — however, RFdiffusion2's improved ligand-aware diffusion (treating ice-crystal surface fragments as "ligands") may outperform vanilla RFdiffusion for AFP scaffold generation. The reaction-description interface is also useful for any peptide with catalytic aspirations.

| Attribute | Assessment |
|-----------|-----------|
| **Integration Priority** | **MEDIUM** |
| **Integration approach** | CLI wrapper (same pattern as existing `generate_backbone` skill); requires RFdiffusion2 repo clone + weights |
| **Hardware requirement** | GPU required; same footprint as RFdiffusion1 |
| **AFP/peptide fit** | Moderate — useful if modeling ice-binding as a pseudo-enzymatic recognition event; less directly applicable than BoltzGen |
| **Recommended action** | Update existing `design_skills.py` `generate_backbone()` to detect and route between RFdiffusion1 and RFdiffusion2 based on whether a ligand/reaction SMILES is supplied. |

---

## 5. RFdiffusion3 (Baker Lab, December 2025)

**What it does**: RFdiffusion3 is a full generational upgrade: ~10× faster than RFdiffusion2, atom-level precision (all-atom diffusion including sidechains and small molecules), and generalized design across protein–protein, protein–nucleic acid, and protein–small molecule targets. It replaces RFdiffusion1 as the baseline backbone generator.

**Why it matters for AFP work**: The atom-level precision directly benefits AFP design — ice-binding motifs depend on precise Thr/Asx sidechain positioning relative to water lattice periodicity. RFdiffusion3 can diffuse with explicit sidechain atoms, potentially generating bindable geometries that were previously only achievable by post-processing with ProteinMPNN.

| Attribute | Assessment |
|-----------|-----------|
| **Integration Priority** | **HIGH** |
| **Integration approach** | CLI wrapper upgrade (same env variable pattern as existing `RFDIFFUSION_PATH`); weights available via Baker Lab |
| **Hardware requirement** | GPU required; 10× faster means same hardware does 10× the throughput |
| **AFP/peptide fit** | Excellent — atom-level ice-binding motif design; replaces RFdiffusion1 as primary backbone generator |
| **Recommended action** | Upgrade `generate_backbone()` to RFdiffusion3 as the primary backend. Add `RFDIFFUSION3_PATH` env var. Preserve RFdiffusion1 as fallback. Document in BORG. |

---

## 6. RFantibody (Baker Lab, 2025)

**What it does**: RFantibody is a fine-tuned variant of RFdiffusion specialized for antibody CDR loop design — given a target antigen structure, it generates antibody-framework-compatible CDR-H3 loops (and other CDRs) optimized for binding. It dramatically simplifies the antibody design pipeline by collapsing separate backbone + sequence steps.

**Why it matters for AFP work**: AFP work is not antibody work, but the underlying capability — designing short structured loops that bind a target surface — is directly analogous to designing ice-binding loops. RFantibody's training on structured binding loops may generalize to repetitive β-solenoid ice-binding segments.

| Attribute | Assessment |
|-----------|-----------|
| **Integration Priority** | **LOW–MEDIUM** |
| **Integration approach** | CLI wrapper; separate weights download from Baker Lab; builds on RFdiffusion3 infrastructure |
| **Hardware requirement** | GPU required |
| **AFP/peptide fit** | Indirect — conceptually useful for loop design; antibody-specific priors may not transfer well to AFP β-helix topology |
| **Recommended action** | Add as optional skill `design_antibody_loop()` in `design_skills.py`. Useful if Mike's work expands toward ice-binding nanobody or peptide-loop library design. |

---

## 7. Chai-2 (Chai Discovery, June 2025)

**What it does**: Chai-2 achieves ~100-fold improvement over AlphaFold3 in antibody–antigen structure prediction accuracy (Fv-only evaluation benchmarks), and extends to protein–protein complex prediction with physical binding affinity estimates. It uses a new multi-chain diffusion architecture trained on curated antibody–antigen complex data.

**Why it matters for AFP work**: While antibody-focused, Chai-2's protein–protein complex prediction and binding affinity scoring are directly applicable to AFP–target (ice crystal surface mimetic peptide) complex analysis. The reported accuracy improvements also apply to general protein–protein interfaces.

| Attribute | Assessment |
|-----------|-----------|
| **Integration Priority** | **MEDIUM** |
| **Integration approach** | `pip install chai-lab` (Chai Discovery Python SDK); API also available |
| **Hardware requirement** | GPU preferred; CPU inference possible for small complexes |
| **AFP/peptide fit** | Moderate — complex prediction for AFP–target interfaces; affinity scoring as design filter |
| **Recommended action** | Add `ChaiSkills`: `predict_complex(chain_a_seq, chain_b_seq)`. Position as alternative to Boltz-2 for protein–protein cases; use both for consensus scoring. |

---

## 8. AlphaFold3 (Google DeepMind, Public Release 2025)

**What it does**: AlphaFold3 extends AF2's protein-structure accuracy to all biological molecule classes: protein + DNA + RNA + small molecule ligands + post-translational modifications (phosphorylation, glycosylation, etc.) in a single unified diffusion-based model. The public server and weights are now available for academic non-commercial use.

**Why it matters for AFP work**: AFP function involves precise interaction with water molecules organized in an ice lattice — structurally, this is a protein interacting with a periodic small-molecule (water) arrangement. AF3's ligand-handling capability, combined with its accuracy on repeat proteins (AFP are often repetitive β-helices), makes it the most accurate structure predictor for validating AFP designs.

| Attribute | Assessment |
|-----------|-----------|
| **Integration Priority** | **HIGH** |
| **Integration approach** | Web server API (non-commercial use) via `alphafoldserver.google.com`; local inference via `alphafold3` pip package (GPU-intensive); JSON input format |
| **Hardware requirement** | Local: A100/H100 recommended; Web: free for academic use |
| **AFP/peptide fit** | Excellent — best-in-class for structure prediction and PTM handling; validates design outputs from RFdiffusion3/BoltzGen |
| **Recommended action** | Add `AlphaFold3Skills`: `submit_prediction_job(sequence, ligands=None)` using the public API. Use as validation step after backbone generation — wire into `AntifreezeDesignWorkflow`. |

---

## 9. Boltz-1 (MIT, 2024–2025)

**What it does**: Boltz-1 is an open-source, fully reproducible implementation matching AlphaFold3's structure prediction performance — including protein, DNA, RNA, and ligand co-folding. Unlike AF3, Boltz-1 has no non-commercial restriction and runs on modest hardware. It is the open-source foundation that BoltzGen and Boltz-2 build upon.

**Why it matters for AFP work**: As the open-source AF3 equivalent, Boltz-1 is the right tool for high-throughput validation of AFP design candidates without API rate limits or commercial restrictions. Its support for glycan and PTM co-folding is relevant if exploring glycosylated AFP variants.

| Attribute | Assessment |
|-----------|-----------|
| **Integration Priority** | **HIGH** |
| **Integration approach** | `pip install boltz`; single CLI call `boltz predict input.yaml`; runs on 8GB VRAM |
| **Hardware requirement** | 8–16GB VRAM for practical use; CPU fallback available (slow) |
| **AFP/peptide fit** | Excellent — open-source AF3-equivalent; no rate limits; use for batch AFP validation |
| **Recommended action** | Add `Boltz1Skills`: `predict_structure(sequence)`, `predict_complex(sequences)`. This becomes the **primary structure prediction** skill, replacing PDB-fetch-only approach. |

---

## Integration Priority Matrix

| Tool | Priority | Effort | AFP Fit | Iteration Target |
|------|----------|--------|---------|-----------------|
| **RFdiffusion3** | HIGH | Low (CLI upgrade) | Excellent | 17 |
| **Boltz-1** | HIGH | Low (pip install) | Excellent | 17 |
| **ESM3** | HIGH | Medium (new SDK) | Excellent | 17–18 |
| **Boltz-2** | HIGH | Low (pip install) | High | 18 |
| **BoltzGen** | HIGH | Medium (depends on Boltz-2) | Very High | 18 |
| **AlphaFold3** | HIGH | Medium (API integration) | Excellent | 18 |
| **Chai-2** | MEDIUM | Low (pip install) | Moderate | 19 |
| **RFdiffusion2** | MEDIUM | Low (CLI upgrade) | Moderate | 19 |
| **RFantibody** | LOW–MEDIUM | Low (CLI wrapper) | Indirect | 20 |

---

## Prioritized Integration Roadmap: Iterations 17–20

### Iteration 17: Open-Source Structure Prediction Foundation
**Theme**: Replace absent structure prediction with SOTA open tools.

1. **Boltz-1 integration** — add `Boltz1Skills` with `predict_structure()` and `predict_complex()`. Wire into GUI "Simulation" tab alongside OpenMM. This gives the platform AF3-quality prediction without API dependency or rate limits.
2. **RFdiffusion3 upgrade** — update `generate_backbone()` to route to RFdiffusion3. Add `RFDIFFUSION3_PATH` env var. Keep RFdiffusion1 as fallback. Document weight download instructions.
3. **ESM3 small model** — add `ESM3Skills` with `generate_sequence_from_structure()` using the 1.4B local model. Expose in GUI "Design" tab as "AI-conditioned sequence generation."

**BORG Log entry target**: Iteration 17 — Structure Prediction and Generation Upgrade.

---

### Iteration 18: Affinity-Guided Design Loop
**Theme**: Close the design loop with binding affinity scoring.

1. **Boltz-2 integration** — add `Boltz2Skills` with `predict_affinity(seq_a, seq_b)`. Wire as a pre-filter before OpenMM minimization in the AFP design workflow.
2. **BoltzGen integration** — add `BoltzGenSkills` with `design_binder(target_pdb, n=10)`. Wire into CrewAI `Architect` agent as a callable design action.
3. **AlphaFold3 API** — add `AlphaFold3Skills` with `submit_af3_job(sequence)` calling the public server. Use as final validation oracle in `AntifreezeDesignWorkflow`.
4. **AFP Design Workflow** — create `AntifreezeDesignWorkflow` in `workflows.py`: BoltzGen candidates → Boltz-2 affinity screen → Boltz-1 structure validation → AlphaFold3 final oracle → OpenMM refinement.

**BORG Log entry target**: Iteration 18 — Affinity-Guided AFP Design Loop.

---

### Iteration 19: Ensemble Scoring and Consensus
**Theme**: Multi-tool consensus for confident design decisions.

1. **Chai-2 integration** — add `ChaiSkills` as alternative complex predictor. Add `consensus_score()` utility that averages Boltz-2 and Chai-2 affinity estimates.
2. **RFdiffusion2 routing** — update `generate_backbone()` to support SMILES-conditioned enzyme design via RFdiffusion2 (`--ligand` flag).
3. **Agent upgrade** — extend `Critic` agent with ensemble scoring awareness: "If Boltz-2 and Chai-2 disagree by >2 kcal/mol, flag for human review."
4. **GUI**: Add "Affinity Dashboard" panel comparing multiple scorer outputs side-by-side in Plotly.

**BORG Log entry target**: Iteration 19 — Ensemble Scoring and Multi-Model Consensus.

---

### Iteration 20: Full BORG Autonomy — Closed-Loop AFP Design
**Theme**: Autonomous multi-step design campaign with agent-driven iteration.

1. **RFantibody** — integrate as optional loop-design skill for AFP binding-loop libraries.
2. **ESM3 API** (large model) — use `esm.sh` API for high-quality function-conditioned generation at scale.
3. **Campaign manager** — CrewAI `Methodologist` orchestrates multi-generation design: generate → score → select → mutate → iterate, logging each round to BORG.
4. **BORG auto-logging** — design campaign outcomes automatically appended to `BORG.md` iterations with quantitative results (predicted affinity, sequence identity to natural AFPs, structural RMSD).

**BORG Log entry target**: Iteration 20 — Autonomous AFP Design Campaign.

---

## Appendix A: Tool Installation Quick Reference

```bash
# Boltz-1 and Boltz-2 (same package)
pip install boltz

# BoltzGen
pip install boltzgen

# ESM3
pip install esm  # EvolutionaryScale SDK

# Chai-2
pip install chai-lab

# AlphaFold3 (local, GPU-heavy)
pip install alphafold3
# OR use web API: https://alphafoldserver.google.com

# RFdiffusion3 (Baker Lab, weights required)
# git clone https://github.com/baker-laboratory/rf_diffusion3
# See Baker Lab instructions for weight download
```

---

## Appendix B: AFP-Specific Integration Notes

The core challenge in AFP/ice-binding peptide design is modeling the protein–ice interface — a quasi-periodic surface with ~7.4 Å periodicity along the a-axis of hexagonal ice. The ideal ProteinToolbox AFP workflow for 2026:

1. **Target definition**: Use a cryo-EM ice crystal surface fragment as a PDB "target" (or synthetic periodic lattice).
2. **Generation**: BoltzGen or RFdiffusion3 generates binder candidates conditioned on the ice surface PDB.
3. **Sequence design**: ESM3 or ProteinMPNN refines sequences conditioned on generated backbone.
4. **Affinity screen**: Boltz-2 rapid-screens 100s of candidates; top 10 proceed.
5. **Structure validation**: Boltz-1 or AlphaFold3 predicts full complex structure.
6. **MD refinement**: OpenMM energy minimization and short MD trajectory.
7. **BORG logging**: Results auto-logged; `Critic` agent reviews and proposes next generation.

This pipeline transforms ProteinToolbox from a collection of wrapped tools into a genuine closed-loop AFP design system.

---

*Report generated by ProteinToolbox BORG autonomous review. Next review scheduled: Iteration 20 completion.*
