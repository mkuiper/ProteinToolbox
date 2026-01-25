import pytest
from unittest.mock import patch, MagicMock
from tenacity import RetryError
from proteintoolbox.skills.bio_skills import fetch_pdb_structure, validate_sequence_robust
from hypothesis import given, strategies as st
import os

# 1. Test Robustness (Retries)
def test_fetch_pdb_structure_retries():
    """
    Test that fetch_pdb_structure retries on network error.
    """
    with patch("Bio.PDB.PDBList.PDBList.retrieve_pdb_file") as mock_retrieve:
        # Simulate network error (IOError)
        mock_retrieve.side_effect = IOError("Network is down")
        
        # We need to mock os.makedirs as well to avoid creating dirs during test
        with patch("os.makedirs"):
             with pytest.raises(RetryError):
                fetch_pdb_structure("1CRN")
            
        # Should have tried 3 times (default stop_after_attempt(3))
        assert mock_retrieve.call_count == 3

def test_fetch_pdb_structure_success_after_retry():
    """
    Test that fetch_pdb_structure succeeds if network recovers.
    """
    with patch("Bio.PDB.PDBList.PDBList.retrieve_pdb_file") as mock_retrieve:
        # Fail twice, then succeed
        mock_retrieve.side_effect = [IOError("Fail 1"), IOError("Fail 2"), "path/to/1CRN.pdb"]
        
        with patch("os.makedirs"):
            result = fetch_pdb_structure("1CRN")
        
        assert result == "path/to/1CRN.pdb"
        assert mock_retrieve.call_count == 3

def test_fetch_pdb_structure_invalid_id():
    """
    Test that PDBDownloadRequest validation works (bad ID).
    This should raise ValidationError (pydantic) not RetryError.
    """
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        # Don't need to patch network because validation happens first
        fetch_pdb_structure("BAD_ID_TOO_LONG")

# 2. Test Validation (Pydantic via function)
valid_amino_acids = "ACDEFGHIKLMNPQRSTVWY"

@given(st.text(alphabet=valid_amino_acids, min_size=1))
def test_validate_sequence_robust_valid(seq):
    cleaned = validate_sequence_robust(seq)
    assert cleaned == seq

@given(st.text(alphabet=valid_amino_acids, min_size=1))
def test_validate_sequence_robust_lowercase(seq):
    cleaned = validate_sequence_robust(seq.lower())
    assert cleaned == seq.upper()

@given(st.text(alphabet=valid_amino_acids, min_size=1), st.text(alphabet="BJOUXZ", min_size=1))
def test_validate_sequence_robust_invalid(valid, invalid):
    mixed = valid + invalid
    with pytest.raises(ValueError):
        validate_sequence_robust(mixed)
