import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from plan_current_body_harness import plan

class BodyHarnessPlanTests(unittest.TestCase):
    def test_complete_fixed_denominator_not_a_route_acceptance(self):
        p=plan()
        self.assertEqual(80,len(p['body_conductors']))
        self.assertEqual(160,p['body_end_count'])
        self.assertEqual(12,len(p['leg_looms']))
        self.assertFalse(p['selected'] or p['physical_pass'] or p['W5_complete'])
        self.assertTrue(all(len(r['ends'])==2 for r in p['body_conductors']))
    def test_source_rail_no_double_occupation(self):
        p=plan();r=next(r for r in p['body_conductors'] if r['id']=='W065')
        self.assertEqual('P_REAR.5',r['a'])
        self.assertEqual('XA01',p['fixed_ports']['P_REAR.1']['wire'])
        self.assertEqual('XP01',p['fixed_ports']['P_REAR.4']['wire'])
    def test_aliases_and_legacy_stock_not_extra_wires(self):
        p=plan();owners=p['internal_boundary_owners']
        self.assertEqual(['W_FL_G.1','W_G1.3'],owners['W025']['graph_aliases'])
        self.assertNotIn('W_FL_G.1',owners)
        self.assertFalse(p['legacy_source_scope']['current_length_stock_complete'])
        self.assertEqual(['W064','W065','W067','W068'],p['legacy_source_scope']['wires'])

if __name__=='__main__':unittest.main()
