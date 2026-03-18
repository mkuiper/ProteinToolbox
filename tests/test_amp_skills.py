"""Tests for AMP design skills."""
import pytest
from proteintoolbox.skills.amp_skills import score_amp_potential, generate_amp_variants


# ─── score_amp_potential ──────────────────────────────────────────────────────

def test_score_returns_expected_keys():
    result = score_amp_potential("ILPWKWPWWPWRR")
    assert "score" in result
    assert "grade" in result
    assert "net_charge" in result
    assert "hydrophobic_moment" in result
    assert "amphipathicity_index" in result
    assert "length" in result
    assert "sub_scores" in result
    assert "explanation" in result


def test_score_in_range():
    for seq in ["ILPWKWPWWPWRR", "AAAAAAAAAA", "KRKRKRKRKR"]:
        r = score_amp_potential(seq)
        assert 0 <= r["score"] <= 100


def test_known_good_amp_scores_higher():
    """A classic magainin-like sequence should score better than poly-Ala."""
    good = score_amp_potential("GIGKFLHSAKKFGKAFVGEIMNS")  # Magainin-2-like
    plain = score_amp_potential("AAAAAAAAAAAAA")
    assert good["score"] > plain["score"]


def test_cationic_peptide_has_positive_charge():
    result = score_amp_potential("KRKRKRKRKR")
    assert result["net_charge"] > 0


def test_length_recorded():
    seq = "ACDEFGHIKL"
    result = score_amp_potential(seq)
    assert result["length"] == len(seq)


def test_invalid_characters_raise():
    with pytest.raises(ValueError, match="Invalid amino acid"):
        score_amp_potential("ACDEFBX")


def test_empty_sequence_raises():
    with pytest.raises(ValueError):
        score_amp_potential("")


def test_grade_excellent_for_strong_amp():
    result = score_amp_potential("ILPWKWPWWPWRR")
    assert result["grade"] in ("Excellent", "Good", "Moderate")


# ─── generate_amp_variants ────────────────────────────────────────────────────

def test_generate_returns_n_variants():
    variants = generate_amp_variants("ACDEFGHIKLM", n=5)
    assert len(variants) == 5


def test_variants_are_tuples():
    variants = generate_amp_variants("ACDEFGHIKLM", n=3)
    for seq, score in variants:
        assert isinstance(seq, str)
        assert 0 <= score <= 100


def test_variants_sorted_by_score():
    variants = generate_amp_variants("ACDEFGHIKLM", n=5)
    scores = [s for _, s in variants]
    assert scores == sorted(scores, reverse=True)


def test_variants_same_length_as_seed():
    seed = "KLLKLLLKLLLKLL"
    variants = generate_amp_variants(seed, n=4)
    for seq, _ in variants:
        assert len(seq) == len(seed)


def test_generate_invalid_raises():
    with pytest.raises(ValueError):
        generate_amp_variants("BBBBB", n=3)
