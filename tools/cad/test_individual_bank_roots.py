import unittest
import FreeCAD as A
import Part
from current_bank_datums import datums
from test_current_bank_datums import BankDatumTests
from plan_individual_bank_seats import seats
from plan_individual_bank_roots import patches,HALF,LEAF_HALF
from plan_axial_source_supports import arm_box


class BankRootTests(unittest.TestCase):
    def test_leaf_nominal_housing_overlap_is_only_inside_catalog_panel(self):
        scene=BankDatumTests().scene();placed=datums(scene);panels=seats(placed,True)
        for r in placed:
            x,y,z=panels[r['id']]['recipe']['centre_mm']
            for sign in (-1,1):
                leaf=arm_box([x,y+sign*6.65,z-3],[x,y+sign*12,z-3],LEAF_HALF)
                overlap=leaf.common(scene[r['parts']['Housing']['name']])
                self.assertGreater(overlap.Volume,0)
                self.assertLess(overlap.cut(panels[r['id']]['body']).Volume,1e-5)

    def test_structural_roots_are_actual_contained_four_mm_cubes(self):
        parent=Part.makeBox(40,40,40);points=patches(parent,[50,20,20])
        self.assertTrue(points);self.assertEqual(HALF,[2,2,2])
        for p in points:self.assertLess(arm_box(p,p,HALF).cut(parent).Volume,1e-5)


if __name__=='__main__':unittest.main()
