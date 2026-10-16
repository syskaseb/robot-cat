import unittest
import FreeCAD as A
import Part
from compose_case_bond_contribution import patch_size


class CaseBondTests(unittest.TestCase):
    def test_patch_sizes_use_actual_bond_plane_not_world_z_only(self):
        self.assertEqual(patch_size([0,0,0,31,.5,8]),[8,31])
        self.assertEqual(patch_size([0,0,0,3,25.5,.5]),[3,25.5])
        with self.assertRaises(AssertionError):patch_size([0,0,0,3,25.5,1])


if __name__=='__main__':unittest.main()
