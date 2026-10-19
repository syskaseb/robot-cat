from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from feline_ato_service import reservation,receive


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

    def test_housing_face_mate_not_exemption_for_other_obstacles(self):
        fixed={}
        for side,letter in ((1,'L'),(-1,'R')):
            for i in range(6):
                x=(-47 if side>0 else -35)+24*i
                root=f'Ref_Material_F_{letter}{i+1}_CP2_'
                y=67.75 if side>0 else -86.55
                fixed[root+'ATO_0_0']=Part.makeBox(5.1,18.8,19.1,A.Vector(x-2.55,y,59.45))
                y=39.25 if side>0 else -67.75
                fixed[root+'Housing_0_0']=Part.makeBox(20.5,28.5,28,A.Vector(x-10.25,y,55))
        world=SimpleNamespace(bus={'name':'not_present'})
        records,_=receive(world,fixed)
        self.assertTrue(all(r['all_reservations_clear'] for r in records))
        blocker=Part.makeBox(2,2,2,A.Vector(-48,98,68))
        records,_=receive(world,fixed,{'ActualNewStrut':blocker})
        first=next(r for r in records if '_L1_' in r['name'])
        self.assertFalse(first['all_reservations_clear'])
        self.assertTrue(any(r['other']=='ActualNewStrut' for r in first['reservation_blockers']))


if __name__=='__main__':unittest.main()
