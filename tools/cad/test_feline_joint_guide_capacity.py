import unittest
from check_feline_joint_guide_capacity import square_shelf


class Shelf(unittest.TestCase):
    def test_four_equal_jackets_have_explicit_disjoint_grid(self):
        s=square_shelf([1.,1.,1.,1.])
        self.assertEqual((s['columns'],s['rows']),(2,2))
        self.assertAlmostEqual(s['width_mm'],4.2)
        self.assertGreater(s['enclosing_radius_mm'],2.)

    def test_unequal_jackets_are_not_shrunk_to_mean_radius(self):
        self.assertAlmostEqual(square_shelf([1.,3.])['pitch_mm'],6.2)


if __name__=='__main__':unittest.main()
