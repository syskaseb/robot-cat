import unittest
from w5_four_ground_returns_plan import plan,provisional_blank,RADIUS
from w5_rounded_path import corner_offsets


class FourGroundReturns(unittest.TestCase):
    def test_current_four_nets_not_w061_duplicate(self):
        rows=plan()
        self.assertEqual([r['wire'] for r in rows],['W025','W036','W062','W063'])
        self.assertEqual(rows[3]['leg_entry_mm'][0],75)
        self.assertTrue(all(not r['selected'] and not r['geometry_checked'] for r in rows))

    def test_real_radius_and_middle_tangents(self):
        for r in plan():
            cuts,units=corner_offsets(r['middle_mm'],RADIUS)
            self.assertEqual(units[0],[0,1,0])
            self.assertEqual(units[-1],[0,-r['leg_side'],0])
            self.assertAlmostEqual(r['middle_mm'][0][2],155.5)
            self.assertAlmostEqual(r['middle_mm'][-1][2],155.5)
            self.assertEqual(cuts[0],0)
            self.assertEqual(cuts[-1],0)

    def test_blank_has_actual_two_family_strip_allowances(self):
        self.assertEqual(provisional_blank(201),260)
        self.assertEqual(provisional_blank(205),260)
        self.assertEqual(provisional_blank(203,'415'),260)


if __name__=='__main__':unittest.main()
