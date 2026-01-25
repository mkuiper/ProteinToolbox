import unittest
from proteintoolbox.skills import design_skills, analysis_skills

class TestDesignAnalysis(unittest.TestCase):
    def test_alanine_scan(self):
        seq = "MKT" # Met-Lys-Thr
        # M1A, K2A, T3A
        variants = design_skills.generate_alanine_scan(seq)
        
        self.assertEqual(len(variants), 3)
        self.assertIn("M1A", variants)
        self.assertEqual(variants["M1A"], "AKT")
        
        seq_with_a = "MAK"
        # M1A, A2A(skip), K3A
        variants_a = design_skills.generate_alanine_scan(seq_with_a)
        self.assertEqual(len(variants_a), 2)
        self.assertNotIn("A2A", variants_a)

    def test_saturation_library(self):
        seq = "MK"
        # Pos 1: M -> 19 others
        variants = design_skills.generate_saturation_library(seq, 1)
        self.assertEqual(len(variants), 19)
        self.assertNotIn("M1M", variants)
        self.assertIn("M1A", variants)
        
        # Check out of bounds
        with self.assertRaises(ValueError):
            design_skills.generate_saturation_library(seq, 3)

    def test_analysis(self):
        seq = "MKT"
        props = analysis_skills.analyze_sequence(seq)
        self.assertIn("molecular_weight", props)
        self.assertIn("isoelectric_point", props)
        self.assertIn("instability_index", props)
        
        # BioPython calculates these deterministicly
        self.assertGreater(props["molecular_weight"], 0)

    def test_composition(self):
        seq = "AA"
        comp = analysis_skills.get_amino_acid_percentages(seq)
        self.assertAlmostEqual(comp['A'], 1.0)
        self.assertAlmostEqual(comp['C'], 0.0)

if __name__ == '__main__':
    unittest.main()
