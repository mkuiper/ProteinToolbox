import os
import subprocess
import shutil

class DesignSkills:
    def __init__(self):
        self.rfdiffusion_path = os.getenv("RFDIFFUSION_PATH")
        self.proteinmpnn_path = os.getenv("PROTEINMPNN_PATH")

    def generate_backbone(self, prompt: str, output_dir: str = "output/rfdiffusion", dry_run: bool = False) -> str:
        """
        Generates a protein backbone using RFdiffusion.
        
        Args:
            prompt (str): Description of the design task (e.g., "binder_design").
                          In a real impl, this would be parsed into contigs/hotspots.
            output_dir (str): Where to save results.
            dry_run (str): Return command instead of running.

        Returns:
            str: Path to generated PDB or status message.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Simplified command construction
        cmd = [
            "python", 
            f"{self.rfdiffusion_path}/scripts/run_inference.py",
            f"--output_prefix={output_dir}/design",
            "--num_designs=1"
        ]
        
        # This is a simplified logic. Real prompt parsing is complex.
        if "binder" in prompt:
            cmd.append("--contigmap_contigs=[...]") 

        if dry_run or not self.rfdiffusion_path:
            return f"Dry Run / Not Installed: Command would be: {' '.join(cmd)}"
        
        try:
            subprocess.run(cmd, check=True)
            return f"Backbone generated at {output_dir}/design_0.pdb"
        except subprocess.CalledProcessError as e:
            return f"Error running RFdiffusion: {e}"

    def design_sequence(self, pdb_path: str, output_dir: str = "output/mpnn", dry_run: bool = False) -> str:
        """
        Designs a sequence for a fixed backbone using ProteinMPNN.

        Args:
            pdb_path (str): Input PDB file.
            output_dir (str): Output directory.

        Returns:
            str: Path to FASTA file or status.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        cmd = [
            "python",
            f"{self.proteinmpnn_path}/protein_mpnn_run.py",
            "--pdb_path_chains", pdb_path,
            "--out_folder", output_dir
        ]

        if dry_run or not self.proteinmpnn_path:
            return f"Dry Run / Not Installed: Command would be: {' '.join(cmd)}"

        try:
            subprocess.run(cmd, check=True)
            return f"Sequences designed at {output_dir}/seqs_0.fa"
        except subprocess.CalledProcessError as e:
            return f"Error running ProteinMPNN: {e}"

# Standalone functions for export
_skills = DesignSkills()

def generate_backbone(prompt: str, output_dir: str = "output/rfdiffusion") -> str:
    return _skills.generate_backbone(prompt, output_dir)

def design_sequence(pdb_path: str, output_dir: str = "output/mpnn") -> str:
    return _skills.design_sequence(pdb_path, output_dir)
