import sys,unittest,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from plan_current_main_sources import plan,R
class MainSourcePlanTests(unittest.TestCase):
    def test_four_continuous_guides_and_complete_terminal_lands(self):
        p=plan();self.assertEqual({'W041_CUSTOM','W042_CUSTOM','W044_CUSTOM','W052_CUSTOM'},set(p['routes']))
        for n,r in p['routes'].items():
            q=r['parts'];self.assertGreaterEqual(q[0]['length_mm'],3 if n=='W041_CUSTOM' else 9);self.assertGreaterEqual(q[-1]['length_mm'],3 if n=='W044_CUSTOM' else 2.5 if n=='W052_CUSTOM' else 9)
            self.assertEqual([11,14],r['nominal_end_strip_mm'])
            self.assertTrue(all(math.dist(a['end'],b['start'])<1e-6 for a,b in zip(q,q[1:])),n)
            self.assertTrue(all(a['radius_mm']==R for a in q if a['kind']=='arc'))
    def test_one_relocated_rail_all_ports_and_no_point(self):
        p=plan();self.assertEqual(5,len(p['P_FRONT']['ports']))
        self.assertEqual('W064 S1.3',p['P_FRONT']['roles']['1'])
        self.assertFalse(p['selected'] or p['W5_complete'] or p['physical_pass'])
        self.assertEqual('P_REAR.3',p['candidate_port_remap']['W044']['candidate'])
        self.assertEqual([29,0,138],p['routes']['W044_CUSTOM']['parts'][-1]['end'])
        self.assertEqual([29,6.5,138],p['routes']['W052_CUSTOM']['parts'][-1]['end'])
if __name__=='__main__':unittest.main()
