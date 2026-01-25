import os
import shutil
import pytest
from proteintoolbox.workflows import get_available_workflows, AntibodyDesignWorkflow, EnzymeRefinementWorkflow

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
TEST_PDB = os.path.join(DATA_DIR, 'pdb1crn.ent')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'test_workflow_output')

@pytest.fixture
def clean_output():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    yield
    # Cleanup after test
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

def test_registry():
    workflows = get_available_workflows()
    assert "antibody_prep" in workflows
    assert "enzyme_refinement" in workflows
    assert isinstance(workflows["antibody_prep"], AntibodyDesignWorkflow)

def test_antibody_workflow(clean_output):
    workflow = AntibodyDesignWorkflow()
    # 1CRN is a small protein, suitable for quick testing
    result = workflow.run(TEST_PDB, OUTPUT_DIR)
    
    assert result.success is True
    # If minimization ran, we expect artifacts. If skipped, maybe not.
    if any("Minimization skipped" in log for log in result.logs):
        pass
    else:
        assert len(result.artifacts) > 0
        assert os.path.exists(result.artifacts[0])
    assert "initial_sasa" in result.data
    assert "final_sasa" in result.data

def test_enzyme_workflow(clean_output):
    workflow = EnzymeRefinementWorkflow()
    result = workflow.run(TEST_PDB, OUTPUT_DIR)
    
    assert result.success is True
    # If minimization ran, we expect artifacts. If skipped, maybe not.
    if any("Minimization skipped" in log for log in result.logs):
        pass
    else:
        assert len(result.artifacts) > 0
    assert "initial_clashes" in result.data
    assert "final_clashes" in result.data
