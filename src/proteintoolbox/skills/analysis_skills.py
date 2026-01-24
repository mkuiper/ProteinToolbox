import protpy
from Bio import SeqIO

def analyze_sequence(sequence: str) -> dict:
    """
    Calculates physicochemical properties of a protein sequence.
    
    Args:
        sequence: Amino acid string.
        
    Returns:
        Dictionary of properties (MW, Isoelectric Point, Hydrophobicity, etc.)
    """
    # protpy requires imports for specific descriptors
    # But for basic props, BioPython's ProteinAnalysis is often simpler.
    # Let's use BioPython for basics and protpy for advanced descriptors if needed.
    
    from Bio.SeqUtils.ProtParam import ProteinAnalysis
    
    analysed_seq = ProteinAnalysis(sequence)
    
    props = {
        "molecular_weight": analysed_seq.molecular_weight(),
        "isoelectric_point": analysed_seq.isoelectric_point(),
        "gravy": analysed_seq.gravy(),
        "aromaticity": analysed_seq.aromaticity(),
        "instability_index": analysed_seq.instability_index()
    }
    
    return props

def get_amino_acid_composition(sequence: str) -> dict:
    import protpy as pe
    # using protpy to get composition
    return pe.amino_acid_composition(sequence)
