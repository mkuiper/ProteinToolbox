from Bio.PDB import PDBList
import Bio.PDB.PDBList as PDBListModule

print(f"PDBList is: {PDBList}")
print(f"Type of PDBList: {type(PDBList)}")
print(f"Has retrieve_pdb_file? {hasattr(PDBList, 'retrieve_pdb_file')}")
print(f"Bio.PDB.PDBList module: {PDBListModule}")
print(f"Class inside module: {PDBListModule.PDBList}")
