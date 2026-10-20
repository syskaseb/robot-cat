"""MAIN coupled-constructor contracts, no whole-scene rerun."""
import json,unittest
import FreeCAD as A
from receive_feline_main_supported_unit import local_inputs,construct,BOARD,BED
from compose_feline_cuff_boundaries import current


class WholeMain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parts,_=local_inputs();_,ends,_=current()
        cls.parts=parts;cls.actors,cls.kinds,cls.recipes,cls.retired=construct(parts,ends)

    def test_real_PCB_not_lowest_compound_point(self):
        b=self.actors[BOARD].BoundBox
        self.assertAlmostEqual(b.ZMin,99.25,4)
        self.assertAlmostEqual(b.ZMax,106.9248,4)
        for i in (0,1):
            self.assertAlmostEqual(self.actors[f'Ref_Material_MAIN_{i}_head_0_0'].BoundBox.ZMin,100.8248,4)
            self.assertAlmostEqual(self.actors[f'Ref_Material_MAIN_{i}_lower_washer_0_0'].BoundBox.ZMax,91.25,4)

    def test_full_insulated_fan_and_grip(self):
        self.assertEqual(len(self.recipes),4)
        for r in self.recipes.values():
            self.assertEqual(r['full_individual_grip_mm'],9)
            self.assertEqual(r['sleeve_raw_mm'],16)
            self.assertGreaterEqual(r['min_recovered_intact_overlap_mm'],6)
            self.assertEqual(r['jacket_nominal_project_radius_mm'],1.05)
            self.assertTrue(r['physical_through_pad_role_preserved'])
        self.assertEqual(sorted(round(r['source_pad_mm'][0],3) for r in self.recipes.values()),[-25.25,-21.75,-18.25,-14.75])

    def test_one_supported_module(self):
        root=self.actors['MainSupported:root'];comb=self.actors['MainSupported:comb']
        self.assertEqual(len(root.Solids),1)
        self.assertGreater(root.common(self.parts[BED]).Volume,10)
        self.assertGreater(root.common(comb).Volume,1)
        self.assertEqual(len(self.retired),18)


if __name__=='__main__':unittest.main()
