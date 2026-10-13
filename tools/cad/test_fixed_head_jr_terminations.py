"""Fixed three-core splice allocation contracts, no assembly claim."""
import unittest
import FreeCAD as A
import Part
from plan_fixed_head_jr_terminations import allocation

class FixedJRJoins(unittest.TestCase):
    def feeds(self):
        return {n:[Part.makeLine(A.Vector(x,100,z),A.Vector(x,-40,z))]
                for n,x,z in [('XB23',-247,51),('XB22',-227,48),('XS23',-237,45)]}
    def test_lap_stock_and_independent_lands(self):
        pads,bands,sleeves,rows=allocation(self.feeds())
        self.assertEqual(len(rows),3);self.assertEqual(len(bands),6)
        for row in rows:
            self.assertAlmostEqual(row['HELU_guide_to_lap_end_mm']+row['JR_guide_to_lap_end_mm'],148)
            self.assertEqual(row['independent_intact_lands_Y_mm'],[[15,24],[46,55]])
        for band in bands.values():self.assertAlmostEqual(band.BoundBox.ZMin,40)
        for sleeve in sleeves.values():
            self.assertAlmostEqual(sleeve.BoundBox.YLength,20)
            self.assertAlmostEqual(sleeve.BoundBox.ZLength,4.8)
    def test_short_corridor_is_rejected_before_native(self):
        feeds=self.feeds();feeds['XB22']=[Part.makeLine(A.Vector(-227,100,48),A.Vector(-227,54,48))]
        with self.assertRaises(AssertionError):allocation(feeds)

if __name__=='__main__':unittest.main()
