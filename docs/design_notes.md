# Design Notes

## Architecture: Skills vs. MCP Servers

Based on recent analysis (e.g., "MCP is Dead" discussions), we have adopted a hybrid "Skills-First" architecture for `ProteinToolbox`.

### The "Skills" Approach
Instead of wrapping every tool in a heavyweight HTTP server (MCP), we implement lightweight Python functions called **Skills**.
*   **Definition**: A Skill is a standalone Python function with clear inputs/outputs and documentation, located in `src/proteintoolbox/skills/`.
*   **Benefits**:
    *   **Lower Latency**: Direct function calls within the agent's process.
    *   **Context Efficiency**: We inject only the necessary skill signatures into the agent's context, rather than a full API schema.
    *   **Simplicity**: No need to manage external server processes for simple tasks like PDB parsing.

### When to use MCP?
We reserve full MCP servers for:
*   **Remote Resources**: Accessing a GPU cluster or cloud API (e.g., Boltz-2 Inference Server).
*   **Complex State**: Tools that need to maintain significant state memory outside the agent's lifecycle.
*   **Language Agnostic**: If a tool is written in C++ or Rust and exposes an HTTP API, an MCP wrapper is appropriate.

## Agent Design
*   **Librarian**: Uses `ToolRegistry` to find the right tool.
*   **Architect**: Plans the high-level scientific workflow.
*   **Technician**: Executes specific "Skills" (Python functions) or generates CLI commands for external tools.

## Web GUI
*   **Framework**: Streamlit.
*   **Location**: `src/proteintoolbox/gui/app.py`.
*   **Features**:
    *   **Project Management**: Create and switch between projects (persisted in `data/projects/`).
    *   **Direct Tool Access**: Wrappers around skills for manual use within the context of the active project.
    *   **Agent Workflow**: Interface to the CrewAI backend.
    *   **Visualization**: **Mol* (streamlit-molstar)** for high-quality, interactive 3D structure viewing.

## Data Flow
*   **Filesystem**: The current prototype relies on the shared filesystem (paths passed as strings).
*   **Projects**: Each project has its own directory in `data/projects/{name}/` containing metadata and all generated files (PDBs, etc.).
*   **Future**: We plan to implement a JSON-based "Manifest" or "ExperimentContext" object that tracks:
    *   `input_pdb`: Path to starting structure.
    *   `designed_backbones`: List of paths.
    *   `sequences`: List of sequences or FASTA paths.
    *   `scores`: Dictionary of metrics.

## Future Plans
*   **Data Compatibility**: Use JSON manifests to track file paths (PDBs, FASTA) as they move between tools.
*   **Web GUI**: A simple interface (Streamlit/Chainlit) to construct workflows visually.
