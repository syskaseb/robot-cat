import unittest
import FreeCAD as A
import Part
from plan_current_upper_operating_roots import printable
from loom_land_port import box


class OperatingRootTests(unittest.TestCase):
    def test_parent_plus_new_material_and_brim_are_combined(self):
        parent=box([0,0,0,200,150,100]);body=box([200,0,0,220,5,5])
        self.assertTrue(printable(parent,body,[[220,0,0]],[2]*3))
        self.assertFalse(printable(parent,body,[[246,0,0]],[2]*3))


if __name__=='__main__':unittest.main()
