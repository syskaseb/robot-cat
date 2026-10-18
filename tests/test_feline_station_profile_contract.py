import importlib.util
import unittest
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/'tools/cad/compose_feline_station_profile_contract.py'
spec=importlib.util.spec_from_file_location('station_contract',PATH)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class StationContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=module.compose()
        cls.ports={r['endpoint']:r for r in cls.result['ports']}

    def test_complete_and_no_false_acceptance(self):
        self.assertEqual(len(self.ports),86)
        self.assertFalse(self.result['N01_complete'])
        self.assertFalse(self.result['current_parts_or_ECAD_changed'])

    def test_port_identity_not_wire_max(self):
        self.assertEqual(self.ports['FL_P.1']['source_recipe_id'],'W026/custom/end')
        self.assertEqual(self.ports['FL_P.1']['query_radius_mm'],2.1)
        self.assertEqual(self.ports['FL_P.2']['query_radius_mm'],1.55)
        self.assertEqual(self.ports['G_TAIL.4']['query_radius_mm'],.7)
        self.assertEqual(self.ports['G_TAIL.3']['query_radius_mm'],.925)

    def test_unknown_not_shrunk(self):
        for endpoint in self.result['unknown_endpoints']:
            row=self.ports[endpoint]
            self.assertIsNone(row['nominal_project_radius_mm'])
            self.assertEqual(row['query_radius_mm'],2.1)
            self.assertTrue(row['unknown_retains_conservative_budget'])
        self.assertEqual(len(self.result['unknown_endpoints']),4)

    def test_no_unrestricted_suffix_guess(self):
        self.assertEqual(module.wire_identity('W026/custom'),'W026')
        self.assertEqual(module.wire_identity('XP03.source'),'XP03')
        self.assertEqual(module.wire_identity('W026/factory'),'W026/factory')


if __name__=='__main__':unittest.main()
