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

def clean_and_validate_sequence(raw_sequence: str, valid_chars: str = "ACDEFGHIKLMNPQRSTVWY") -> str:
    """
    Cleans a protein sequence string and validates it contains only standard amino acids.
    
    Args:
        raw_sequence (str): Input sequence (can contain whitespace, lower case).
        valid_chars (str): String of allowed characters. Default is 20 standard amino acids.
        
    Returns:
        str: Cleaned, uppercase sequence.
        
    Raises:
        ValueError: If invalid characters are found or sequence is empty.
    """
    if not raw_sequence:
        raise ValueError("Sequence is empty.")
        
    # Remove whitespace and newline characters
    clean_seq = "".join(raw_sequence.split()).upper()
    
    if not clean_seq:
        raise ValueError("Sequence is empty after cleaning.")

    # Check for invalid characters efficiently
    valid_set = set(valid_chars)
    invalid_chars = set(clean_seq) - valid_set
    
    if invalid_chars:
        # Sort for deterministic error messages
        bad_chars = "".join(sorted(list(invalid_chars)))
        raise ValueError(f"Invalid characters found in sequence: {bad_chars}")
        
    return clean_seq
    
