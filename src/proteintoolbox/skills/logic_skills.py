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
