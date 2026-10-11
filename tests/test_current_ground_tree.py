import json,math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/cad'))
from plan_current_ground_tree import plan,OUT
from open_prototype_source_group import check_path

class GroundTree(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=plan()
    def test_all_seven_complete_returns_and_unique_ground_ports(self):
        self.assertEqual(set(self.p['routes']),{'W001','W025','W036','W060','W061','W062','W063'})
        self.assertEqual(set(self.p['G1_same_ground_port_mapping'].values()),set(range(1,6)))
        for n,r in self.p['routes'].items():
            check_path(r['parts'],min_radius=12.4 if n=='W001' else 11.1 if n=='W060' else 21,
              start=r['parts'][0]['start'],end=r['parts'][-1]['end'])
            self.assertIsNone(r['actual_cut_mm'])
    def test_main_free_wire_budget_includes_bare_and_rail_strip(self):
        r=self.p['routes']['W060'];bare=self.p['retained_MAIN_bare_parts']['W060']
        self.assertLessEqual(r['guide_mm']+sum(s['length_mm'] for s in bare)+14,300)
        self.assertEqual(r['parts'][-1]['end'],bare[-1]['end'])
    def test_no_width_growth_and_no_partial_selection(self):
        b=self.p['G1']['casing_mm'];self.assertGreaterEqual(b[1],-100);self.assertLessEqual(b[4],100)
        self.assertFalse(self.p['selected']);self.assertFalse(self.p['W5_complete']);self.assertFalse(self.p['physical_pass'])
    def test_concentric_pair_and_downstream_grip_lands(self):
        for n in ('W025','W061'):
            q=self.p['routes'][n]['parts']
            self.assertTrue(any(s['kind']=='line' and s['length_mm']>=9 and abs(s['start'][0]-s['end'][0])<1e-6
              and abs(s['start'][1]-s['end'][1])<1e-6 for s in q))
        self.assertEqual(self.p['rear_ground_same_rail_mapping']['1'],4)

if __name__=='__main__':unittest.main()
