import unittest
import FreeCAD as A
import Part
from current_bank_datums import datums,bounds
from test_current_bank_datums import BankDatumTests
from plan_individual_bank_seats import seats


class SeatTests(unittest.TestCase):
    def test_catalog_two_mm_seats_remain_inside_own_flange(self):
        placed=datums(BankDatumTests().scene());q=seats(placed)
        self.assertEqual(len(q),12)
        for r in placed:
            p=q[r['id']];x,y=r['centre_xy_mm'];z=r['flange_top_z_mm']
            self.assertEqual(bounds(p['body']),[x-14,y-7.5,z-4,x+14,y+7.5,z-2])
            self.assertAlmostEqual(p['body'].Volume,(28*15-22.2*11.6)*2)
            self.assertIsNone(p['recipe']['root_path']);self.assertTrue(p['recipe']['delivered_fit_gate'])


if __name__=='__main__':unittest.main()
