import unittest
import FreeCAD as A
import Part
from refresh_feline_power_space import same_geometry


class MeshResume(unittest.TestCase):
    def test_meshing_is_not_a_geometry_revision(self):
        a=Part.makeBox(3,4,5);b=a.copy(True,True)
        b.tessellate(.25)
        self.assertTrue(same_geometry(a,b))

    def test_private_copy_does_not_mutate_input_serialization(self):
        a=Part.makeBox(3,4,5);before=a.exportBrepToString()
        b=a.copy(True,True);b.tessellate(.25)
        self.assertEqual(before,a.exportBrepToString())

    def test_shift_is_rejected(self):
        a=Part.makeBox(3,4,5);b=a.copy()
        b.translate(A.Vector(.01,0,0))
        self.assertFalse(same_geometry(a,b))

    def test_equal_outer_bounds_do_not_hide_a_hole(self):
        a=Part.makeBox(3,4,5)
        b=a.cut(Part.makeCylinder(.3,5,A.Vector(1,1,0)))
        self.assertFalse(same_geometry(a,b))


if __name__=='__main__':unittest.main()
