import os
try:
    import openmm as mm
    from openmm import app, unit
except ImportError:
    mm = None

def run_minimization(pdb_path: str, output_path: str = "minimized.pdb"):
    """
    Runs a simple energy minimization on a PDB structure using OpenMM.

    Args:
        pdb_path (str): Path to input PDB.
        output_path (str): Path to save minimized structure.
    """
    if not mm:
        return "Error: OpenMM not installed."

    pdb = app.PDBFile(pdb_path)
    forcefield = app.ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
    
    # Add Hydrogens
    modeller = app.Modeller(pdb.topology, pdb.positions)
    modeller.addHydrogens(forcefield)
    
    # Create system (implicit solvent for speed in this demo skill)
    system = forcefield.createSystem(modeller.topology, nonbondedMethod=app.NoCutoff, constraints=app.HBonds)
    integrator = mm.LangevinMiddleIntegrator(300*unit.kelvin, 1/unit.picosecond, 0.004*unit.picoseconds)
    simulation = app.Simulation(modeller.topology, system, integrator)
    simulation.context.setPositions(modeller.positions)
    
    print("Minimizing energy...")
    simulation.minimizeEnergy()
    
    with open(output_path, 'w') as f:
        app.PDBFile.writeFile(simulation.topology, simulation.context.getState(getPositions=True).getPositions(), f)
    
    return f"Minimization complete. Saved to {output_path}"
