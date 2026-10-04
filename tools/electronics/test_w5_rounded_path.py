import unittest
from w5_rounded_path import corner_offsets


class CornerConsumptionTests(unittest.TestCase):
    def test_first_segment_with_one_bend_may_be_shorter_than_two_radii(self):
        cuts,_=corner_offsets([[0,0,0],[12,0,0],[12,22.5,0],[50,22.5,0]],10)
        self.assertAlmostEqual(cuts[1],10)
        self.assertAlmostEqual(cuts[2],10)
        self.assertEqual(cuts[0],0)
        self.assertEqual(cuts[-1],0)

    def test_real_internal_overlap_is_rejected(self):
        with self.assertRaisesRegex(AssertionError,'overlap'):
            corner_offsets([[0,0,0],[12,0,0],[12,18,0],[50,18,0]],10)

    def test_oblique_offsets_and_reverse(self):
        cuts,_=corner_offsets([[0,0,0],[30,0,0],[60,30,0]],10)
        self.assertAlmostEqual(cuts[1],10*(2**.5-1))
        with self.assertRaisesRegex(AssertionError,'Reverse'):
            corner_offsets([[0,0,0],[30,0,0],[0,0,0]],10)


if __name__=='__main__':unittest.main()
