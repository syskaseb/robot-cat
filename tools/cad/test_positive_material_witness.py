import unittest
import FreeCAD as A
import Part
from immutable_bounds import ImmutableBounds
from positive_material_witness import witness


class PositiveWitnessTest(unittest.TestCase):
    def test_real_inside_point_rejects(self):
        box=Part.makeBox(10,10,10);line=Part.makeLine(A.Vector(-1,5,5),A.Vector(11,5,5))
        self.assertIsNotNone(witness(line,box,ImmutableBounds(),{}))
    def test_inside_bbox_hole_is_not_solid_contact(self):
        ring=Part.makeBox(10,10,10).cut(Part.makeCylinder(2,12,A.Vector(5,5,-1)))
        line=Part.makeLine(A.Vector(5,5,-1),A.Vector(5,5,11))
        self.assertIsNone(witness(line,ring,ImmutableBounds(),{}))
    def test_missing_witness_does_not_claim_radius_clearance(self):
        box=Part.makeBox(10,10,10);line=Part.makeLine(A.Vector(0,10.1,5),A.Vector(10,10.1,5))
        self.assertIsNone(witness(line,box,ImmutableBounds(),{}))
        self.assertLess(line.distToShape(box)[0],1.25)


if __name__=='__main__':unittest.main()
