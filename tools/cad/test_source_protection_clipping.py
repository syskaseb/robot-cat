"""Small exact-distance threshold tests, no full CAD scene rebuild."""
import unittest
import FreeCAD as A
import Part
from check_source_contact_insulation import bounded_distance

class Clipping(unittest.TestCase):
 def setUp(self):self.s=Part.makeBox(1,1,1)
 def test_near_solid_preserves_violation(self):
  other=Part.makeBox(30,1,1,A.Vector(1.7,0,0))
  self.assertAlmostEqual(bounded_distance(self.s,other,1),.7,places=6)
 def test_far_lower_bound_is_not_a_measurement(self):
  other=Part.makeBox(1,1,1,A.Vector(20,0,0))
  self.assertGreaterEqual(bounded_distance(self.s,other,1),1)
  self.assertLess(bounded_distance(self.s,other,1),2)
 def test_near_curve_and_remote_tail(self):
  curve=Part.makePolygon([A.Vector(.5,1.4,.5),A.Vector(20,1.4,.5),A.Vector(100,100,.5)])
  self.assertAlmostEqual(bounded_distance(self.s,curve,1),.4,places=6)
 def test_threshold_equality_not_missed(self):
  other=Part.makeBox(10,1,1,A.Vector(2,0,0))
  self.assertAlmostEqual(bounded_distance(self.s,other,1),1,places=6)

if __name__=='__main__':unittest.main()
