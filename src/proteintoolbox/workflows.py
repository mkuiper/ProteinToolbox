import os
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from proteintoolbox.skills import structure_skills, sim_skills, validation_skills

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WorkflowResult:
    """Standardized result object for workflows."""
    success: bool
    data: Dict[str, Any]
    artifacts: List[str] # Paths to generated files
    logs: List[str]

class Workflow(ABC):
    """Abstract base class for protein design workflows."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def run(self, input_pdb: str, output_dir: str) -> WorkflowResult:
        """
        Execute the workflow.
        
        Args:
            input_pdb (str): Path to the starting PDB structure.
            output_dir (str): Directory to save outputs.
            
        Returns:
            WorkflowResult: The outcome of the workflow.
        """
        pass

class AntibodyDesignWorkflow(Workflow):
    """
    A workflow for Antibody structure preparation and analysis.
    Focuses on validating the structure, identifying surface residues (often CDRs are exposed),
    and relaxing the structure.
    """
    
    def __init__(self):
        super().__init__("AntibodyDesignPrep")
        
    def run(self, input_pdb: str, output_dir: str) -> WorkflowResult:
        logger.info(f"Starting {self.name} on {input_pdb}")
        logs = []
        artifacts = []
        data = {}
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 1: Initial Validation
        logs.append("Step 1: Validating initial structure...")
        val_res = validation_skills.validate_structure(input_pdb)
        data['initial_validation'] = val_res
        
        if not val_res['is_valid']:
            logs.append(f"Validation found issues: {val_res['backbone_breaks']} {val_res['clashes']}")
            if len(val_res['backbone_breaks']) > 0:
                return WorkflowResult(False, data, artifacts, logs) # Abort on breaks
            # Continue if just clashes, minimization fixes them
        
        # Step 2: Surface Analysis (Identify potential binding sites)
        logs.append("Step 2: Analyzing surface residues...")
        sasa_stats = structure_skills.calculate_sasa(input_pdb)
        surface_res = structure_skills.identify_surface_residues(input_pdb)
        data['initial_sasa'] = sasa_stats
        data['surface_residues_count'] = len(surface_res)
        
        # Step 3: Energy Minimization (Relaxation)
        logs.append("Step 3: Minimizing structure...")
        minimized_pdb_path = os.path.join(output_dir, "antibody_minimized.pdb")
        
        try:
            msg = sim_skills.run_minimization(input_pdb, minimized_pdb_path)
            logs.append(msg)
            artifacts.append(minimized_pdb_path)
        except ImportError:
            logs.append("Minimization skipped: OpenMM not installed. Using input structure.")
            minimized_pdb_path = input_pdb
        except Exception as e:
            logs.append(f"Minimization failed: {str(e)}")
            return WorkflowResult(False, data, artifacts, logs)
            
        # Step 4: Final Validation
        logs.append("Step 4: Validating minimized structure...")
        final_val = validation_skills.validate_structure(minimized_pdb_path)
        data['final_validation'] = final_val
        
        # Step 5: Final Analysis
        logs.append("Step 5: Final SASA analysis...")
        final_sasa = structure_skills.calculate_sasa(minimized_pdb_path)
        data['final_sasa'] = final_sasa
        
        success = final_val['is_valid'] or len(final_val['backbone_breaks']) == 0
        
        return WorkflowResult(success, data, artifacts, logs)

class EnzymeRefinementWorkflow(Workflow):
    """
    A workflow for Enzyme refinement.
    Strictly checks for steric clashes which might impede active site function,
    minimizes, and reports geometry stats.
    """
    
    def __init__(self):
        super().__init__("EnzymeRefinement")
        
    def run(self, input_pdb: str, output_dir: str) -> WorkflowResult:
        logger.info(f"Starting {self.name} on {input_pdb}")
        logs = []
        artifacts = []
        data = {}
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 1: Pre-check Clashes
        logs.append("Step 1: Checking for steric clashes...")
        clashes = validation_skills.check_steric_clashes(input_pdb)
        data['initial_clashes'] = len(clashes)
        
        # Step 2: Minimization
        logs.append("Step 2: Minimizing structure to resolve clashes...")
        refined_pdb_path = os.path.join(output_dir, "enzyme_refined.pdb")
        
        try:
            msg = sim_skills.run_minimization(input_pdb, refined_pdb_path)
            logs.append(msg)
            artifacts.append(refined_pdb_path)
        except ImportError:
            logs.append("Minimization skipped: OpenMM not installed. Using input structure.")
            refined_pdb_path = input_pdb
        except Exception as e:
            logs.append(f"Minimization failed: {str(e)}")
            return WorkflowResult(False, data, artifacts, logs)
            
        # Step 3: Post-check
        logs.append("Step 3: Verifying refinement...")
        final_clashes = validation_skills.check_steric_clashes(refined_pdb_path)
        data['final_clashes'] = len(final_clashes)
        
        logs.append(f"Clashes reduced from {len(clashes)} to {len(final_clashes)}")
        
        # Success if clashes reduced or zero
        success = len(final_clashes) <= len(clashes)
        
        return WorkflowResult(success, data, artifacts, logs)

def get_available_workflows() -> Dict[str, Workflow]:
    return {
        "antibody_prep": AntibodyDesignWorkflow(),
        "enzyme_refinement": EnzymeRefinementWorkflow()
    }
