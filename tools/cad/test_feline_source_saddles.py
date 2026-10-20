import unittest
import FreeCAD
from feline_source_saddles import build
from plan_feline_battery_f0_joint import path


class SourceSaddles(unittest.TestCase):
    def test_full_nine_on_first_R12_arc_no_extra_length(self):
        r=path([0,0,0],[2**-.5,2**-.5,0],[('turn',[-2**-.5,2**-.5,0])],12.4)
        kit,rec=build(r['parts'][0],.3,[0,0,-1],7.)
        self.assertEqual(rec['full_jacket_grip_arclength_mm'],[.3,9.3])
        self.assertEqual(rec['extra_wire_length_mm'],0)
        self.assertAlmostEqual(kit['head'].Volume,5*4.3*5.3,places=5)

    def test_early_vertical_R25_grip_and_whole_head(self):
        r=path([0,0,0],[0,0,-1],[('turn',[-3**.5/2,-.5,0])],25.2)
        kit,rec=build(r['parts'][0],3,[-.5,3**.5/2,0],9)
        self.assertEqual(rec['full_jacket_grip_arclength_mm'],[3,12])
        self.assertEqual(len(kit['pad'].Solids),1)

    def test_reject_invented_grip_beyond_existing_segment(self):
        r=path([0,0,0],[1,0,0],[('line',8)],12.4)
        with self.assertRaises(AssertionError):build(r['parts'][0],0,[0,0,-1],4.5)


if __name__=='__main__':unittest.main()
