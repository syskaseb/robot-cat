import unittest
from plan_remaining_source_retention import land


class SourceLands(unittest.TestCase):
    def test_short_insulated_custom_land_starts_after_sleeve(self):
        p=[dict(kind='line',start=[19,80.589,88.9],end=[19,63.589,88.9],length_mm=17)]
        q=land(p,0,3,14)
        self.assertAlmostEqual(q['centre_world_mm'][1],65.089)
        self.assertLessEqual(q['centre_world_mm'][1]+1.5,66.589+1e-8)

    def test_no_fictitious_long_land(self):
        p=[dict(kind='line',start=[0,0,0],end=[0,0,3],length_mm=3)]
        with self.assertRaises(AssertionError):land(p,0,9)
        self.assertEqual(land(p,0,3)['centre_world_mm'],[0,0,1.5])


if __name__=='__main__':unittest.main()
