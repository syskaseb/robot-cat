"""Open bank saddle changes support topology, not the selected conductor."""
import math
from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from feline_bank_simple_source import proposal
from feline_s1_flexible_fans import saddle_shapes
from plan_feline_central_pi_wedge import packed
from plan_feline_layout import OUT


class BankSimpleSource(unittest.TestCase):
    def test_selected_wire_first9_and_quarter_R_are_unchanged(self):
        source,row,wire,land=proposal()
        self.assertEqual(row['first_mm'],source['land_mm'])
        self.assertEqual(row['R_mm'],source['bend_R_mm'])
        self.assertAlmostEqual(wire.Volume,math.pi*source['radius_mm']**2*(18+math.pi*source['bend_R_mm']/2),places=5)
        self.assertEqual(land['grip_start_mm'],source['start_mm'])
        self.assertEqual(land['grip_axis'],source['departure_axis'])

    def test_full_open_grip_and_stock_head_clear_actual_key(self):
        source,row,wire,land=proposal();_,parts,_=packed(OUT/'n01-six-source-current-core.json')
        key=parts['Ref_Material_S0_key_CP2_0_0']
        self.assertGreater(wire.distToShape(key)[0],1.25)
        for head in (0,270):
            kit=saddle_shapes(land,270,head)
            self.assertAlmostEqual(kit['head_budget'].Volume,216)
            self.assertAlmostEqual(kit['saddle'].Volume,math.pi*((source['radius_mm']+2)**2-(source['radius_mm']+.15)**2)*9/2,places=5)
            for name,s in kit.items():
                self.assertTrue(s.isValid());self.assertGreater(s.distToShape(key)[0],1.25,name)
                self.assertLess(s.common(wire).Volume,1e-5,name)


if __name__=='__main__':unittest.main()
