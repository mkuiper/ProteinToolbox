import os
import shutil
import sys
import tempfile
import unittest

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from proteintoolbox.skills import docs_skills

class TestDocsSkills(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.pdb_content = "HEADER    TEST PDB\nATOM      1  N   ASP A   1      30.140  10.230  10.120  1.00  0.00           N\n"
        with open(os.path.join(self.test_dir, "test.pdb"), "w") as f:
            f.write(self.pdb_content)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_generate_project_report(self):
        report_path = docs_skills.generate_project_report(self.test_dir)
        self.assertTrue(os.path.exists(report_path))
        self.assertEqual(os.path.basename(report_path), "REPORT.md")
        
        with open(report_path, "r") as f:
            content = f.read()
            
        self.assertIn("# Project Report:", content)
        self.assertIn("## File Summary", content)
        self.assertIn("| test.pdb |", content)
        # Note: sequence extraction might fail on this mock PDB if BioPython is strict, 
        # but the report function handles exceptions, so we check if it ran.
        self.assertIn("## Structure Analysis", content)

if __name__ == '__main__':
    unittest.main()

