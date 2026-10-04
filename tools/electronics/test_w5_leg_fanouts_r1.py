import unittest
from w5_leg_fanouts_r1 import wago_datum, termination, CORE_OD, BUNDLE_OD
import math


class LegFanoutTests(unittest.TestCase):
    def test_physical_order_preserves_logical_rear_cages(self):
        b={'D_RR_design':[96,-49.5,109,126,-30.5,118]}
        self.assertEqual(wago_datum('D_RR.3',b),([97.5,-30.5,113.5],1))
        self.assertEqual(wago_datum('D_RR.2',b),([104.25,-30.5,113.5],1))
        self.assertEqual(wago_datum('D_RR.4',b),([117.75,-30.5,113.5],1))

    def test_front_ground_swap_and_inner_face(self):
        b={'FR_G_design':[-48,-49.5,109,-18,-30.5,118],
           'FL_G_design':[-48,30.5,109,-18,49.5,118]}
        self.assertEqual(wago_datum('FR_G.2',b),([-46.5,-30.5,113.5],1))
        self.assertEqual(wago_datum('FR_G.1',b),([-39.75,-30.5,113.5],1))
        self.assertEqual(wago_datum('FL_G.2',b),([-39.75,30.5,113.5],-1))

    def test_bundle_contains_three_provisional_cores(self):
        self.assertGreater(BUNDLE_OD,CORE_OD*(1+2/math.sqrt(3)))
        self.assertGreater(CORE_OD*(1+2/math.sqrt(3)),5)

    def test_terminal_does_not_invent_manufacturer_strip(self):
        t=termination('V','W020','F_FL1.out')
        self.assertIsNone(t['strip_mm'])
        self.assertTrue(t['strip_source_pending'])
        self.assertTrue(t['local_bank_exit_is_not_a_splice'])
        self.assertEqual(termination('G','W019','FL_G.2')['strip_mm'],11)


if __name__=='__main__':unittest.main()
