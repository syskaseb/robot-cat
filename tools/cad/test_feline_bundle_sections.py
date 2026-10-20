import unittest
from feline_bundle_sections import certificate,triangle,square


class BundleSections(unittest.TestCase):
    def test_section_fit_does_not_override_inner_bend(self):
        a=certificate(square(2.1),[2.1]*4,[25.2]*4,6,28)
        self.assertLess(a['enclosing_radius_mm'],6)
        self.assertFalse(a['section_and_turn_fit'])

    def test_four_medium_low_bend_have_explicit_spacing(self):
        a=certificate(square(2.1),[2.1]*4,[12.4]*4,6,16)
        self.assertTrue(a['section_and_turn_fit'])
        self.assertAlmostEqual(a['minimum_jacket_gap_mm'],.2)

    def test_three_small_large_bend_fit_existing_tangent_class(self):
        a=certificate(triangle(1.55),[1.55]*3,[25.2]*3,3.5,28)
        self.assertTrue(a['section_and_turn_fit'])
        self.assertGreater(a['guaranteed_minimum_wire_bend_mm'],25.2)


if __name__=='__main__':unittest.main()
