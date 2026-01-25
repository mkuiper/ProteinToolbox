from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import re

class ProteinSequenceRequest(BaseModel):
    """
    Model for validating protein sequence inputs.
    """
    sequence: str = Field(..., description="The amino acid sequence", min_length=1)
    id: Optional[str] = Field(None, description="Optional identifier for the sequence")
    valid_chars: str = Field("ACDEFGHIKLMNPQRSTVWY", description="Allowed amino acid characters")

    @field_validator('sequence')
    @classmethod
    def validate_sequence_chars(cls, v, info):
        valid_chars = info.data.get('valid_chars', "ACDEFGHIKLMNPQRSTVWY")
        # Clean whitespace first? Or assume raw?
        # Let's clean it here to be robust
        clean_v = "".join(v.split()).upper()
        
        invalid_chars = set(clean_v) - set(valid_chars)
        if invalid_chars:
            # Sort for deterministic error messages
            bad_chars = "".join(sorted(list(invalid_chars)))
            raise ValueError(f"Sequence contains invalid characters: {bad_chars}")
        
        if not clean_v:
            raise ValueError("Sequence is empty after cleaning.")
            
        return clean_v

class PDBDownloadRequest(BaseModel):
    pdb_id: str = Field(..., min_length=4, max_length=4, pattern=r"^[0-9A-Za-z]{4}$")
    output_dir: str = Field("data/pdb", description="Directory to save PDB file")
