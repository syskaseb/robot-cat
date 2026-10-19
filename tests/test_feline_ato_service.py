from pathlib import Path
import sys
import unittest
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from feline_ato_service import reservation


class AtoService(unittest.TestCase):
    def test_continuous_all_translation_and_both_sides(self):
        for side in (-1,1):
            y=67.75 if side>0 else -86.55
            fuse=Part.makeBox(5.1,18.8,19.1,A.Vector(-49.55,y,59.45))
            tools,record=reservation('Ref_Material_F_L1_CP2_ATO_0_0',fuse)
            self.assertEqual(record['side'],side)
            for step in (0,5,10,15,20,25):
                moved=fuse.copy();moved.translate(A.Vector(0,side*step,0))
                self.assertLess(moved.cut(tools['continuous_fuse_sweep']).Volume,1e-7)
            self.assertAlmostEqual(tools['tool_budget'].BoundBox.XLength,12)
            self.assertFalse(record['supplier_tool_or_physical_fit_verified'])


if __name__=='__main__':unittest.main()
