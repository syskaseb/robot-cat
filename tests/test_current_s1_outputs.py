import sys,unittest,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from plan_current_s1_outputs import plan
class SwitchedOutputTests(unittest.TestCase):
    def test_current_rings_not_historical_endpoints(self):
        p=plan();self.assertAlmostEqual(123.7,p['rings']['W064']['point_mm'][0])
        self.assertAlmostEqual(63.623,p['rings']['W064']['point_mm'][1])
        self.assertAlmostEqual(7.377,p['rings']['W065']['point_mm'][1])
        self.assertEqual([29,-13,138],p['routes']['W065']['parts'][0]['start'])
        self.assertFalse(p['W5_complete'] or p['selected'] or p['physical_pass'])
    def test_full_continuous_wires_not_an_extra_920mm_stock_piece(self):
        for r in plan()['routes'].values():
            self.assertIsNone(r['actual_cut_mm'])
            self.assertEqual(14,r['rail_strip_mm'])
            self.assertTrue(all(math.dist(a['end'],b['start'])<1e-6 for a,b in zip(r['parts'],r['parts'][1:])))
if __name__=='__main__':unittest.main()
