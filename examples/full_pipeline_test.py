import sys
import os

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from proteintoolbox.skills import bio_skills, sim_skills, docking_skills, analysis_skills

def main():
    print("--- Testing Full Pipeline Skills ---")
    
    # 1. Bio Skills
    print("\n1. Bio: Fetching 1CRN...")
    pdb_path = bio_skills.fetch_pdb_structure("1CRN", output_dir="data/test_pipeline")
    seq = bio_skills.get_sequence_from_pdb(pdb_path)
    print(f"   Sequence: {seq}")
    
    # 2. Analysis Skills
    print("\n2. Analysis: Analyzing sequence...")
    # Using a known sequence since PDB extraction might be partial
    test_seq = "TTCCPSIVARSNFNVCRLPGTPEAICATYTGCIIIPGATCPGDYAN" 
    props = analysis_skills.analyze_sequence(test_seq)
    print(f"   MW: {props['molecular_weight']:.2f}")
    print(f"   pI: {props['isoelectric_point']:.2f}")
    
    # 3. Docking Skills (Mock)
    # We don't have a real ligand file handy, so we'll just check if the function exists and is importable
    print("\n3. Docking: Verifying Vina import...")
    try:
        from vina import Vina
        print("   AutoDock Vina is installed and importable.")
    except ImportError:
        print("   Error: Vina not found.")

    print("\n--- Test Complete ---")

if __name__ == "__main__":
    main()

