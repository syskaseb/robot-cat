import unittest
import FreeCAD as A
import Part
from current_bank_datums import datums,nominal_sweep,bounds


class BankDatumTests(unittest.TestCase):
    def scene(self):
        result={}
        for side,y in [('L',62),('R',-62)]:
            for i in range(1,7):
                x=i*30;root=f'F_{side}{i}_CP2'
                for suffix,size,origin in [('Housing',[28,15,28.5],[x-14,y-7.5,97.5]),
                    ('ATO',[19.1,5.1,18.8],[x-9.55,y-2.55,126]),
                    ('IN',[10,10,24],[x-5,y+2,73.5]),('OUT',[10,6,22],[x-5,y-10,75.5])]:
                    result[root+'_'+suffix+'/0/0']=Part.makeBox(*size,A.Vector(*origin))
        return result

    def test_all_twelve_use_actual_placed_centres_not_58(self):
        rows=datums(self.scene());self.assertEqual(len(rows),12)
        self.assertEqual({r['centre_xy_mm'][1] for r in rows},{62,-62})
        for r in rows:
            b=bounds(nominal_sweep(r));self.assertAlmostEqual((b[1]+b[4])/2,r['centre_xy_mm'][1])
            self.assertAlmostEqual(b[5],179.8)

    def test_inconsistent_fuse_placement_is_rejected(self):
        scene=self.scene();scene['F_L1_CP2_ATO/0/0'].translate(A.Vector(0,-4,0))
        with self.assertRaises(AssertionError):datums(scene)

    def test_incomplete_bank_is_not_accepted(self):
        scene=self.scene();scene.pop('F_R6_CP2_OUT/0/0')
        with self.assertRaises(AssertionError):datums(scene)


if __name__=='__main__':unittest.main()
