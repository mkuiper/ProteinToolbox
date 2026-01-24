# RFdiffusion

**Category**: Design (Backbone Generation)
**Repository**: [github.com/RosettaCommons/RFdiffusion](https://github.com/RosettaCommons/RFdiffusion)

## Description
RFdiffusion is a state-of-the-art method for generating protein backbones using diffusion models. It can generate unconditionally or conditioned on motifs, hotspots, or binders.

## Usage in ProteinToolbox
Currently integrated as a **CLI wrapper**. The agent generates the shell command to run RFdiffusion inference.

## Future Skill Integration
We plan to create a wrapper `design_skills.generate_backbone(prompt)` that handles the CLI execution and file management transparently.

## Requirements
*   NVIDIA GPU (High VRAM recommended).
*   Weights files (must be downloaded separately).
*   Dedicated Conda environment (often conflicts with other tools).
