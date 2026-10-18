"""Pure checks of the full nominal source routes, not hardware acceptance."""
import importlib.util
import math
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('coupled',ROOT/'tools/cad/plan_feline_n01_coupled_pi_bus.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class CoupledPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=mod.build_flat_unit()
    def test_full_endpoint_and_length_gates(self):
        p=self.p;w={r['wire']:r for r in p['routes']}
        self.assertEqual(w['W043']['end_mm'],[-84,4.5,-33.5])
        self.assertLess(math.dist(w['W077']['end_mm'],p['splice']['tip16_mm']),1e-8)
        self.assertAlmostEqual(w['W078']['end_mm'][2],-16)
        self.assertEqual(w['W078']['end_direction'],[0,0,1])
        self.assertLess(w['W043']['raw_required_mm'],40)
        self.assertLess(w['W077']['length_mm'],60)
        self.assertLess(60+8.35,84.5)
        self.assertLess(w['W078']['raw_required_mm'],65)
        self.assertEqual(p['stock_candidate']['K1474_units'],1)
        self.assertFalse(p['selected']);self.assertFalse(p['N01_complete'])
    def test_curve_continuity_and_tangents(self):
        for row in self.p['routes']:
            for a,b in zip(row['parts'],row['parts'][1:]):
                self.assertLess(math.dist(a['end'],b['start']),1e-8)
            for part in row['parts']:
                if part['kind']=='arc':
                    self.assertGreaterEqual(part['radius_mm'],6)
                    self.assertAlmostEqual(part['length_mm'],math.pi*part['radius_mm']/2)
    def test_sleeve_and_both_full_grips_distinct(self):
        s=self.p['splice'];a,b=s['sleeve_y_mm']
        left,right=s['jacket_grip16_y_mm'],s['jacket_grip18_y_mm']
        self.assertAlmostEqual(b-a,20)
        self.assertAlmostEqual(left[1]-left[0],9)
        self.assertAlmostEqual(right[1]-right[0],9)
        self.assertAlmostEqual(a-left[1],2)
        self.assertAlmostEqual(right[0]-b,2)
        # The WHOLE9mm clamp must end on the25mm straight, not extend into
        # the following arc as the unselected R2 metadata did by1mm.
        donor=next(r for r in self.p['routes'] if r['wire']=='W078')
        self.assertAlmostEqual(right[1],donor['parts'][0]['end'][1])

    def test_same_parts_and_colour_stock(self):
        p=self.p;s=p['stock_candidate']
        self.assertEqual(s['red_remaining_mm']+s['red_W078_candidate_mm']+225,1000)
        self.assertEqual(s['black_remaining_mm']+s['black_W060_retained_candidate_mm']+225,1000)
        self.assertLessEqual(s['positive_path_candidate_mm'],300)
        self.assertEqual(p['unit_template_groups'],['F_PI','WAGO:P_SYS_new','MAIN'])
        self.assertTrue(p['unit_world_pose_pending'])

if __name__=='__main__':unittest.main()
