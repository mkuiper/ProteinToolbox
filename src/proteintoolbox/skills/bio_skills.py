import os
from Bio.PDB import PDBList, PDBParser, PPBuilder
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
    # Use PDBParser to get structure
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("struct", pdb_path)
    
    # Use PPBuilder to extract polypeptides
    ppb = PPBuilder()
    pps = ppb.build_peptides(structure)
    
    # Concatenate all polypeptide sequences (usually just one for a single chain)
    sequence = ""
    for pp in pps:
        sequence += str(pp.get_sequence())
        
    return sequence
