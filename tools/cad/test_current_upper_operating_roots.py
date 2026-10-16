import unittest
import FreeCAD as A
import Part
from plan_current_upper_operating_roots import printable,arrival_goal
from plan_axial_source_supports import arm_box
from loom_land_port import box


class OperatingRootTests(unittest.TestCase):
    def test_parent_plus_new_material_and_brim_are_combined(self):
        parent=box([0,0,0,200,150,100]);body=box([200,0,0,220,5,5])
        self.assertTrue(printable(parent,body,[[220,0,0]],[2]*3))
        self.assertFalse(printable(parent,body,[[246,0,0]],[2]*3))

    def test_mta_arrival_is_on_print_side_not_in_adhesive(self):
        for side in (-1,1):
            lo,hi=sorted((side*69,side*69.5));floorlo,floorhi=sorted((side*67.8,side*69))
            recipe=dict(adhesive_bounds_mm=[-30.5,lo,145.4,.5,hi,153.4])
            row=dict(kind='MTA_case_shelf',goal=[-8,side*67.3,149.4],half=[2]*3,recipe=recipe)
            seed=arm_box(arrival_goal(row),arrival_goal(row),row['half'])
            self.assertLess(seed.common(box(recipe['adhesive_bounds_mm'])).Volume,1e-6)
            self.assertGreater(seed.common(box([-30.5,floorlo,145.4,.5,floorhi,153.4])).Volume,1)


if __name__=='__main__':unittest.main()
