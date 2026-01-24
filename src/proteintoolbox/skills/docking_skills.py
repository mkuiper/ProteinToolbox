import os
from vina import Vina
from meeko import MoleculePreparation
from rdkit import Chem

def prepare_ligand(ligand_path: str, output_path: str = None) -> str:
    """
    Prepares a ligand (SDF/MOL2) for docking by converting to PDBQT using Meeko.
    
    Args:
        ligand_path: Path to input ligand file.
        output_path: Path to save PDBQT.
        
    Returns:
        Path to PDBQT file.
    """
    if not output_path:
        output_path = os.path.splitext(ligand_path)[0] + ".pdbqt"
        
    # Read molecule with RDKit (assumes SDF or Mol2)
    # Simple case: usually requires 3D coordinates generated beforehand
    if ligand_path.endswith(".sdf"):
        suppl = Chem.SDMolSupplier(ligand_path)
        mol = suppl[0]
    elif ligand_path.endswith(".mol2"):
        mol = Chem.MolFromMol2File(ligand_path)
    else:
        return "Error: Unsupported ligand format. Use SDF or MOL2."

    if not mol:
        return "Error: Could not read molecule."

    preparator = MoleculePreparation()
    preparator.prepare(mol)
    pdbqt_string = preparator.write_pdbqt_string()
    
    with open(output_path, 'w') as f:
        f.write(pdbqt_string)
        
    return output_path

def run_docking(receptor_pdbqt: str, ligand_pdbqt: str, center: list, size: list = [20, 20, 20], output_path: str = "docked.pdbqt") -> str:
    """
    Runs AutoDock Vina.
    
    Args:
        receptor_pdbqt: Prepared receptor.
        ligand_pdbqt: Prepared ligand.
        center: [x, y, z] coordinates of box center.
        size: [x, y, z] size of box (Angstroms).
        output_path: Output file.
        
    Returns:
        Status string.
    """
    v = Vina(sf_name='vina')
    v.set_receptor(receptor_pdbqt)
    v.set_ligand_from_file(ligand_pdbqt)
    
    v.compute_vina_maps(center=center, box_size=size)
    
    # Dock
    v.dock(exhaustiveness=8, n_poses=5)
    v.write_poses(output_path, n_poses=5, overwrite=True)
    
    return f"Docking complete. Saved to {output_path}"
