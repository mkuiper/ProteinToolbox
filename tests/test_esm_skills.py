import pytest
from proteintoolbox.skills import esm_skills

def test_esm_embedding():
    """Test that ESM embedding generation works and returns correct shape."""
    seq = "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
    embedding = esm_skills.get_embedding(seq)
    
    assert isinstance(embedding, list)
    assert all(isinstance(x, float) for x in embedding)
    # esm2_t6_8M_UR50D has hidden size 320
    assert len(embedding) == 320
