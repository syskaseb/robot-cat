"""Face bearing is distinct from a zero-volume solid intersection."""
import unittest
import FreeCAD as A
import Part
from plan_current_data_ground_mounts import bearing_area


class Bearing(unittest.TestCase):
    def test_coincident_actual_faces(self):
        a=Part.makeBox(10,10,3,A.Vector(0,0,-3))
        b=Part.makeBox(8,8,2,A.Vector(1,1,0))
        self.assertAlmostEqual(bearing_area(a,b,0),64,6)
        self.assertLess(a.common(b).Volume,1e-8)

    def test_no_inferred_contact_from_near_or_bbox(self):
        a=Part.makeBox(10,10,3,A.Vector(0,0,-3))
        for x,z in [(0,.001),(11,0)]:
            b=Part.makeBox(8,8,2,A.Vector(x,1,z))
            self.assertEqual(bearing_area(a,b,0),0)

    def test_only_plane_roundoff_normalized(self):
        a=Part.makeBox(10,10,3,A.Vector(0,0,-3))
        b=Part.makeBox(8,8,2,A.Vector(1,1,1e-9))
        self.assertAlmostEqual(bearing_area(a,b,0),64,6)


if __name__=='__main__':unittest.main()
