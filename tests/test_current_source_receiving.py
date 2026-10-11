import sys,unittest,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from plan_current_source_receiving import plan
from open_prototype_source_group import check_path
class SourceReceivingTests(unittest.TestCase):
    def test_complete_tangent_continuity_before_native_scene(self):
        p=plan()
        for n,r in {**p['routes'],**p['factory_routes']}.items():
            with self.subTest(wire=n):check_path(r['parts'],min_radius=25.2 if n in p['routes'] else 6)
    def test_whole_current_station_and_short_prefuse(self):
        p=plan();self.assertEqual(5,len(p['P_SYS']['ports']))
        self.assertEqual('W043 F_PI.in',p['P_SYS']['roles']['5'])
        self.assertEqual('W066 S0.out',p['P_SYS']['roles']['1'])
        self.assertLessEqual(p['F_PI']['input_factory_blank_mm'],50)
        self.assertLess(math.dist(p['factory_routes']['W043']['parts'][-1]['end'],p['P_SYS']['ports']['5']),1e-6)
    def test_separate_ring_columns_and_no_completion_claim(self):
        p=plan();self.assertEqual({'W067','W068'},set(p['routes']))
        self.assertFalse(p['selected'] or p['W5_complete'] or p['physical_pass'])
        self.assertEqual(3,p['routes']['W068']['parts'][-1]['length_mm'])
        for n,r in p['routes'].items():
            self.assertIsNone(r['actual_crimp_strip_mm'])
            self.assertTrue(all(math.dist(a['end'],b['start'])<1e-6 for a,b in zip(r['parts'],r['parts'][1:])))
            self.assertLess(math.dist(r['parts'][-1]['end'],p['rings'][n]['point_mm']),1e-6)
if __name__=='__main__':unittest.main()
