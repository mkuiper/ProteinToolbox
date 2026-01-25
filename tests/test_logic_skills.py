import unittest
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from proteintoolbox.skills import logic_skills

class TestLogicSkills(unittest.TestCase):
    def test_check_design_constraints_pass(self):
        # A simple sequence (Insulin A chain roughly)
        seq = "GIVEQCCTSICSLYQLENYCN"
        constraints = {
            "max_molecular_weight": 5000,
            "min_instability_index": 0
        }
        result = logic_skills.check_design_constraints(seq, constraints)
        self.assertTrue(result['pass'])
        self.assertEqual(len(result['violations']), 0)

    def test_check_design_constraints_fail(self):
        # Very long hydrophobic sequence
        seq = "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV" 
        constraints = {
            "solubility_preference": "hydrophilic"
        }
        result = logic_skills.check_design_constraints(seq, constraints)
        self.assertFalse(result['pass'])
        self.assertIn("GRAVY", result['violations'][0])

    def test_infer_functionality_issues(self):
        # Short sequence
        short_seq = "ACDEF"
        issues = logic_skills.infer_functionality_issues(short_seq)
        self.assertTrue(any("Length Warning" in i for i in issues))

        # Odd Cysteines
        cys_seq = "ACCC"
        issues = logic_skills.infer_functionality_issues(cys_seq)
        self.assertTrue(any("Cysteine Warning" in i for i in issues))

    def test_get_reasoning_template(self):
        template = logic_skills.get_reasoning_template('scientific_method')
        self.assertIn("Hypothesis", template)
        
        template_fail = logic_skills.get_reasoning_template('magic_wand')
        self.assertIn("Unknown strategy", template_fail)

    def test_decompose_request(self):
        # Design request
        req = "Design a stable binder for EGFR"
        decomp = logic_skills.decompose_request(req)
        self.assertEqual(decomp['intent'], 'design')
        self.assertIn('min_instability_index', decomp['inferred_constraints'])
        self.assertIn('generate_sequences', decomp['implied_steps'])

        # Analysis request
        req2 = "Analyze the properties of this PDB"
        decomp2 = logic_skills.decompose_request(req2)
        self.assertEqual(decomp2['intent'], 'analysis')
        self.assertIn('calculate_properties', decomp2['implied_steps'])

if __name__ == '__main__':
    unittest.main()
