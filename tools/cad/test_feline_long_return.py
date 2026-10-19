"""Constructor regressions only; these do not award N01 or world clearance."""
import math,unittest
from unittest.mock import patch
import FreeCAD as A
import Part
from plan_feline_long_return import usb_recipe,under_port_recipe


class LongReturnConstructor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.wire,cls.recipe=usb_recipe()

    def test_whole_original_project_length_not_a_shortened_cable(self):
        self.assertAlmostEqual(self.recipe['USB_length_mm'],452,places=5)
        self.assertTrue(self.wire.isValid());self.assertEqual(len(self.wire.Solids),1)
        self.assertAlmostEqual(self.wire.Volume,math.pi*2.5**2*452,delta=.05)

    def test_two_complete_nine_lands_before_any_new_grips(self):
        for name in ('Pi_full9_mm','BUS_full9_mm'):
            self.assertAlmostEqual(math.dist(*self.recipe[name]),9,places=7)
        self.assertAlmostEqual(math.dist(self.recipe['Pi_mouth_mm'],self.recipe['Pi_full9_mm'][0]),3,places=7)
        self.assertAlmostEqual(math.dist(self.recipe['BUS_mouth_mm'],self.recipe['BUS_full9_mm'][0]),3,places=7)

    def test_hard_radius_and_shared_return_not_rear_coil(self):
        self.assertGreaterEqual(self.recipe['minimum_R_mm'],30)
        self.assertGreaterEqual(self.recipe['return_ramp_minimum_R_mm'],30)
        self.assertEqual(self.recipe['main_straight_mm'],140)
        self.assertEqual(self.recipe['return_drop_mm'],12)
        # A B-spline's OCC box can exceed its actual extremum; this only
        # guards the declared coarse bay, not clearance to the tail.
        self.assertLess(self.wire.BoundBox.XMax,140)
        self.assertGreater(self.wire.BoundBox.ZMin,80)  # Coarse OCC box only.


class UnderPortConstructor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.wire,cls.recipe=under_port_recipe()

    def test_preserved_length_and_hard_bend_radius(self):
        self.assertTrue(self.wire.isValid());self.assertEqual(len(self.wire.Solids),1)
        self.assertAlmostEqual(self.recipe['USB_length_mm'],452,places=5)
        self.assertGreaterEqual(self.recipe['minimum_R_mm'],30)
        self.assertEqual(self.recipe['full_fixed_plane_Z_mm'],81.5)

    def test_both_full_grips_are_on_exact_straight_wire_not_a_curved_ramp(self):
        for key in ('Pi_full9_mm','BUS_full9_mm'):
            a,b=(A.Vector(*p) for p in self.recipe[key]);axis=b-a
            self.assertAlmostEqual(axis.Length,9,places=7)
            land=Part.makeCylinder(2.5,9,a,axis)
            outside=land.cut(self.wire)
            self.assertTrue(outside.isNull() or outside.isValid())
            self.assertLess(outside.Volume,1e-5)

    def test_complete_mating_bays_are_solved_from_same452_length(self):
        with patch('sys.argv',['test','--separate-mating-bays']):
            wire,recipe=under_port_recipe()
        self.assertAlmostEqual(recipe['BUS_mouth_mm'][0],64,places=7)
        self.assertAlmostEqual(recipe['USB_length_mm'],452,places=5)
        self.assertEqual(recipe['actual_Pi_USB_A_front_end_X_mm'],54)
        self.assertGreaterEqual(recipe['minimum_R_mm'],30)
        self.assertTrue(wire.isValid())


if __name__=='__main__':unittest.main()
