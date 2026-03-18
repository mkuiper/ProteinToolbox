"""
Antimicrobial Peptide (AMP) Design Skills

Provides heuristic scoring and sequence optimization for antimicrobial peptides.
All calculations are pure-Python / NumPy — no external ML dependencies required.

Key references:
- Eisenberg et al. (1984) hydrophobicity scale
- Wimley-White interfacial scale for membrane partitioning
- Gautier et al. amphipathicity descriptors
"""
from __future__ import annotations

import math
import random
from typing import Any


# ─── Physico-chemical lookup tables ──────────────────────────────────────────

# Eisenberg consensus hydrophobicity scale (normalized, 1984)
_EISENBERG: dict[str, float] = {
    "A": 0.25, "R": -1.76, "N": -0.64, "D": -0.72, "C": 0.04,
    "Q": -0.69, "E": -0.62, "G": 0.16, "H": -0.40, "I": 0.73,
    "L": 0.53, "K": -1.10, "M": 0.26, "F": 0.61, "P": -0.07,
    "S": -0.26, "T": -0.18, "W": 0.37, "Y": 0.02, "V": 0.54,
}

# Net charge contribution at pH 7 (simplified Henderson-Hasselbalch)
_CHARGE_PH7: dict[str, float] = {
    "K": +1.0, "R": +1.0, "H": +0.1,  # positive
    "D": -1.0, "E": -1.0,              # negative
}

# Amino acids grouped by AMP-relevance
_POSITIVE_AA = set("KRH")
_NEGATIVE_AA = set("DE")
_HYDROPHOBIC_AA = set("ILMFVW")
_SMALL_AA = set("AGSP")

# Substitution table for AMP variant generation
# Maps target property → residues to try
_AMP_SUBS: dict[str, list[str]] = {
    "positive":    ["K", "R"],
    "hydrophobic": ["L", "I", "V", "F"],
    "flexible":    ["G", "A"],
}


# ─── Core calculations ────────────────────────────────────────────────────────

def _net_charge(sequence: str) -> float:
    """Compute net charge at pH 7."""
    return sum(_CHARGE_PH7.get(aa, 0.0) for aa in sequence)


def _hydrophobic_moment(sequence: str, angle_deg: float = 100.0) -> float:
    """
    Compute the hydrophobic moment (μH) using the Eisenberg scale.

    Uses a helical wheel projection at the given angle between residues
    (100° is canonical for α-helices).
    """
    if not sequence:
        return 0.0
    angle_rad = math.radians(angle_deg)
    sin_sum = 0.0
    cos_sum = 0.0
    for i, aa in enumerate(sequence):
        h = _EISENBERG.get(aa, 0.0)
        sin_sum += h * math.sin(i * angle_rad)
        cos_sum += h * math.cos(i * angle_rad)
    mu_h = math.sqrt(sin_sum ** 2 + cos_sum ** 2) / len(sequence)
    return round(mu_h, 4)


def _amphipathicity_index(sequence: str) -> float:
    """
    Rough amphipathicity index: ratio of max hydrophobic moment to mean |hydrophobicity|.
    Ranges from ~0 (not amphipathic) to ~2+ (highly amphipathic).
    """
    mu_h = _hydrophobic_moment(sequence)
    mean_h = sum(abs(_EISENBERG.get(aa, 0.0)) for aa in sequence) / max(len(sequence), 1)
    if mean_h < 1e-6:
        return 0.0
    return round(mu_h / mean_h, 3)


def _validate_sequence(sequence: str) -> str:
    """Uppercase and validate sequence."""
    sequence = sequence.strip().upper()
    if not sequence:
        raise ValueError("Empty sequence.")
    invalid = set(sequence) - set(_EISENBERG.keys())
    if invalid:
        raise ValueError(f"Invalid amino acid characters: {invalid}")
    return sequence


# ─── Public skills ────────────────────────────────────────────────────────────

def score_amp_potential(sequence: str) -> dict[str, Any]:
    """
    Compute a heuristic AMP (Antimicrobial Peptide) potential score (0–100).

    The score is based on four sub-scores, each weighted:
      1. Net charge at pH 7         (weight 30) — optimal +2 to +9
      2. Hydrophobic moment μH      (weight 30) — higher is better
      3. Length                     (weight 20) — optimal 10–40 residues
      4. Amphipathicity index       (weight 20) — higher is better

    Args:
        sequence: Single-letter amino acid sequence (case-insensitive).

    Returns:
        Dict with keys:
            - 'score': float 0–100
            - 'grade': str ('Excellent' / 'Good' / 'Moderate' / 'Poor')
            - 'net_charge': float
            - 'hydrophobic_moment': float
            - 'amphipathicity_index': float
            - 'length': int
            - 'sub_scores': dict of individual component scores (0–100)
            - 'explanation': list[str] of human-readable notes
    """
    sequence = _validate_sequence(sequence)
    n = len(sequence)

    charge = _net_charge(sequence)
    mu_h = _hydrophobic_moment(sequence)
    amphi = _amphipathicity_index(sequence)

    # --- Sub-score: charge (optimal +2 to +9) ---
    if 2 <= charge <= 9:
        charge_score = 100.0
    elif 0 < charge < 2:
        charge_score = 60.0 + 40.0 * (charge / 2)
    elif charge > 9:
        charge_score = max(0.0, 100.0 - (charge - 9) * 8)
    else:
        charge_score = max(0.0, 50.0 + charge * 25)  # negative charge hurts

    # --- Sub-score: hydrophobic moment (0–0.6 typical; >0.4 good) ---
    hm_score = min(100.0, (mu_h / 0.5) * 100)

    # --- Sub-score: length (10–40 optimal) ---
    if 10 <= n <= 40:
        length_score = 100.0
    elif n < 10:
        length_score = (n / 10) * 100
    elif 40 < n <= 60:
        length_score = max(40.0, 100.0 - (n - 40) * 3)
    else:
        length_score = max(0.0, 40.0 - (n - 60) * 2)

    # --- Sub-score: amphipathicity (>0.5 good) ---
    amphi_score = min(100.0, (amphi / 0.8) * 100)

    total = (
        0.30 * charge_score +
        0.30 * hm_score +
        0.20 * length_score +
        0.20 * amphi_score
    )
    total = round(min(100.0, max(0.0, total)), 1)

    # Grade
    if total >= 75:
        grade = "Excellent"
    elif total >= 55:
        grade = "Good"
    elif total >= 35:
        grade = "Moderate"
    else:
        grade = "Poor"

    # Human-readable notes
    notes: list[str] = []
    if charge < 2:
        notes.append(f"Low net charge ({charge:+.1f}); AMPs typically need +2 to +9.")
    elif charge > 9:
        notes.append(f"Very high charge ({charge:+.1f}) may reduce membrane selectivity.")
    else:
        notes.append(f"Net charge {charge:+.1f} is in the optimal AMP range (+2 to +9).")

    if mu_h >= 0.4:
        notes.append(f"Hydrophobic moment {mu_h:.3f} is strong (good membrane insertion).")
    elif mu_h >= 0.2:
        notes.append(f"Hydrophobic moment {mu_h:.3f} is moderate.")
    else:
        notes.append(f"Hydrophobic moment {mu_h:.3f} is low; consider increasing amphipathicity.")

    if 10 <= n <= 40:
        notes.append(f"Length {n} aa is in the optimal AMP range (10–40).")
    else:
        notes.append(f"Length {n} aa is outside the typical AMP range (10–40).")

    hydrophobic_frac = sum(1 for aa in sequence if aa in _HYDROPHOBIC_AA) / n
    if hydrophobic_frac < 0.3:
        notes.append(f"Hydrophobic residue fraction ({hydrophobic_frac:.0%}) is low; "
                     "consider adding L/I/V/F residues.")
    elif hydrophobic_frac > 0.6:
        notes.append(f"Very high hydrophobic fraction ({hydrophobic_frac:.0%}); "
                     "may reduce aqueous solubility.")
    else:
        notes.append(f"Hydrophobic residue fraction {hydrophobic_frac:.0%} is balanced.")

    return {
        "score": total,
        "grade": grade,
        "net_charge": round(charge, 2),
        "hydrophobic_moment": mu_h,
        "amphipathicity_index": amphi,
        "length": n,
        "sub_scores": {
            "charge": round(charge_score, 1),
            "hydrophobic_moment": round(hm_score, 1),
            "length": round(length_score, 1),
            "amphipathicity": round(amphi_score, 1),
        },
        "explanation": notes,
    }


def generate_amp_variants(sequence: str, n: int = 5) -> list[tuple[str, float]]:
    """
    Generate AMP-optimized sequence variants by targeted substitution.

    Strategy:
      - If net charge < 2: substitute some D/E/N/Q with K or R
      - If hydrophobic moment < 0.3: substitute small residues at even positions with L/I
      - Random single-residue substitutions to explore local sequence space
      - Each candidate is scored; top-n by AMP score are returned

    Args:
        sequence: Seed amino acid sequence (case-insensitive).
        n: Number of top variants to return.

    Returns:
        List of (variant_sequence, amp_score) tuples, sorted by score descending.
        The original sequence is always included as the first candidate.
    """
    sequence = _validate_sequence(sequence)
    seq_len = len(sequence)

    candidates: set[str] = {sequence}

    base_charge = _net_charge(sequence)
    base_mu_h = _hydrophobic_moment(sequence)

    def _mutate(seq: str, pos: int, new_aa: str) -> str:
        return seq[:pos] + new_aa + seq[pos + 1:]

    # Strategy 1: Improve charge if too low
    if base_charge < 2:
        targets = [i for i, aa in enumerate(sequence) if aa in "DENQ"]
        random.shuffle(targets)
        for pos in targets[:4]:
            for new_aa in ["K", "R"]:
                candidates.add(_mutate(sequence, pos, new_aa))

    # Strategy 2: Improve hydrophobic moment at even positions
    if base_mu_h < 0.3:
        for pos in range(0, seq_len, 2):
            if sequence[pos] in _SMALL_AA:
                for new_aa in ["L", "I", "V"]:
                    candidates.add(_mutate(sequence, pos, new_aa))

    # Strategy 3: Improve charge at odd positions
    for pos in range(1, seq_len, 2):
        if sequence[pos] in _NEGATIVE_AA:
            for new_aa in ["K", "R"]:
                candidates.add(_mutate(sequence, pos, new_aa))

    # Strategy 4: Random single substitutions for diversity
    rng = random.Random(42)
    for _ in range(max(30, n * 6)):
        pos = rng.randrange(seq_len)
        orig_aa = sequence[pos]
        # Pick a random substitution that isn't the same
        pool: list[str]
        if orig_aa in _NEGATIVE_AA:
            pool = ["K", "R", "A", "L"]
        elif orig_aa in _POSITIVE_AA:
            pool = ["K", "R", "L", "I"]
        elif orig_aa in _HYDROPHOBIC_AA:
            pool = ["L", "I", "V", "K"]
        else:
            pool = ["K", "L", "A", "R", "I"]
        new_aa = rng.choice([aa for aa in pool if aa != orig_aa] or pool)
        candidates.add(_mutate(sequence, pos, new_aa))

    # Score all candidates
    scored: list[tuple[str, float]] = []
    for cand in candidates:
        try:
            result = score_amp_potential(cand)
            scored.append((cand, result["score"]))
        except ValueError:
            pass

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:n]
