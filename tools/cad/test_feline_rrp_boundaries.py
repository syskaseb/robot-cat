import unittest
from compose_feline_rrp_boundaries import current
from feline_adjudicated_boundaries import current as before


class RRBoundaries(unittest.TestCase):
    def test_four_actual_caps_do_not_move_any_electrical_identity(self):
        base,rows,_=current();_,old,_=before()
        self.assertEqual(len(base['portions']),123);self.assertEqual(len(rows),246)
        changed=[]
        for a,b in zip(old,rows):
            for key in ('id','wire','portion_id','endpoint','group','point_mm','departure_axis'):
                self.assertEqual(a.get(key),b.get(key))
            if a!=b:
                changed.append(b['id']);self.assertEqual(b['grip_kind'],'CURVED_FULL9')
                self.assertIsNone(b['jacket_grip9_mm']);self.assertIsNone(b['grip_axis'])
                self.assertAlmostEqual(b['jacket_grip9_curve_parts'][0]['length_mm'],9)
                self.assertAlmostEqual(b['routing_exit_mm'][2],94.02726902604963)
                self.assertTrue(b['support_load_path_OPEN'])
        self.assertEqual(len(changed),4)


if __name__=='__main__':unittest.main()
