import unittest
import FreeCAD as A
import Part
from immutable_bounds import ImmutableBounds
from current_prototype_harness_scene import W


class Tests(unittest.TestCase):
    def test_original_operation_matches_including_touch_and_margin(self):
        g=ImmutableBounds();a=Part.makeBox(2,3,4)
        for dx in (0,2,2.001,5,-4):
            for r in (0,.001,.5,3):
                b=a.copy();b.translate(A.Vector(dx,1,2))
                self.assertEqual(g.near(a,b,r),W.near(a,b,r))
                self.assertEqual(g.near(b,a,r),g.near(a,b,r))
        b=a.copy();b.translate(A.Vector(3,4,5))
        for r in (0,1,1.999999,2,3,4):
            self.assertEqual(g.near(a,b,r),W.near(a,b,r))

    def test_changed_placement_new_instance_and_no_accumulated_margin(self):
        g=ImmutableBounds();a=Part.makeBox(1,1,1);b=a.copy()
        b.Placement=A.Placement(A.Vector(4,0,0),A.Rotation())*b.Placement
        self.assertTrue(g.near(a,b,4));self.assertFalse(g.near(a,b,0))
        self.assertTrue(g.near(a,a,0));self.assertEqual(len(g.bounds),2)


if __name__=='__main__':unittest.main()
