import os
from Bio.PDB import PDBList, PDBParser
from typing import Optional

def fetch_pdb_structure(pdb_id: str, output_dir: str = "data/pdb") -> str:
    """
    Downloads a PDB structure file.

    Args:
        pdb_id (str): The 4-letter PDB code (e.g., '1CRN').
        output_dir (str): Directory to save the file.

    Returns:
        str: Path to the downloaded file.
    """
    pdbl = PDBList()
    os.makedirs(output_dir, exist_ok=True)
    file_path = pdbl.retrieve_pdb_file(pdb_id, pdir=output_dir, file_format="pdb")
    return file_path

def get_sequence_from_pdb(pdb_path: str) -> str:
    """
    Extracts the amino acid sequence from a PDB file.

    Args:
        pdb_path (str): Path to the PDB file.

    Returns:
        str: The amino acid sequence (1-letter code).
    """
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("struct", pdb_path)
    sequence = ""
    # Simple extraction (first model, first chain) - scalable for more complex needs
    for model in structure:
        for chain in model:
            for residue in chain:
                if residue.get_id()[0] == ' ': # Standard residue
                    # Convert 3-letter to 1-letter (simplified logic)
                    # For a robust skill, we'd use Bio.SeqUtils
                    resname = residue.get_resname()
                    # Placeholder for mapping logic or use BioPython's Polypeptide builder
                    pass 
    return "MKT..." # Dummy return for prototype, normally implemented with SeqUtils
