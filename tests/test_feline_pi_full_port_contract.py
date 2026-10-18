"""Full Pi planning source and assumption boundaries, not CAD clearance."""
import json
import unittest
from pathlib import Path

OUT=Path(__file__).resolve().parents[1]/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class FullPiContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=json.loads((OUT/'n01-pi-full-port-contract.json').read_text())

    def test_all_labelled_primary_components_included(self):
        parts={r['role']:r for r in self.p['parts']}
        self.assertEqual(len(parts),11)
        for n,z in [('USB_A_rear',16),('USB_A_front',16),('Ethernet',13.5),('GPIO_header',8.5)]:
            self.assertEqual(parts[n]['official_drawing_label_Z_mm'],z)
            self.assertTrue(parts[n]['physical_contact_cannot_be_inferred_from_reservation_overlap'])
        self.assertEqual(parts['USB_C']['official_footprint_board_XY_mm'],[6.875,-1.25,15.525,6.15])

    def test_both_power_receiver_bodies_not_tiny_R3_mould(self):
        r=self.p['full_selected_USB_C_receiver']
        self.assertEqual(r['SKU'],'Delock60047')
        self.assertEqual(set(r['reservations_mm']),{'AdapterBody','RetainedK1474Boot'})
        self.assertEqual(r['free_wire_mouths_mm']['W079'],[32.7,-37.15,50.92])
        self.assertEqual(len(self.p['GPIO_endpoints']),5)

    def test_data_plug_is_separate_explicit_fit_assumption(self):
        p=self.p['USB_A_data_plug_budget']
        self.assertEqual(p['catalog_total_mm'],500)
        self.assertFalse(p['manufacturer_mould_dimensions_found'])
        self.assertEqual(p['source_departure_axis'],[1,0,0])
        self.assertFalse(self.p['N01_complete'])
        self.assertFalse(self.p['selected_parts_or_ECAD_changed'])


if __name__=='__main__':unittest.main()
