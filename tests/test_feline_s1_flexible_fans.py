"""Flexible source profiles preserve physical datums; no wholeN01 assertion."""
import json
import math
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from feline_s1_flexible_fans import curve,wire_shape,saddle_shapes,absolute_inside
from plan_feline_layout import OUT


class FlexibleSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=json.loads((OUT/'n01-intrinsic-s1-whole-pose.json').read_text())
        cls.pose=json.loads((OUT/'n01-source-saddles-whole-joint.json').read_text())['fore_outboard_budget']['pose']

    def test_all_four_mouths_are_rigid_and_keep_R25_2(self):
        r=np.array(self.pose['rotation_rows'])
        for source in self.packet['recipes']:
            row=curve(source,self.pose,self.packet,45,45)
            q=r@(np.array(source['point_mm'])-self.packet['centre_mm'])+self.pose['centre_mm']
            np.testing.assert_allclose(q,row['point_mm'],atol=1e-10)
            np.testing.assert_allclose(r@source['departure_axis'],row['departure_axis'],atol=1e-10)
            self.assertEqual((row['R_mm'],row['first_project_mm'],row['full_grip_mm']),(25.2,3,9))

    def test_fore_up_port_has_variable_sweep_not_forced_quarter_loop(self):
        source=next(r for r in self.packet['recipes'] if r['ref'].startswith('W065/'))
        row=curve(source,self.pose,self.packet,45,45)
        self.assertTrue(row['sample_inside_absolute_envelope'])
        s=wire_shape(row)
        self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1)
        self.assertTrue(absolute_inside(s))
        length=3+25.2*math.pi/4+9
        self.assertAlmostEqual(s.Volume,math.pi*2.1**2*length,places=5)

    def test_full_after9_saddle_band_and_head_are_present(self):
        row=curve(self.packet['recipes'][0],self.pose,self.packet,45,45)
        parts=saddle_shapes(row,0,90)
        self.assertEqual(set(parts),{'saddle','band_budget','head_budget'})
        self.assertTrue(all(s.isValid() and s.Solids for s in parts.values()))
        self.assertEqual(len(parts['saddle'].Solids),1)
        self.assertAlmostEqual(parts['head_budget'].Volume,216)
        self.assertAlmostEqual(parts['saddle'].Volume,math.pi*(4.1**2-2.25**2)/2*9,places=6)


if __name__=='__main__':unittest.main()
