import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from plan_current_harness_interfaces import plan

class CurrentHarnessInterfaces(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=plan();cls.rows={r['id']:r for r in cls.p['body_conductors']}
    def test_fixed_partition_no_partial_credit(self):
        self.assertEqual((self.p['body_count'],self.p['body_end_count'],self.p['qualified_nominal_guides']),(80,160,25))
        self.assertEqual(len(self.p['open_body_guides']),19)
        self.assertEqual(sum(len(l['electrical']) for l in self.p['looms']),36)
        self.assertFalse(self.p['W5_complete']);self.assertFalse(self.p['selected'])
    def test_current_ports_and_same_rail_remaps(self):
        self.assertEqual(self.rows['W043']['roles'],['F_PI.in','P_SYS.5'])
        for row in self.rows.values():
            for e in row['current_ends']:
                if e['role'].startswith(('D_','FL_G.','FR_G.','RL_G.','RR_G.','FL_P.','FR_P.','RL_P.','RR_P.')):
                    self.assertEqual(e['departure'],[0,0,1])
                if e['role'].startswith('G2.'):
                    self.assertEqual(e['departure'],[1,0,0]);self.assertAlmostEqual(e['point_mm'][2],155)
        self.assertEqual(self.p['occupied_body_ports']['P_REAR.3'],'W044')
        self.assertEqual(self.p['occupied_body_ports']['P_REAR.2'],'W052')
    def test_inverted_servo_membership_not_name(self):
        for l in self.p['looms']:
            expected=1 if l['stage']=='Hip' else 2
            self.assertEqual(len(l['crossed_axes']),expected)
            self.assertIsNone(l['cable_OD_mm']);self.assertIsNone(l['dynamic_min_radius_mm'])
    def test_unknown_bus_and_factory_boundary_not_invented(self):
        for wid in ('W002','W003'):
            e=next(e for e in self.rows[wid]['current_ends'] if e['role'].startswith('BUS.'))
            self.assertNotIn('point_mm',e)
        for wid in ('W026','W037','W045','W053','W041','W042','W044','W052'):
            self.assertGreater(self.rows[wid]['factory_segment']['guide_mm'],0)

if __name__=='__main__':unittest.main()
