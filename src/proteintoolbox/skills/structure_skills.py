import freesasa
from Bio.PDB import PDBParser
import os
from typing import Dict, List, Tuple

def calculate_sasa(pdb_path: str) -> Dict[str, float]:
    """
    Calculates the Solvent Accessible Surface Area (SASA) of a protein structure using FreeSASA.

    Args:
        pdb_path (str): Path to the PDB file.

    Returns:
        Dict[str, float]: A dictionary containing 'total', 'polar', and 'apolar' SASA values.
    """
    structure = freesasa.Structure(pdb_path)
    result = freesasa.calc(structure)
    
    # Classify by polarity (simplified default classifier)
    # freesasa has default classifiers, usually N, O are polar, C, S are apolar
    
    classifier = freesasa.Classifier()
    
    total = result.totalArea()
    polar = 0.0
    apolar = 0.0
    
    for i in range(structure.nAtoms()):
        # freesasa requires stripping whitespace for cleaner matching sometimes, 
        # but usually returns stripped strings.
        res_name = structure.residueName(i).strip()
        atom_name = structure.atomName(i).strip()
        atom_area = result.atomArea(i)
        
        cls = classifier.classify(res_name, atom_name)
        
        if cls == "Polar":
            polar += atom_area
        elif cls == "Apolar":
            apolar += atom_area
    
    return {
        "total": total,
        "polar": polar,
        "apolar": apolar
    }

def get_residue_sasa(pdb_path: str) -> Dict[str, float]:
    """
    Calculates SASA for each residue.

    Args:
        pdb_path (str): Path to the PDB file.

    Returns:
        Dict[str, float]: Dictionary mapping residue ID (Chain:ResNum) to SASA value.
    """
    structure = freesasa.Structure(pdb_path)
    result = freesasa.calc(structure)
    
    residue_areas = {}
    
    # Iterate through result
    # FreeSASA structure iteration is hierarchical
    for i in range(structure.nAtoms()):
        res_name = structure.residueName(i)
        res_num = structure.residueNumber(i)
        chain_id = structure.chainLabel(i)
        atom_area = result.atomArea(i)
        
        key = f"{chain_id}:{res_num}_{res_name}"
        residue_areas[key] = residue_areas.get(key, 0.0) + atom_area
        
    return residue_areas

def identify_surface_residues(pdb_path: str, threshold: float = 10.0) -> List[str]:
    """
    Identifies residues that are exposed on the surface (SASA > threshold).
    
    Args:
        pdb_path (str): Path to PDB.
        threshold (float): Area threshold in square Angstroms.
        
    Returns:
        List[str]: List of residue identifiers.
    """
    res_sasa = get_residue_sasa(pdb_path)
    return [res_id for res_id, area in res_sasa.items() if area > threshold]
