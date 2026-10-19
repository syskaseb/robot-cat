import json,math,unittest
from pathlib import Path
OUT=Path(__file__).resolve().parents[2]/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class RoutingBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.r=json.loads((OUT/'n01-shared-routing-boundaries.json').read_text())
    def test_all_identities_preserved_not_final_middle(self):
        old=json.loads((OUT/'n01-shared-end-plan.json').read_text())
        self.assertEqual([r['id'] for r in self.r['endpoints']],[r['id'] for r in old['endpoints']])
        self.assertEqual(len(self.r['portions']),123);self.assertEqual(len(self.r['endpoints']),246)
        self.assertFalse(self.r['unresolved_routing_boundaries']);self.assertFalse(self.r['N01_complete'])
        self.assertFalse(self.r['physical_pass']);self.assertFalse(self.r['native_changed'])
    def test_jackets_do_not_become_fabricated_pads(self):
        for r in self.r['endpoints']:
            if r['pose_status'] in ('CURRENT_JACKET_BOUNDARY_SOLDER_PAD_REMAINS_SEPARATE','CURRENT_SHARED_INLINE_JACKET_INTERNAL_ACCOUNTING_SEPARATE'):
                self.assertIsNone(r['point_mm']);self.assertIsNotNone(r['jacket_routing_point_mm'])
            self.assertAlmostEqual(math.sqrt(sum(v*v for v in r['routing_exit_axis'])),1)
        balance=self.r['balance_factory_contract'];self.assertTrue(balance['not_in_existing_123_portions_or_246_ends'])
        self.assertFalse(balance['physical_GTech_pinout_assigned']);self.assertEqual(len(balance['branches']),4)
    def test_factory_capacity_is_not_extra_stock(self):
        self.assertEqual(len(self.r['received_factory4MTA_curves']),8)
        self.assertTrue(all(r['nominal_remaining_before_trim_mm']>=0 for r in self.r['received_factory4MTA_curves']))
        self.assertTrue(self.r['source_920_accounting']['not_an_extra_conductor_or_stock_purchase'])
        for r in self.r['endpoints']:
            if r['wire']=='W043':
                self.assertEqual(r['protected_source_radius_mm'],1.7)
                self.assertEqual(r['protected_source_project_R_mm'],6)
                self.assertTrue(r['no_new_HELU_type_or_R_inferred_from_station_port'])


if __name__=='__main__':unittest.main()
