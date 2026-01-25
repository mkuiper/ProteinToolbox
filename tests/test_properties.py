
import pytest
from hypothesis import given, strategies as st, example
from proteintoolbox.skills.bio_skills import clean_and_validate_sequence
from proteintoolbox.skills.logic_skills import infer_functionality_issues

# Strategy for valid amino acids
valid_amino_acids = "ACDEFGHIKLMNPQRSTVWY"

@given(st.text(alphabet=valid_amino_acids, min_size=1))
def test_clean_and_validate_sequence_valid(seq):
    """
    Test that valid sequences are accepted and returned unchanged (if already uppercase).
    """
    cleaned = clean_and_validate_sequence(seq)
    assert cleaned == seq

@given(st.text(alphabet=valid_amino_acids, min_size=1))
def test_clean_and_validate_sequence_lowercase(seq):
    """
    Test that lowercase valid sequences are accepted and converted to uppercase.
    """
    lower_seq = seq.lower()
    cleaned = clean_and_validate_sequence(lower_seq)
    assert cleaned == seq

@given(st.text(min_size=1))
def test_clean_and_validate_sequence_whitespace(seq):
    """
    Test that whitespace is removed.
    """
    # Create a sequence with whitespace
    # This is a bit tricky with pure fuzzing, so we'll construct it specifically
    pass # See explicit test below

@given(st.lists(st.text(alphabet=valid_amino_acids, min_size=1), min_size=1))
def test_clean_and_validate_sequence_with_whitespace_fuzz(parts):
    """
    Test that joining parts with whitespace results in the correct sequence.
    """
    full_seq_clean = "".join(parts)
    full_seq_dirty = " 	 ".join(parts)
    
    cleaned = clean_and_validate_sequence(full_seq_dirty)
    assert cleaned == full_seq_clean

@given(st.text(min_size=1).filter(lambda s: any(c.upper() not in valid_amino_acids for c in s.split())))
def test_clean_and_validate_sequence_invalid(seq):
    """
    Test that sequences with invalid characters raise ValueError.
    Note: We filter to ensure at least one invalid char exists after cleaning whitespace.
    """
    # We must be careful not to generate a string that becomes empty or valid after whitespace removal
    # So we construct one explicitly with an invalid char
    pass # Rely on mixed strategy below

@given(st.text(alphabet=valid_amino_acids, min_size=1), st.text(alphabet="BJOUXZ123@#$", min_size=1))
def test_clean_and_validate_sequence_mixed_invalid(valid_part, invalid_part):
    """
    Test that mixing valid and invalid characters raises ValueError.
    """
    mixed = valid_part + invalid_part
    with pytest.raises(ValueError):
        clean_and_validate_sequence(mixed)

@given(st.text(alphabet=valid_amino_acids, min_size=1))
def test_infer_functionality_issues_cys(seq):
    """
    Test heuristics for Cysteine warnings.
    """
    # Calculate expected logic
    cys_count = seq.count('C')
    issues = infer_functionality_issues(seq)
    
    has_cys_warning = any("Cysteine Warning" in i for i in issues)
    
    if cys_count > 0 and cys_count % 2 != 0:
        assert has_cys_warning
    else:
        assert not has_cys_warning

@given(st.text(alphabet=valid_amino_acids, min_size=1, max_size=19))
def test_infer_functionality_issues_short(seq):
    """
    Test heuristic for short sequences.
    """
    issues = infer_functionality_issues(seq)
    assert any("Length Warning" in i for i in issues)

@given(st.text(alphabet=valid_amino_acids, min_size=20))
def test_infer_functionality_issues_long(seq):
    """
    Test heuristic for long sequences (should not have length warning).
    """
    issues = infer_functionality_issues(seq)
    assert not any("Length Warning" in i for i in issues)

@given(st.text(alphabet="PG", min_size=20)) # Pure Proline/Glycine
def test_infer_functionality_issues_disorder(seq):
    """
    Test heuristic for high disorder (100% P/G).
    """
    issues = infer_functionality_issues(seq)
    assert any("Composition Warning" in i for i in issues)

