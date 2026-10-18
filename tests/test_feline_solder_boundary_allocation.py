import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from compose_feline_solder_boundary_allocation import compose


class SolderBoundary(unittest.TestCase):
    def test_actual_seven_sources_and_tangent(self):
        p=compose();self.assertEqual(len(p['ends']),7)
        self.assertFalse(p['selected']);self.assertFalse(p['N01_complete'])
        for e in p['ends']:
            self.assertEqual(e['bare_segments'][-1]['end'],e['jacket_mouth_world_mm'])
            self.assertEqual(e['jacket_departure_axis'],[1,0,0])
            self.assertGreater(e['source_nominal_strip_mm'],3.5)

    def test_selected_core_and_sku_not_generic(self):
        rows={e['wire']:e for e in compose()['ends']}
        self.assertEqual(rows['XS11']['selected_source']['sku_candidate'],'Adafruit1446')
        self.assertEqual(rows['XS11']['bare_radius_project_mm'],.13)
        self.assertEqual(rows['XL05']['selected_source']['sku_candidate'],'Pololu1871')
        self.assertAlmostEqual(rows['XL05']['bare_radius_project_mm'],.2026375466632702)
        self.assertAlmostEqual(rows['XL02']['bare_radius_project_mm'],.28209479177387814)


if __name__=='__main__':unittest.main()
