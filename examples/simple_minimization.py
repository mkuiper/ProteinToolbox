import sys
import os

# Ensure we can import from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from proteintoolbox.skills import bio_skills, sim_skills

def main():
    print("Test: Fetching PDB 1CRN...")
    pdb_path = bio_skills.fetch_pdb_structure("1CRN", output_dir="data/test_pdb")
    print(f"Downloaded to: {pdb_path}")

    print("Test: Minimizing structure...")
    result = sim_skills.run_minimization(pdb_path, output_path="data/test_pdb/1crn_minimized.pdb")
    print(result)

if __name__ == "__main__":
    main()
