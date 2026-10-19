"""Constraint/constructor tests, not whole N01 or physical acceptance."""
import math,unittest
import FreeCAD as A
import Part
from feline_service_gallery import usb_recipe


class GalleryConstructor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.wire,cls.recipe=usb_recipe()

    def test_original_USB_length_and_full_hard_R(self):
        self.assertAlmostEqual(self.recipe['USB_length_mm'],452,places=5)
        self.assertGreaterEqual(self.recipe['minimum_R_mm'],30)
        self.assertGreaterEqual(self.recipe['first_turn_minimum_R_mm'],30)
        self.assertTrue(self.wire.isValid());self.assertEqual(len(self.wire.Solids),1)
        self.assertAlmostEqual(self.wire.Volume,math.pi*2.5**2*452,delta=.05)

    def test_both_grips_have_actual_full_straight_nine(self):
        for key in ('Pi_full9_mm','BUS_full9_mm'):
            a,b=(A.Vector(*p) for p in self.recipe[key]);axis=b-a
            self.assertAlmostEqual(axis.Length,9,places=7)
            outside=Part.makeCylinder(2.5,9,a,axis).cut(self.wire)
            self.assertTrue(outside.isNull() or outside.isValid())
            self.assertLess(outside.Volume,1e-5)

    def test_return_separates_complete_port_and_tool_height_constraints(self):
        self.assertGreaterEqual(self.recipe['fixed_return_plane_Z_mm']-2.5-self.recipe['ATO_tool_top_Z_mm'],1.25)
        # Received old USB-A upperY31.96 shifted to the shared Pi datum:
        # +7.8581096 from the old under-port scene, then -4mm.
        port_max_Y=31.96+7.85810963471377-4
        self.assertGreaterEqual(self.recipe['return_Y_mm']-4-port_max_Y,1.25)
        self.assertGreaterEqual(self.recipe['final_exact_straight_mm'],12)
        self.assertEqual(self.recipe['BUS_mouth_mm'],[86,46,89])


if __name__=='__main__':unittest.main()
