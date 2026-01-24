# ProteinToolbox

**ProteinToolbox** is an AI-powered suite for protein design, engineering, and simulation. It leverages modern open-source tools and `CrewAI` agents to assist researchers in designing complex biomolecules.

## Features

*   **Tool Registry**: A curated database of state-of-the-art tools (RFdiffusion, ProteinMPNN, Boltz-2, BioPhi, etc.).
*   **AI Agents**: Intelligent agents (Librarian, Architect, Technician) that help plan and execute design workflows.
*   **Resource Awareness**: Automatically checks for GPU availability for compute-intensive tasks.
*   **Modular**: Easy to add new tools and update existing ones.

## Included Tools (Registry)

*   **Boltz-2**: Biomolecular interaction modeling.
*   **BioPython**: Core biological computation.
*   **OpenMM**: Molecular dynamics simulation.
*   **ProteinMPNN**: Sequence design.
*   **RFdiffusion**: Backbone generation.
*   **BioPhi**: Antibody design.
*   (And more...)

## Installation

Prerequisites: Python 3.10 - 3.12

1.  Clone the repository:
    ```bash
    git clone git@github.com:mkuiper/ProteinToolbox.git
    cd ProteinToolbox
    ```

2.  Install dependencies:
    ```bash
    pip install .
    ```
    *Note: For GPU support, ensure you have the correct CUDA drivers installed for PyTorch and OpenMM.*

## Usage

Run the interactive CLI:

```bash
python main.py
```

### Example Workflow
1.  Select "Run a Design Agent Task".
2.  Enter: "I want to design a nanobody that binds to a specific viral protein structure."
3.  The agents will:
    *   Check for tools (e.g., RFdiffusion, ProteinMPNN).
    *   Check for GPU.
    *   Propose a sequence of steps (Backbone generation -> Sequence design -> Folding -> Validation).
    *   Provide the necessary commands.

## Structure

*   `src/proteintoolbox/`: Source code.
    *   `agents/`: CrewAI agent definitions.
    *   `registry.py`: Tool database management.
    *   `resources.py`: Hardware check logic.
*   `data/`: Configuration and registry files.
*   `examples/`: Example scripts.
*   `tests/`: Unit tests.

## License

[License Name Here]
