import torch
from transformers import AutoTokenizer, EsmModel

class ESMSkills:
    def __init__(self, model_name: str = "facebook/esm2_t6_8M_UR50D"):
        """
        Initializes the ESM model wrapper.
        
        Args:
            model_name (str): The Hugging Face model ID. Defaults to the smallest ESM2 model (8M params)
                              for efficiency in this toolbox environment.
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self._device = "cuda" if torch.cuda.is_available() else "cpu"

    def _load_model(self):
        """Lazy loads the model and tokenizer."""
        if self.model is None:
            # print(f"Loading ESM model: {self.model_name} on {self._device}...") 
            # (Silence output for CLI tool unless debug)
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = EsmModel.from_pretrained(self.model_name).to(self._device)
                self.model.eval()
            except Exception as e:
                raise RuntimeError(f"Failed to load ESM model {self.model_name}: {e}")

    def get_embedding(self, sequence: str) -> list[float]:
        """
        Computes the mean representation (embedding) for a protein sequence using ESM.
        
        Args:
            sequence (str): Amino acid sequence (e.g., "MKTVRQ...").
            
        Returns:
            list[float]: The mean embedding vector (size 320 for esm2_t6_8M).
        """
        self._load_model()
        
        # ESM tokenizer expects standard amino acids.
        inputs = self.tokenizer(sequence, return_tensors="pt").to(self._device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            # last_hidden_state shape: (batch_size, sequence_length, hidden_size)
            # sequence_length includes [CLS] and [EOS] tokens.
            last_hidden_state = outputs.last_hidden_state[0]
            
            # Exclude the [CLS] (first) and [EOS] (last) tokens to get residue embeddings
            # The input sequence length is len(sequence), tensor is len(sequence)+2
            residue_embeddings = last_hidden_state[1:-1]
            
            # Compute mean over residues
            mean_embedding = torch.mean(residue_embeddings, dim=0)
            
        return mean_embedding.cpu().tolist()

# Singleton instance
_esm_skills = ESMSkills()

def get_embedding(sequence: str) -> list[float]:
    """
    Public API to get protein embedding.
    """
    return _esm_skills.get_embedding(sequence)
