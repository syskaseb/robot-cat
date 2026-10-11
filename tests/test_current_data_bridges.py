import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/cad'))
from plan_current_data_bridges import plan,rise
from open_prototype_source_group import check_path

class DataBridges(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=plan()
    def test_three_whole_bridges_with_supplier_static_radius(self):
        self.assertEqual(set(self.p['routes']),{'W007','W011','W012'})
        for n,r in self.p['routes'].items():
            check_path(r['parts'],min_radius=5.2)
            self.assertEqual(r['radius_mm'],.65)
            self.assertEqual(r['strip_mm'],[11,11]);self.assertIsNone(r['actual_cut_mm'])
    def test_no_known_power_crossings_or_completion_claim(self):
        self.assertFalse(self.p['rejected']);self.assertFalse(self.p['selected'])
        self.assertFalse(self.p['W5_complete']);self.assertFalse(self.p['physical_pass'])
    def test_outward_fan_preserves_all_five_mouths_without_crossed_stems(self):
        q=[rise([135.5+4.75*i,-80,79.5],'D_RR.'+str(i+1)) for i in range(5)]
        for a,b in zip(q,q[1:]):
            self.assertEqual(a[0]['length_mm'],9);self.assertEqual(b[0]['length_mm'],9)
            self.assertAlmostEqual(b[-1]['end'][0]-a[-1]['end'][0],4.75)
        self.assertTrue(all(abs(v[-1]['end'][1]+94)<1e-6 for v in q))
    def test_rear_bridge_uses_previously_free_same_rail_port(self):
        self.assertEqual(self.p['routes']['W012']['endpoints'],['D_RL.5','D_RR.5'])
        self.assertEqual(self.p['physical_port_reassignment']['D_RL']['current_NC_port'],'1')

if __name__=='__main__':unittest.main()
