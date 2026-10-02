import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class F0Source(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=json.loads((ROOT/'hardware/electronics/full-cat/f0-factory-leads-r1/interface.json').read_text(encoding='utf-8'))
    def test_exact_SKU_not_red_variant(self):
        self.assertEqual(self.data['part_number'],'FHAC0002ZXJ');self.assertEqual(self.data['wire_AWG'],12)
        self.assertEqual(self.data['factory_insulation_colour'],'orange')
    def test_nominal_conversion_not_guarantee(self):
        self.assertAlmostEqual(self.data['factory_each_lead_nominal_mm'],3.524*25.4)
        self.assertAlmostEqual(self.data['factory_each_end_strip_nominal_mm'],.25*25.4)
        self.assertIsNone(self.data['length_tolerance_mm']);self.assertIsNone(self.data['guaranteed_minimum_each_lead_mm'])
    def test_no_false_route_or_protection_acceptance(self):
        self.assertIsNone(self.data['selected_cut_lengths_mm'])
        for f in ('W5_complete','E3_complete','physical_pass','purchases_changed'):self.assertFalse(self.data[f])
        self.assertTrue(self.data['rating_is_not_selected_F0_fuse_or_E3_approval'])
if __name__=='__main__':unittest.main()
