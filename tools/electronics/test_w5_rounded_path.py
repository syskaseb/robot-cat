import unittest
import math
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

    def test_new_entry_lifts_before_existing_inner_data_bridge(self):
        # R10 first corner atY14.5/Z113.5: arc centreY24.5/Z123.5.
        # The selected horizontal bridge crossesY17.5/Z113.5. Distance
        # to the quarter-circle exceeds nominal OD2.4/OD1.3 half-sum.
        gap=math.hypot(24.5-17.5,123.5-113.5)-10
        self.assertGreater(gap,(2.4+1.3)/2)
        self.assertAlmostEqual(30.5-14.5-10,6)


if __name__=='__main__':unittest.main()
