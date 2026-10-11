import json,math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/cad'))
from plan_current_front_gallery import plan,OUT

class FrontGallery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=plan()
    def test_cases_clear_declared_side_wall_without_width_growth(self):
        for n,s in self.p['stations'].items():
            self.assertEqual(s['centre_mm'][0],40)
            self.assertEqual(s['centre_mm'][1],75 if n=='FL_P' else -93)
            self.assertGreater(abs(s['centre_mm'][1])-4.5,49.34)
            self.assertLessEqual(abs(s['centre_mm'][1])+4.5,100)
    def test_main_input_is_outside_westgoing_fans(self):
        for n,s in self.p['stations'].items():
            self.assertEqual(s['logical_to_physical_common_rail_cavity']['1'],5)
            self.assertGreater(s['ports']['1'][0],max(s['ports'][str(i)][0] for i in (2,3,4)))
            self.assertIsNone(self.p['ports'][n+'.5']['wire'])
    def test_all_changed_paths_and_terminal_lands_present(self):
        self.assertEqual(len(self.p['routes']),8)
        for n,r in self.p['routes'].items():
            self.assertGreaterEqual(r['parts'][-1]['length_mm'],9)
            self.assertIsNone(r['actual_cut_mm'])
        self.assertFalse(self.p['selected']);self.assertFalse(self.p['W5_complete'])
    def test_unchanged_upper_outputs_remain_exact(self):
        old=json.loads((OUT/'leg-stations-plan.json').read_text())
        for n,count in [('W026_CUSTOM',8),('W037_CUSTOM',9)]:
            self.assertEqual(self.p['routes'][n]['parts'][:count],old['routes'][n]['parts'][:count])

if __name__=='__main__':unittest.main()
