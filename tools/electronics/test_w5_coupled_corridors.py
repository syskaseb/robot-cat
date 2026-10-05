"""Cheap whole-scope invariants; these do not qualify physical routing."""
import unittest
import math
import w5_coupled_corridors_r2 as candidate


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.bodies,self.rows,self.preserved,_=candidate.contract()

    def test_whole49_once(self):
        self.assertEqual(len(self.rows),34)
        self.assertEqual(len(set(self.preserved)|{r['wire'] for r in self.rows}),49)
        self.assertFalse(set(self.preserved)&{r['wire'] for r in self.rows})

    def test_all19_connected_data_cages_once_and_one_nc(self):
        cages=[r[s+'_end'] for r in self.rows for s in ('a','b') if r[s+'_end'].startswith('D_')]
        self.assertEqual(len(cages),19)
        physical={f'D_{leg}.{n}' for leg in ('FL','FR','RL','RR') for n in range(1,6)}
        self.assertEqual(physical-set(cages),{'D_RL.5'})
        self.assertEqual(len(set(cages)),19)

    def test_backbone_not_forgotten(self):
        self.assertTrue({'W002','W007','W011','W012'}<={r['wire'] for r in self.rows})

    def test_derived_row_clearance(self):
        self.assertAlmostEqual(self.bodies['D_FR'][4],-23)
        self.assertAlmostEqual(-20.3-self.bodies['D_FR'][4],2.7)
        self.assertEqual(self.bodies['D_FR'][2:3],[175])

    def test_all_routes_have_analytical_candidates(self):
        for r in self.rows:
            with self.subTest(wire=r['wire']):
                choices=list(candidate.base.variants(r))
                self.assertTrue(choices)
                self.assertTrue(all(c['radius_mm']==r['radius_mm'] for c in choices))

    def test_bus_keeps_source_datum(self):
        r=next(r for r in self.rows if r['wire']=='W002')
        for c in candidate.base.variants(r):
            self.assertEqual(c['middle'][0],r['target'])
            self.assertEqual(c['middle'][-1],c['a']['tip'])


class LengthTests(unittest.TestCase):
    def test_quarter_circle_fillet(self):
        from w5_path_length import rounded_length
        self.assertAlmostEqual(rounded_length([[0,0,0],[30,0,0],[30,30,0]],10),40+5*math.pi)

    def test_spatial_right_angle_is_same_length(self):
        from w5_path_length import rounded_length
        self.assertAlmostEqual(rounded_length([[0,0,0],[0,0,30],[0,30,30]],10),40+5*math.pi)

    def test_impossible_corners_remain_invalid(self):
        from w5_path_length import rounded_length
        with self.assertRaises(AssertionError):rounded_length([[0,0,0],[5,0,0],[5,5,0]],10)


class NorthContractTests(unittest.TestCase):
    def test_sources_and_bridge_are_reopened_together(self):
        import w5_coupled_corridors_r4 as north
        bodies,rows,preserved,_=north.contract()
        self.assertEqual(len(rows),36)
        self.assertEqual(len(preserved),12)
        self.assertEqual(len({r['wire'] for r in rows}|set(preserved)|{'W061'}),49)
        self.assertTrue({'W001','W003'}<={r['wire'] for r in rows})
        self.assertFalse({'W001','W003','W061'}&set(preserved))
        self.assertAlmostEqual(bodies['G2'][0]-bodies['G1'][3],49.5)


if __name__=='__main__':unittest.main()
