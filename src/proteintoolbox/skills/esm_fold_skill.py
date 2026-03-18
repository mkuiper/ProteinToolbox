"""
ESMFold Structure Prediction Skill

Wraps the ESMFold REST API (Meta / EvolutionaryScale Atlas) for fast
single-sequence structure prediction without requiring local GPU resources.
Falls back gracefully when the API is unreachable.
"""
from __future__ import annotations

import re
import requests


_ESMFOLD_API_URL = "https://esmatlas.com/resources/esm_fold"
_TIMEOUT_S = 120  # ESMFold can be slow for long sequences


def predict_structure_esmfold(sequence: str) -> str:
    """
    Predict a protein structure via the ESMFold REST API.

    Sends the amino-acid sequence to the public ESM Atlas endpoint and
    returns the PDB-format string of the predicted structure.

    Args:
        sequence: Single-letter amino acid sequence (case-insensitive).

    Returns:
        PDB-format string of the predicted structure.

    Raises:
        ValueError: If the sequence contains invalid characters.
        RuntimeError: If the API call fails or returns a non-PDB response.
    """
    sequence = sequence.strip().upper()
    if not sequence:
        raise ValueError("Empty sequence provided.")

    invalid = set(sequence) - set("ACDEFGHIKLMNPQRSTVWY")
    if invalid:
        raise ValueError(f"Invalid amino acid characters: {invalid}")

    try:
        response = requests.post(
            _ESMFOLD_API_URL,
            data=sequence,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=_TIMEOUT_S,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError(
            f"ESMFold API timed out after {_TIMEOUT_S}s. "
            "Try a shorter sequence or retry later."
        )
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            f"ESMFold API request failed: {exc}\n"
            "The ESM Atlas public endpoint may be temporarily unavailable."
        )

    text = response.text.strip()
    if not text.startswith("ATOM") and "ATOM" not in text[:500]:
        raise RuntimeError(
            f"ESMFold API returned unexpected response (not a PDB):\n{text[:300]}"
        )

    return text


def get_esmfold_confidence(pdb_string: str) -> dict:
    """
    Extract per-residue pLDDT confidence scores from an ESMFold PDB string.

    ESMFold encodes pLDDT in the B-factor column of ATOM records.

    Args:
        pdb_string: PDB-format string returned by predict_structure_esmfold.

    Returns:
        Dict with keys:
            - 'per_residue': list of (residue_num, plddt) tuples
            - 'mean_plddt': float average
            - 'high_confidence_fraction': fraction of residues with pLDDT >= 70
    """
    per_residue: list[tuple[int, float]] = []
    seen_residues: set[int] = set()

    for line in pdb_string.splitlines():
        if not line.startswith("ATOM"):
            continue
        try:
            res_num = int(line[22:26].strip())
            b_factor = float(line[60:66].strip())
        except (ValueError, IndexError):
            continue
        if res_num not in seen_residues:
            seen_residues.add(res_num)
            per_residue.append((res_num, b_factor))

    if not per_residue:
        return {"per_residue": [], "mean_plddt": 0.0, "high_confidence_fraction": 0.0}

    scores = [s for _, s in per_residue]
    mean_plddt = sum(scores) / len(scores)
    high_frac = sum(1 for s in scores if s >= 70) / len(scores)

    return {
        "per_residue": per_residue,
        "mean_plddt": round(mean_plddt, 2),
        "high_confidence_fraction": round(high_frac, 3),
    }
