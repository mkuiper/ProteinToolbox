from proteintoolbox.skills import analysis_skills

def check_design_constraints(sequence: str, constraints: dict) -> dict:
    """
    Evaluates a protein sequence against a set of logical constraints.
    
    Args:
        sequence: The amino acid sequence.
        constraints: A dictionary of constraints, e.g., 
                     {'max_molecular_weight': 50000, 'min_instability_index': 40}
    
    Returns:
        dict: A report with 'pass' (bool), 'violations' (list), and 'metrics' (dict).
    """
    props = analysis_skills.analyze_sequence(sequence)
    violations = []
    
    # 1. Molecular Weight Check
    if 'max_molecular_weight' in constraints:
        if props['molecular_weight'] > constraints['max_molecular_weight']:
            violations.append(f"Molecular Weight {props['molecular_weight']:.2f} > {constraints['max_molecular_weight']}")
            
    if 'min_molecular_weight' in constraints:
        if props['molecular_weight'] < constraints['min_molecular_weight']:
            violations.append(f"Molecular Weight {props['molecular_weight']:.2f} < {constraints['min_molecular_weight']}")

    # 2. Isoelectric Point Check
    if 'target_pi_range' in constraints:
        min_pi, max_pi = constraints['target_pi_range']
        if not (min_pi <= props['isoelectric_point'] <= max_pi):
             violations.append(f"Isoelectric Point {props['isoelectric_point']:.2f} outside range {min_pi}-{max_pi}")

    # 3. Instability Index (Guruprasad method)
    # Value > 40 indicates unstable structure
    if 'require_stable' in constraints and constraints['require_stable']:
        if props['instability_index'] > 40:
            violations.append(f"Instability Index {props['instability_index']:.2f} > 40 (Predicted Unstable)")

    # 4. GRAVY (Grand average of hydropathicity)
    # Positive: hydrophobic, Negative: hydrophilic
    if 'solubility_preference' in constraints:
        pref = constraints['solubility_preference']
        if pref == 'hydrophilic' and props['gravy'] > 0:
             violations.append(f"GRAVY {props['gravy']:.2f} is positive (Hydrophobic) but 'hydrophilic' requested")
        elif pref == 'hydrophobic' and props['gravy'] < 0:
             violations.append(f"GRAVY {props['gravy']:.2f} is negative (Hydrophilic) but 'hydrophobic' requested")

    return {
        "pass": len(violations) == 0,
        "violations": violations,
        "metrics": props
    }

def infer_functionality_issues(sequence: str) -> list:
    """
    Uses heuristic reasoning to infer potential functionality issues based on sequence composition.
    """
    issues = []
    length = len(sequence)
    
    # Heuristic 1: Sequence too short for stable fold
    if length < 20:
        issues.append("Length Warning: Sequence is very short (<20 AA), unlikely to form a stable tertiary structure independently.")
        
    # Heuristic 2: Cysteine content and Disulfide bonds
    cys_count = sequence.count('C')
    if cys_count > 0 and cys_count % 2 != 0:
        issues.append(f"Cysteine Warning: Odd number of Cysteines ({cys_count}). This may lead to free thiols or intermolecular disulfide aggregation.")
        
    # Heuristic 3: Proline/Glycine abundance (disordered regions)
    pro_gly_percent = (sequence.count('P') + sequence.count('G')) / length
    if pro_gly_percent > 0.3:
        issues.append(f"Composition Warning: High Proline/Glycine content ({pro_gly_percent:.1%}). Suggests potential intrinsic disorder.")

    return issues

def validate_workflow_logic(steps: list[str]) -> dict:
    """
    Analyzes a list of workflow steps for logical dependency violations.
    Assumes standard keywords: 'search', 'design', 'fold', 'structure', 'dock', 'minimize', 'validate'.
    """
    errors = []
    warnings = []
    
    # Normalize steps for analysis
    normalized_steps = [s.lower() for s in steps]
    
    # Define generic dependencies
    # key: must appear AFTER value
    dependencies = {
        'dock': ['fold', 'structure', 'pdb'],
        'minimize': ['fold', 'structure', 'design', 'mutation'],
        'validate': ['design', 'fold', 'dock'],
        'design': ['search', 'target'],
    }
    
    found_concepts = set()
    
    for i, step in enumerate(normalized_steps):
        # Identify concepts in this step
        current_concepts = []
        for key in ['dock', 'fold', 'structure', 'design', 'mutation', 'search', 'target', 'minimize', 'validate', 'pdb']:
            if key in step:
                current_concepts.append(key)
        
        # Check dependencies
        for concept in current_concepts:
            if concept in dependencies:
                required_precursors = dependencies[concept]
                # Check if ANY of the precursors have been seen yet
                has_precursor = any(p in found_concepts for p in required_precursors)
                
                # Special case: 'structure' might be an input, so we might not need to fold if we fetched a PDB.
                # But generally, we check if we are doing an action that requires a structure.
                
                # If it's the first step, it can't have precursors (unless provided externally, which we can't check easily here)
                if not has_precursor and i > 0:
                     # Check if maybe it's implicitly available?
                     pass 
                
                # Simple Logic: If I want to Dock, I must have a Structure.
                if concept == 'dock' and not any(x in found_concepts for x in ['fold', 'structure', 'pdb']):
                    errors.append(f"Step {i+1} '{step}' attempts to Dock without a prior Structure/Fold/PDB step.")

        # Update found concepts
        found_concepts.update(current_concepts)
        
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def propose_refinements(steps: list[str]) -> list[str]:
    """
    Suggests improvements to a workflow plan based on best practices.
    """
    suggestions = []
    text = " ".join(steps).lower()
    
    # 1. Post-Design Minimization
    if ('design' in text or 'mutation' in text) and 'minimize' not in text:
        suggestions.append("Consider adding a 'minimization' step after sequence design to relax the structure.")
        
    # 2. Validation
    if ('design' in text or 'dock' in text) and 'validate' not in text:
        suggestions.append("The workflow lacks an explicit 'validation' or 'analysis' step to check quality metrics.")
        
    # 3. Aggregation Check for heavy design
    if 'design' in text and 'aggregation' not in text:
        suggestions.append("For protein design, it is recommended to check for 'aggregation' prone regions.")

    return suggestions

def get_reasoning_template(strategy: str) -> str:
    """
    Returns a Chain-of-Thought (CoT) template for a given strategy.
    Strategies: 'scientific_method', 'design_cycle', 'root_cause_analysis', 'first_principles'.
    """
    templates = {
        'scientific_method': (
            "1. Observation: What is the current state or problem?\n"
            "2. Question: What specific biological question are we asking?\n"
            "3. Hypothesis: What do we expect to happen?\n"
            "4. Experiment: How will we test this (tools/methods)?\n"
            "5. Analysis: How will we interpret the results?"
        ),
        'design_cycle': (
            "1. Specify Requirements: Target properties (stability, binding, etc.).\n"
            "2. Generate Candidates: Methods for sequence/structure generation.\n"
            "3. Simulate/Evaluate: In silico validation steps.\n"
            "4. Refine: Iterative improvement strategy.\n"
            "5. Final Selection: Criteria for choosing the best candidate."
        ),
        'root_cause_analysis': (
            "1. Problem Definition: What failed or is suboptimal?\n"
            "2. Possible Causes: List potential reasons (sequence, structure, parameters).\n"
            "3. Investigation: Check each cause (e.g., steric clashes, unstable fold).\n"
            "4. Conclusion: Identify the primary driver.\n"
            "5. Mitigation: Propose a fix."
        ),
        'first_principles': (
            "1. Fundamental Constraints: What are the physical limits (thermodynamics, sterics)?\n"
            "2. Component Analysis: Break down into amino acids, secondary structures, domains.\n"
            "3. Construction: Build the solution from these basic components.\n"
            "4. Verification: Does the built solution satisfy fundamental constraints?"
        )
    }
    return templates.get(strategy, "Unknown strategy. Available: " + ", ".join(templates.keys()))

def decompose_request(request: str) -> dict:
    """
    Decomposes a user request into inferred sub-components using keyword heuristics.
    Returns a structured dictionary of { 'intent': str, 'implied_steps': list, 'constraints': list }
    """
    request_lower = request.lower()
    
    intent = "unknown"
    implied_steps = []
    constraints = []
    
    # 1. Determine Intent
    if "design" in request_lower or "optimize" in request_lower:
        intent = "design"
    elif "analyze" in request_lower or "assess" in request_lower:
        intent = "analysis"
    elif "dock" in request_lower or "bind" in request_lower:
        intent = "interaction"
        
    # 2. Infer Steps based on Intent and keywords
    if intent == "design":
        implied_steps.append("search_literature_or_pdb")
        implied_steps.append("analyze_target")
        implied_steps.append("generate_sequences")
        implied_steps.append("validate_designs")
        
    if intent == "interaction" or "dock" in request_lower:
        if "dock" not in implied_steps:
            implied_steps.append("prepare_receptor")
            implied_steps.append("prepare_ligand")
            implied_steps.append("run_docking")
            
    if intent == "analysis":
        implied_steps.append("load_structure")
        implied_steps.append("calculate_properties")
        
    # 3. Infer Constraints
    if "stable" in request_lower:
        constraints.append("min_instability_index")
    if "soluble" in request_lower:
        constraints.append("solubility_preference")
    if "binder" in request_lower:
        constraints.append("high_affinity")

    return {
        "intent": intent,
        "implied_steps": implied_steps,
        "inferred_constraints": constraints
    }