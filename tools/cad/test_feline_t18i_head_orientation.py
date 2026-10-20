"""Cheap own-nylon interface gate before loading the complete world."""
import unittest
import FreeCAD
from receive_feline_positive_service_deck import open_grip
from receive_feline_mta_tilted_fans import head_above_existing_band


class HeadOrientation(unittest.TestCase):
    def test_both_sides_keep_full_stock_and_actual_band_union(self):
        for side in (-1,1):
            kit=open_grip([104,side*15,-34],[1,0,0],[0,side,0],4.5)
            head,r=head_above_existing_band(kit['band'],kit['head'],side*15)
            self.assertAlmostEqual(head.Volume,5*5.3*4.3,6)
            self.assertEqual(r['head_band_union_solids'],1)
            self.assertGreater(r['actual_existing_band_contact_area_mm2'],13)
            self.assertLess(r['actual_nominal_face_gap_mm'],1e-10)
            self.assertTrue(r['existing_band_pad_root_and_wire_NOT_changed'])


if __name__=='__main__':unittest.main()
