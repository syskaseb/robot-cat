import unittest
import FreeCAD as A
import Part
from plan_remaining25_saddle_roots import printable


class RootPrintContract(unittest.TestCase):
    def test_brim_is_checked_on_combined_parent_not_arm_alone(self):
        parent=Part.makeBox(100,100,100)
        saddle=Part.makeBox(3,3,3,A.Vector(0,0,200))
        self.assertTrue(printable(parent,saddle,[[1,1,201]]))
        self.assertFalse(printable(parent,saddle,[[1,1,246]]))

    def test_world_translation_does_not_change_print_size(self):
        parent=Part.makeBox(100,100,100,A.Vector(-200,10,75))
        saddle=Part.makeBox(3,3,3,A.Vector(-190,12,200))
        self.assertTrue(printable(parent,saddle,[[-190,13,201]]))


if __name__=='__main__':unittest.main()
