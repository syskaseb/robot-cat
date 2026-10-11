import unittest,sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from plan_current_leg_stations import plan
from open_prototype_source_group import check_path

class LegStationTests(unittest.TestCase):
    def test_twelve_cases_sixty_unique_ports_same_graph(self):
        p=plan();self.assertEqual(12,len(p['stations']));self.assertEqual(60,len(p['ports']))
        self.assertEqual('W026',p['ports']['FL_P.1']['wire'])
        self.assertEqual('W053',p['ports']['RR_P.1']['wire'])
        self.assertEqual([124.5,-80,19.5],p['ports']['RR_P.1']['point_mm'])
        self.assertEqual([-69.5,-80,19.5],p['ports']['FR_P.1']['point_mm'])
        self.assertEqual([35,-79,99],p['stations']['D_FR']['centre_mm'])
        self.assertFalse(p['selected'] or p['W5_complete'] or p['physical_pass'])
        self.assertLess(p['factory_override']['guide_mm'],84.5)
        check_path(p['factory_override']['parts'],min_radius=25.2)
    def test_full_four_output_paths_tangent_and_radius(self):
        p=plan()
        for leg,wid in [('FL','W026'),('FR','W037'),('RL','W045'),('RR','W053')]:
            r=p['routes'][wid+'_CUSTOM'];check_path(r['parts'],end=p['ports'][leg+'_P.1']['point_mm'],min_radius=25.2)
            self.assertIsNone(r['actual_cut_mm'])
if __name__=='__main__':unittest.main()
