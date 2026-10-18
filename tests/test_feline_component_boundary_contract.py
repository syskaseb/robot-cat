import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from compose_feline_component_boundary_contract import compose


class BoundaryContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=compose()

    def test_actual_fuse_and_display_dimensions(self):
        by={r['role']:r for r in self.p['unplaced_component_dimensions']}
        for ref in ('F_HY','F_HP','F_TY'):
            self.assertEqual(by[ref]['source_dimensions_XYZ_mm'],[51,20.25,22])
            self.assertEqual(by[ref]['vertical_X_to_minusZ_dimensions_XYZ_mm'],[22,20.25,51])
        self.assertEqual(by['Monitor5015']['upright_Rx_minus90_dimensions_XYZ_mm'],[41,12,25])

    def test_solder_pads_not_jacket_mouths(self):
        pads=self.p['seven_PCA_solder_pads'];self.assertEqual(len(pads),7)
        self.assertTrue(all(r['jacket_point_and_bare_form_must_be_explicit'] for r in pads))
        self.assertEqual(sorted(r['nominal_OD_project_upper_mm'] for r in pads),[.8,.8,.8,1.4,1.4,1.4,1.4])

    def test_no_scope_point_for_source_contract(self):
        self.assertFalse(self.p['selected']);self.assertFalse(self.p['N01_complete']);self.assertFalse(self.p['physical_pass'])
        self.assertEqual(len(self.p['all20_WAGO_station_sizes']),20)
        self.assertEqual(len(self.p['preserved_fore_frame_and_side_wall_bounds']),5)


if __name__=='__main__':unittest.main()
