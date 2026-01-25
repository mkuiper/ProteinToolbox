from Bio import SeqIO
from Bio.SeqUtils.ProtParam import ProteinAnalysis

def analyze_sequence(sequence: str) -> dict:
    """
    Calculates physicochemical properties of a protein sequence using BioPython.
    
    Args:
        sequence: Amino acid string.
        
    Returns:
        Dictionary of properties (MW, Isoelectric Point, Hydrophobicity, etc.)
    """
    analysed_seq = ProteinAnalysis(sequence)
    
    props = {
        "molecular_weight": analysed_seq.molecular_weight(),
        "isoelectric_point": analysed_seq.isoelectric_point(),
        "gravy": analysed_seq.gravy(),
        "aromaticity": analysed_seq.aromaticity(),
        "instability_index": analysed_seq.instability_index(),
        "secondary_structure_fraction": analysed_seq.secondary_structure_fraction(), # (Helix, Turn, Sheet)
        "extinction_coefficient": analysed_seq.molar_extinction_coefficient() # (reduced, oxidized)
    }
    
    return props

def get_amino_acid_percentages(sequence: str) -> dict:
    """
    Calculates the percentage of each amino acid in the sequence.
    """
    analysed_seq = ProteinAnalysis(sequence)
    return analysed_seq.get_amino_acids_percent()
