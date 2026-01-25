import numpy as np
from Bio.PDB import PDBParser, Selection, NeighborSearch, Residue
from typing import Dict, List, Tuple, Any

def check_backbone_continuity(pdb_path: str, threshold: float = 2.0) -> List[str]:
    """
    Checks for breaks in the protein backbone (C-N distance > threshold).
    
    Args:
        pdb_path (str): Path to the PDB file.
        threshold (float): Max distance in Angstroms for a peptide bond. Default 2.0.
        
    Returns:
        List[str]: List of messages describing breaks (e.g., "Break between A:10 and A:11").
    """
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("check", pdb_path)
    breaks = []
    
    for model in structure:
        for chain in model:
            residues = [r for r in chain if r.get_id()[0] == " "] # Standard residues only
            for i in range(len(residues) - 1):
                res1 = residues[i]
                res2 = residues[i+1]
                
                # Check if residues are consecutive in numbering
                # (Note: PDB numbering can be messy, but strictly consecutive residues in sequence should be bonded)
                # Here we assume list order implies sequence order.
                
                if 'C' in res1 and 'N' in res2:
                    c_atom = res1['C']
                    n_atom = res2['N']
                    distance = c_atom - n_atom
                    
                    if distance > threshold:
                        breaks.append(f"Break in Chain {chain.id}: {res1.get_resname()}{res1.get_id()[1]} - {res2.get_resname()}{res2.get_id()[1]} (Dist: {distance:.2f}A)")
                else:
                    breaks.append(f"Missing backbone atoms in Chain {chain.id}: {res1.get_resname()}{res1.get_id()[1]} or {res2.get_resname()}{res2.get_id()[1]}")
                    
    return breaks

def check_steric_clashes(pdb_path: str, min_distance: float = 1.5) -> List[str]:
    """
    Checks for severe steric clashes between non-bonded atoms.
    
    Args:
        pdb_path (str): Path to PDB.
        min_distance (float): Distance threshold in Angstroms. Default 1.5 (severe clash).
        
    Returns:
        List[str]: List of clash descriptions.
    """
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("clash_check", pdb_path)
    atoms = Selection.unfold_entities(structure, 'A')
    
    ns = NeighborSearch(atoms)
    clashes = []
    
    # search_all returns all pairs within radius
    pairs = ns.search_all(min_distance)
    
    for atom1, atom2 in pairs:
        # Ignore atoms in same residue (bonded or close)
        if atom1.get_parent() == atom2.get_parent():
            continue
            
        # Ignore atoms in consecutive residues (peptide bond neighbors)
        res1 = atom1.get_parent()
        res2 = atom2.get_parent()
        if res1.get_parent() == res2.get_parent(): # Same chain
            try:
                # Simple check for consecutive ID
                id1 = res1.get_id()[1]
                id2 = res2.get_id()[1]
                if abs(id1 - id2) <= 1:
                    continue
            except:
                pass # Fallback to reporting if IDs are weird
        
        # If we are here, it's likely a clash or a disulfide bridge
        # Disulfide: SG - SG usually ~2.05A. If min_distance < 2.0, we might flag it.
        # Check for disulfide
        if atom1.element == 'S' and atom2.element == 'S':
            if 1.8 < (atom1 - atom2) < 2.5:
                continue # Likely bridge

        clashes.append(f"Clash: {res1.get_resname()}{res1.get_id()[1]}.{atom1.name} - {res2.get_resname()}{res2.get_id()[1]}.{atom2.name} ({atom1 - atom2:.2f}A)")
        
    return clashes

def validate_structure(pdb_path: str) -> Dict[str, Any]:
    """
    Runs a suite of validation checks on a PDB file.
    
    Args:
        pdb_path (str): Path to PDB.
        
    Returns:
        Dict: validation report.
    """
    breaks = check_backbone_continuity(pdb_path)
    clashes = check_steric_clashes(pdb_path)
    
    valid = len(breaks) == 0 and len(clashes) == 0
    
    return {
        "is_valid": valid,
        "backbone_breaks": breaks,
        "clashes": clashes,
        "clash_count": len(clashes)
    }
