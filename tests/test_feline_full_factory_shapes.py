import sys
import math
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from receive_feline_full_factory_packages import recipe_shapes,all_ranked


class FullFactoryShapes(unittest.TestCase):
    def test_quarter_full_sleeve_and_trim_coverage(self):
        for first in (9,45):
            row=dict(point_mm=[0,0,0],departure_axis=[1,0,0])
            candidate=dict(first_mm=first,bend_unit=[0,1,0])
            remaining,whole,own=recipe_shapes(row,candidate)
            self.assertTrue(all(s.isValid() and s.Solids for s in (remaining,whole,own)))
            self.assertEqual(len(remaining.Solids),3)
            arc_volume=math.pi*4*(first-9+12.4*math.pi/2)
            self.assertAlmostEqual(remaining.Solids[0].Volume,arc_volume,places=5)
            self.assertAlmostEqual(remaining.Solids[1].Volume,math.pi*2.4**2*20,places=5)
            self.assertAlmostEqual(remaining.Solids[2].Volume,math.pi*1.55**2*26,places=5)
            self.assertAlmostEqual(whole.BoundBox.XMin,0,places=6)
            self.assertAlmostEqual(own.BoundBox.XMin,2.5,places=6)
            self.assertAlmostEqual(remaining.BoundBox.YMax,12.4+14+18,places=6)

    def test_rigid_rotation_and_translation(self):
        row=dict(point_mm=[10,20,30],departure_axis=[0,-1,0])
        candidate=dict(first_mm=18,bend_unit=[0,0,1])
        remaining,whole,_=recipe_shapes(row,candidate)
        self.assertAlmostEqual(whole.BoundBox.YMax,20,places=6)
        self.assertAlmostEqual(remaining.BoundBox.ZMax,30+12.4+14+18,places=6)

    def test_invalid_axes_and_excess_factory_allowance_not_pass(self):
        for first,bend in ((54,[0,1,0]),(63,[0,1,0]),(9,[1,0,0])):
            with self.assertRaises(AssertionError):
                recipe_shapes(dict(point_mm=[0,0,0],departure_axis=[1,0,0]),dict(first_mm=first,bend_unit=bend))

    def test_ranker_keeps_negative_field_recipes_but_not_long_leads(self):
        row=dict(point_mm=[0,0,0],departure_axis=[1,0,0])
        f={'material':lambda p:np.full(len(p),0.)}
        candidates=all_ranked(row,f)
        self.assertEqual(len(candidates),160)
        self.assertEqual({r['first_mm'] for r in candidates},{9,18,27,36,45})
        self.assertTrue(all(r['numeric_min_surface_margin_mm']<0 for r in candidates))
        with self.assertRaises(AssertionError):
            all_ranked(row,{'material':lambda p:np.full(len(p),np.nan)})


if __name__=='__main__':unittest.main()
