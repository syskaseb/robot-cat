"""Do not confuse valid reference curves with invalid purchased solids."""
import unittest
import FreeCAD as A
import Part
from receive_feline_jpwm_whole_pose import solid_profile_target
from feline_fore_power_pair import SolidQueries


class ProfileTarget(unittest.TestCase):
    def test_full_known_radius_not_just_centreline(self):
        wire=Part.Wire([Part.makeLine(A.Vector(0,0,0),A.Vector(0,20,0))])
        solid=solid_profile_target(wire,dict(kind='curve_profile_reservation',nominal_profile_radius_mm=2.))
        self.assertTrue(solid.isValid())
        self.assertEqual(len(solid.Solids),1)
        obstacle=Part.makeBox(2,4,2,A.Vector(1.5,8,-1))
        self.assertGreater(wire.distToShape(obstacle)[0],1.25)
        self.assertAlmostEqual(SolidQueries().distance(solid,obstacle),0.)

    def test_world_placement_not_applied_twice(self):
        wire=Part.Wire([Part.makeLine(A.Vector(0,0,0),A.Vector(0,20,0))])
        wire.Placement=A.Placement(A.Vector(31,42,53),A.Rotation(A.Vector(0,0,1),90))
        solid=solid_profile_target(wire,dict(kind='curve_profile_reservation',nominal_profile_radius_mm=2.))
        self.assertAlmostEqual(solid.BoundBox.XMin,11.)
        self.assertAlmostEqual(solid.BoundBox.XMax,31.)
        self.assertAlmostEqual(solid.BoundBox.YMin,40.)
        self.assertAlmostEqual(solid.BoundBox.ZMin,51.)

    def test_missing_radius_cannot_be_invented(self):
        wire=Part.Wire([Part.makeLine(A.Vector(0,0,0),A.Vector(0,20,0))])
        with self.assertRaisesRegex(AssertionError,'invented'):
            solid_profile_target(wire,dict(kind='curve_profile_reservation'))


if __name__=='__main__':unittest.main()
