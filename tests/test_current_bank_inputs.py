import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from plan_current_bank_inputs import plan
from open_prototype_source_group import check_path
from open_prototype_path_preflight import samples

class BankInputTests(unittest.TestCase):
    def test_complete_twelve_unique_current_pairs(self):
        p=plan();self.assertEqual(12,len(p['routes']))
        ends=[e for r in p['routes'].values() for e in r['endpoints']]
        self.assertEqual(24,len(set(ends)))
        for r in p['routes'].values():
            check_path(r['parts'],min_radius=12.4)
            self.assertIsNone(r['actual_cut_mm'])
            for _,point in samples(r['parts']):self.assertLessEqual(abs(point[1])+1.55,100)
        self.assertFalse(p['selected'] or p['W5_complete'] or p['physical_pass'])
    def test_only_two_assessed_local_passages_not_whole_wing_cut(self):
        self.assertEqual([[-53,55],[-53,69]],[r['centre_xy_mm'] for r in plan()['required_foundation_passages']])
        removal=plan()['obsolete_side_attachment_removal']
        self.assertEqual('LowerCarrier001',removal['target'])
        for b in removal['cut_bounds_mm']:
            self.assertTrue(b[1]>=34.9 or b[4]<=-34.9)
            self.assertLess(b[3],134) # Preserve rear-column axes and tail load path.
    def test_fan_levels_follow_transfer_direction_and_keep_grip_lands(self):
        p=plan()['routes']
        for names,lands in ((['W027','W028','W029'],[19,14,9]),
                            (['W038','W039','W040'],[19,14,9]),
                            (['W046','W048','W050'],[9,14,19]),
                            (['W054','W056','W058'],[9,14,19])):
            self.assertEqual(lands,[p[n]['parts'][0]['length_mm'] for n in names])
            for n in names:
                self.assertGreaterEqual(p[n]['parts'][-1]['length_mm'],9)
                self.assertTrue(all(s['end'][2]>=s['start'][2] for s in p[n]['parts']))

if __name__=='__main__':unittest.main()
