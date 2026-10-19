import unittest
import FreeCAD as A
import Part
from plan_feline_pi_root_access import material_entries,profile_gap,root_arm


class RootAccess(unittest.TestCase):
    def test_annular_centroid_is_not_a_material_anchor(self):
        s=Part.makeBox(20,20,2,A.Vector(-10,-10,0)).cut(Part.makeCylinder(3,2))
        entries=material_entries(s,[0,0,5]);self.assertTrue(entries)
        self.assertFalse(s.isInside(A.Vector(0,0,1.5),1e-7,False))
        for row in entries:self.assertTrue(s.isInside(A.Vector(*row['point_mm']),1e-7,False))

    def test_connected_profile_guard_rejects_containment_and_crossing(self):
        box=Part.makeBox(10,10,10)
        inside=Part.makeLine(A.Vector(3,3,3),A.Vector(4,4,4))
        crossing=Part.makeLine(A.Vector(-5,5,5),A.Vector(15,5,5))
        clear=Part.makeLine(A.Vector(0,20,0),A.Vector(10,20,0))
        self.assertFalse(profile_gap(box,inside,1)['ok'])
        self.assertFalse(profile_gap(box,crossing,1)['ok'])
        self.assertTrue(profile_gap(box,clear,1)['ok'])

    def test_root_arm_is_fused_and_has_real_positive_parent_joint(self):
        parent=Part.makeBox(20,20,2,A.Vector(-10,-10,0))
        arm=root_arm([9.5,0,1],[30,0,10])
        self.assertEqual(len(arm.Solids),1)
        self.assertGreater(parent.common(arm).Volume,1)


if __name__=='__main__':unittest.main()
