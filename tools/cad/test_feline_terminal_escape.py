import math,unittest
from feline_terminal_escape import bound


class EscapeBound(unittest.TestCase):
    def test_every_quarter_clock_lies_in_the_bound(self):
        R=25.2
        for i in range(1,25):
            L=float(i);r=bound(R,L,0,2.1)
            theta=math.asin(L/R)
            self.assertAlmostEqual(r['maximum_transverse_excursion_mm'],R*(1-math.cos(theta)))
            for clock in range(12):
                a=clock*math.pi/6;d=r['maximum_transverse_excursion_mm']
                self.assertAlmostEqual(math.hypot(d*math.cos(a),d*math.sin(a)),d)

    def test_inside_post_rejects_all_clocks_not_only_a_tested_curve(self):
        r=bound(25.2,12.25,-4,2.1)
        self.assertTrue(r['no_admissible_clearance_path']);self.assertTrue(r['unavoidable_jacket_material_intersection'])

    def test_outside_material_does_not_get_called_impossible(self):
        self.assertFalse(bound(25.2,5,8,2.1)['no_admissible_clearance_path'])

    def test_does_not_extrapolate_past_quarter_limit(self):
        with self.assertRaises(AssertionError):bound(25.2,30,0,2.1)


if __name__=='__main__':unittest.main()
