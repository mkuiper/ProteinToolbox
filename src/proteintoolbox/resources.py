import torch
import shutil

class ResourceManager:
    def __init__(self):
        self.gpu_available = torch.cuda.is_available()
        self.gpu_count = torch.cuda.device_count() if self.gpu_available else 0
        self.gpu_name = torch.cuda.get_device_name(0) if self.gpu_available else "None"

    def get_status(self):
        return {
            "gpu_available": self.gpu_available,
            "gpu_count": self.gpu_count,
            "gpu_name": self.gpu_name,
            "cuda_version": torch.version.cuda if self.gpu_available else None
        }

    def check_tool_requirements(self, tool_name: str) -> bool:
        # Simple heuristic: AI tools usually need GPU
        ai_tools = ["rfdiffusion", "proteinmpnn", "boltz-2", "abx", "biophi"]
        if tool_name.lower() in ai_tools:
            if not self.gpu_available:
                print(f"Warning: {tool_name} is recommended to run on GPU, but none detected.")
                return False # Or return True with warning depending on strictness
        return True
