import sys,unittest,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/cad'))
from plan_current_positive_source import plan
from plan_current_s0_in_extension import plan as in_plan
from open_prototype_source_group import check_path

class CurrentSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=plan();cls.i=in_plan()
    def test_intact_prefuse_and_original_factory_lead_limits(self):
        for n,limit in [('W075',50),('W076_FACTORY',84.5)]:
            r=self.p['routes'][n];self.assertLessEqual(r['nominal_blank_mm'],limit)
            self.assertIsNone(r['actual_cut_mm']);check_path(r['parts'],min_radius=10)
        self.assertEqual(self.p['routes']['W075']['endpoints'],['BAT.plus','F0.in'])
    def test_three_qualified_proposals_do_not_cross_known_guides(self):
        self.assertFalse([v for v in self.p['rejected'] if v['b'] in ('W075','W076_FACTORY','W066')])
        check_path(self.p['routes']['W066']['parts'],min_radius=25.2)
        self.assertLessEqual(max(v[k][1] for v in self.p['routes']['W066']['parts'] for k in ('start','end')),97.5)
    def test_whole_in_clocking_changes_terminal_not_qualified_neighbor(self):
        self.assertFalse(self.i['rejected']);self.assertEqual(self.i['source_change']['new_barrel_axis'],[-.5,math.sqrt(3)/2,0])
        self.assertEqual(self.i['source_change']['rotation_z_degrees'],180)
        self.assertAlmostEqual(self.i['source_change']['new_barrel_tip_mm'][0],-102.45)
        self.assertTrue(self.i['source_change']['same_net']);check_path(self.i['routes']['W076_EXTENSION']['parts'],min_radius=25.2)
    def test_unknown_s0_datums_and_no_completion_claim(self):
        self.assertFalse(self.i['source_change']['manufacturer_stud_datums_verified'])
        for p in (self.p,self.i):
            self.assertFalse(p['selected']);self.assertFalse(p['W5_complete']);self.assertFalse(p['physical_pass'])

if __name__=='__main__':unittest.main()
