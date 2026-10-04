import unittest
from w5_ground_entries_r1 import profile, THICK


class GroundEntryProfileTest(unittest.TestCase):
    def test_exact_fixed_radius_not_replaced_with_helu(self):
        for wire in THICK:
            p = profile(wire)
            self.assertEqual((p['OD_mm'], p['radius_mm']), (4.2, 21))
            self.assertTrue(p['supplier_radius'])
        self.assertEqual(profile('XA05')['radius_mm'], 15)

    def test_prototype_cables_not_declared_supplier_dimensions(self):
        for wire in ('W003', 'W060', 'W019', 'W069', 'W074'):
            self.assertFalse(profile(wire)['supplier_radius'])
            self.assertEqual(profile(wire)['radius_mm'], 10)
        self.assertEqual(profile('W060')['OD_mm'], 3)
        self.assertEqual(profile('W003')['OD_mm'], 2)


if __name__ == '__main__': unittest.main()
