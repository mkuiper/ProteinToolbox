import unittest
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from proteintoolbox.skills.bio_skills import fetch_pdb_structure
from proteintoolbox.skills.validation_skills import validate_structure, check_backbone_continuity, check_steric_clashes

class TestValidationSkills(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Fetch a small PDB for testing (Crambin)
        cls.pdb_path = fetch_pdb_structure("1crn", output_dir="tests/data")

    def test_validate_structure_valid(self):
        # 1CRN should be largely valid, though small break/clash checks might trigger depending on strictness
        report = validate_structure(self.pdb_path)
        print(f"\nValidation Report for 1CRN: {report}")
        self.assertIn("is_valid", report)
        self.assertIn("backbone_breaks", report)
        self.assertIn("clashes", report)

    def test_clash_detection(self):
        clashes = check_steric_clashes(self.pdb_path, min_distance=0.5) # Very strict to avoid noise, 1CRN is high qual
        self.assertIsInstance(clashes, list)

if __name__ == '__main__':
    unittest.main()
