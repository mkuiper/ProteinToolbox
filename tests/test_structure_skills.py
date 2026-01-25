import unittest
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from proteintoolbox.skills.bio_skills import fetch_pdb_structure
from proteintoolbox.skills.structure_skills import calculate_sasa, identify_surface_residues

class TestStructureSkills(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Fetch a small PDB for testing (Crambin)
        cls.pdb_path = fetch_pdb_structure("1crn", output_dir="tests/data")

    def test_calculate_sasa(self):
        sasa = calculate_sasa(self.pdb_path)
        self.assertIn("total", sasa)
        self.assertIn("polar", sasa)
        self.assertIn("apolar", sasa)
        self.assertGreater(sasa["total"], 0)
        print(f"SASA for 1CRN: {sasa}")

    def test_surface_residues(self):
        surface_res = identify_surface_residues(self.pdb_path)
        self.assertIsInstance(surface_res, list)
        self.assertGreater(len(surface_res), 0)
        print(f"Surface residues (first 5): {surface_res[:5]}")

if __name__ == '__main__':
    unittest.main()
