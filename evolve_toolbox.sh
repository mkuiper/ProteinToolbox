#!/bin/bash

# Configuration
START_ITER=7
ITERATIONS=50
LOG_FILE="ProteinToolbox/BORG.md"
CLI_CMD="gemini"

echo "Resuming ProteinToolbox Evolution Loop from Iteration $START_ITER..."

for i in $(seq $START_ITER $ITERATIONS); do
    echo "=================================================="
    echo "Optimization Cycle: $i / $ITERATIONS"
    echo "=================================================="
    
    # Construct the Focus
    case $((i % 5)) in
        0) FOCUS="GUI Experience and Visualization (e.g. Plotly charts, Mol* enhancements)" ;;
        1) FOCUS="New Skills and Integrations (Search for 'awesome protein design' or 'SOTA protein design models')" ;;
        2) FOCUS="Agent Logic and Reasoning (e.g. specialized roles, chain-of-thought protocols)" ;;
        3) FOCUS="Testing, Validation, and Robustness (e.g. property-based testing, better error recovery)" ;;
        4) FOCUS="Workflow recipes and examples (e.g. predefined antibody/enzyme design paths)" ;;
    esac

    PROMPT="Perform Iteration $i of the ProteinToolbox evolution.
    
    Current Focus: $FOCUS
    
    Instructions:
    1. **Research**: Find a new tool or method for '$FOCUS'.
    2. **Implement**: Add the feature. IF YOU ADD A NEW LIBRARY, YOU MUST:
        a. Run 'pip install <library>' in a shell command.
        b. Add the library name to 'pyproject.toml'.
    3. **Document**: Append a detailed entry to '$LOG_FILE' under '## Iteration $i'. Do not overwrite the file, APPEND to it.
    4. **Commit**: Run 'git add .' and 'git commit -m \"Evolution Iteration $i: Added $FOCUS features\"'.
    5. **Verify**: Run 'curl -I http://localhost:8501' to ensure GUI still works.
    
    Maintain high scientific standards. Be creative."

    echo "Sending prompt to Agent..."
    $CLI_CMD -y "$PROMPT"
    
    EXIT_CODE=$?
    if [ $EXIT_CODE -ne 0 ]; then
        echo "Error: Agent exited with code $EXIT_CODE. Pausing loop."
        break
    fi
    
    echo "Iteration $i complete. Waiting 10 seconds..."
    sleep 10
done

echo "Evolution Loop Finished."
