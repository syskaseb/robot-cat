import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
import math
from plan_feline_fore_vertical_packet import fore_datum,upper_angle,prefix,grip
import FreeCAD as A


class ForeDatum(unittest.TestCase):
    def test_whole_case_and_whole_grip_margins_not_just_wire(self):
        x,y,z=fore_datum(-110.15,14,-48,-124.457566,30.842526,-117)
        self.assertAlmostEqual(-124.457566-(x+2.9),1.45)
        self.assertGreaterEqual(-117-(x+10.125),1.25)
        self.assertAlmostEqual((y-11)-14,1.25)
        self.assertAlmostEqual((z-25.5)-30.842526,1.25)

    def test_datum_translates_with_actual_source_constraints(self):
        a=fore_datum(-110.15,14,-48,-124.457566,30.842526,-117)
        b=fore_datum(-100.15,19,-45,-114.457566,33.842526,-107)
        self.assertEqual([round(y-x,8) for x,y in zip(a,b)],[10,5,3])

    def test_upper_roof_constraint_entire_wire_not_only_arc(self):
        qz=83.092526;angle=upper_angle(qz,112)
        self.assertLessEqual(qz+9+(6+1.55)*math.sin(angle)+32*math.cos(angle),112-3.25+1e-8)
        self.assertAlmostEqual(math.degrees(angle),73)

    def test_straight_and_angled_prefix_and_full_hardware(self):
        q=A.Vector(-128,25,30);d=A.Vector(0,0,-1);b=A.Vector(0,1,0)
        for angle in (0,math.radians(73)):
            s,end,t=prefix(q,d,b,angle)
            self.assertTrue(s.isValid());self.assertAlmostEqual(t.Length,1)
            self.assertAlmostEqual(s.Volume,math.pi*1.7**2*(9+6*angle),places=5)
            for custom in (False,True):
                self.assertTrue(all(x.isValid() and x.Solids for x in grip(end,t,1.7,custom)))


if __name__=='__main__':unittest.main()
