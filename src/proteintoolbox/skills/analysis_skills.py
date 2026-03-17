from Bio import SeqIO
from Bio.SeqUtils.ProtParam import ProteinAnalysis
from typing import Dict
import collections

# Standard codon table (DNA -> amino acid, 1-letter)
CODON_TABLE = {
    'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
    'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
    'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
    'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
    'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
    'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
    'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
    'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
    'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
    'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
    'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
    'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
    'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
    'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
    'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
}

def get_codon_usage(dna_sequence: str) -> Dict[str, int]:
    """
    Computes codon usage frequencies from a DNA sequence.

    Args:
        dna_sequence (str): DNA/CDS sequence (must be divisible by 3).

    Returns:
        Dict[str, int]: Codon -> count mapping for all 64 codons.
    """
    seq = dna_sequence.upper().replace(" ", "").replace("\n", "")
    if len(seq) % 3 != 0:
        raise ValueError(f"DNA sequence length ({len(seq)}) is not divisible by 3.")

    # Initialize all 64 codons with 0 count
    counts: Dict[str, int] = {codon: 0 for codon in CODON_TABLE}
    for i in range(0, len(seq) - 2, 3):
        codon = seq[i:i+3]
        if codon in counts:
            counts[codon] += 1

    return counts


def get_codon_usage_heatmap_data(dna_sequence: str) -> dict:
    """
    Returns codon usage as a 2D grid suitable for a heatmap.
    Rows = first two bases, Cols = third base (TCAG).

    Args:
        dna_sequence (str): DNA sequence.

    Returns:
        dict with 'z' (2D values), 'x' (col labels), 'y' (row labels), 'text' (aa labels).
    """
    usage = get_codon_usage(dna_sequence)

    third_bases = ['T', 'C', 'A', 'G']
    first_two = sorted(set(c[:2] for c in CODON_TABLE))

    z = []
    text = []
    for prefix in first_two:
        row_z = []
        row_text = []
        for third in third_bases:
            codon = prefix + third
            count = usage.get(codon, 0)
            aa = CODON_TABLE.get(codon, '?')
            row_z.append(count)
            row_text.append(f"{codon}<br>({aa})")
        z.append(row_z)
        text.append(row_text)

    return {"z": z, "x": third_bases, "y": first_two, "text": text}


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
