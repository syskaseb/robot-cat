import unittest
import FreeCAD as A
import Part
from current_bank_datums import datums,bounds
from test_current_bank_datums import BankDatumTests
from plan_individual_bank_seats import seats


class SeatTests(unittest.TestCase):
    def test_only_r6_corner_changes_no_part_or_whole_panel_movement(self):
        placed=datums(BankDatumTests().scene());old=seats(placed);new=seats(placed,True)
        for key,p in old.items():
            if key!='F_R6_CP2':self.assertEqual(p['recipe'],new[key]['recipe']);continue
            self.assertLess(new[key]['body'].Volume,p['body'].Volume)
            self.assertEqual(bounds(new[key]['body']),bounds(p['body']))
            x,y,z=new[key]['recipe']['centre_mm']
            # Two centre end-strip witnesses remain full2mm; actual delivered
            # snap/force/creep is deliberately not inferred from these cubes.
            for sign in (-1,1):
                strip=Part.makeBox(1,2,2,A.Vector(x+sign*12-.5,y-1,z-4))
                self.assertAlmostEqual(new[key]['body'].common(strip).Volume,4)

    def test_catalog_two_mm_seats_remain_inside_own_flange(self):
        placed=datums(BankDatumTests().scene());q=seats(placed)
        self.assertEqual(len(q),12)
        for r in placed:
            p=q[r['id']];x,y=r['centre_xy_mm'];z=r['flange_top_z_mm']
            self.assertEqual(bounds(p['body']),[x-14,y-7.5,z-4,x+14,y+7.5,z-2])
            self.assertAlmostEqual(p['body'].Volume,(28*15-22.2*11.6)*2)
            self.assertIsNone(p['recipe']['root_path']);self.assertTrue(p['recipe']['delivered_fit_gate'])


if __name__=='__main__':unittest.main()
