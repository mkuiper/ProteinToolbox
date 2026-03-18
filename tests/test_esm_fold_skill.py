"""Tests for ESMFold skill (local logic only — no live API calls)."""
import pytest
from proteintoolbox.skills.esm_fold_skill import (
    get_esmfold_confidence,
    predict_structure_esmfold,
)


# ─── get_esmfold_confidence ───────────────────────────────────────────────────

_MOCK_PDB = """\
ATOM      1  CA  ALA A   1      10.000  10.000  10.000  1.00 92.50           C
ATOM      2  CA  GLY A   2      12.000  10.000  10.000  1.00 45.00           C
ATOM      3  CA  LYS A   3      14.000  10.000  10.000  1.00 75.00           C
"""


def test_confidence_returns_expected_keys():
    conf = get_esmfold_confidence(_MOCK_PDB)
    assert "per_residue" in conf
    assert "mean_plddt" in conf
    assert "high_confidence_fraction" in conf


def test_confidence_mean_plddt_correct():
    conf = get_esmfold_confidence(_MOCK_PDB)
    expected_mean = (92.5 + 45.0 + 75.0) / 3
    assert abs(conf["mean_plddt"] - expected_mean) < 0.01


def test_confidence_high_fraction():
    conf = get_esmfold_confidence(_MOCK_PDB)
    # Residues 1 (92.5) and 3 (75.0) are >= 70; residue 2 (45.0) is not
    assert abs(conf["high_confidence_fraction"] - 2 / 3) < 0.01


def test_confidence_per_residue_count():
    conf = get_esmfold_confidence(_MOCK_PDB)
    assert len(conf["per_residue"]) == 3


def test_confidence_empty_pdb():
    conf = get_esmfold_confidence("REMARK no atoms here\n")
    assert conf["per_residue"] == []
    assert conf["mean_plddt"] == 0.0
    assert conf["high_confidence_fraction"] == 0.0


# ─── predict_structure_esmfold input validation ───────────────────────────────

def test_invalid_characters_raise_value_error():
    with pytest.raises(ValueError, match="Invalid amino acid"):
        predict_structure_esmfold("ACDEFBX2")


def test_empty_sequence_raises_value_error():
    with pytest.raises(ValueError, match="Empty"):
        predict_structure_esmfold("")


def test_whitespace_only_raises_value_error():
    with pytest.raises(ValueError, match="Empty"):
        predict_structure_esmfold("   ")
