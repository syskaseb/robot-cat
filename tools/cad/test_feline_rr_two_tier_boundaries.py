import unittest
import numpy as np
from compose_feline_rr_two_tier_boundaries import compose,parent,current
from compose_feline_integrated_boundaries import apply_updates


class RRTwoTierBoundaries(unittest.TestCase):
    def test_actual_current_caps_and_immutable246(self):
        p=compose();_,old,_=parent();rows=apply_updates(old,p['updates']);byid={r['id']:r for r in rows}
        self.assertEqual(len(rows),246);self.assertEqual(len({r['portion_id'] for r in rows}),123)
        self.assertEqual(len(p['updates']),13)
        for a,b in zip(old,rows):
            for key in ('id','wire','portion_id','endpoint','group'):self.assertEqual(a[key],b[key])
            if a['point_mm'] is None:self.assertIsNone(b['point_mm'])
            if a['id'] not in p['updates']:self.assertEqual(a,b)
        for wire,y in (('W072',-88.5),('W073',-83.75),('W074',-79)):
            source=byid[wire+'/body/start'];target=byid[wire+'/body/end']
            self.assertTrue(np.allclose(source['point_mm'],[130,y,98]))
            self.assertTrue(np.allclose(source['routing_exit_mm'],[121,y,98]))
            self.assertTrue(np.allclose(target['routing_exit_mm'],[99.875,y,98]))
            self.assertEqual(target['routing_exit_axis'],[1,0,0])
            self.assertAlmostEqual(target['whole_body_length_mm'],42.375)
            self.assertTrue(source['full_middle_route_accepted']);self.assertTrue(target['full_middle_route_accepted'])
        self.assertFalse(byid['W063/retained0/end']['full_middle_route_accepted'])
        self.assertTrue(np.allclose(byid['W063/retained0/end']['routing_exit_mm'],[99.875,-74.25,98]))
        self.assertFalse(p['N01_complete']);_,r,_=current();self.assertEqual(rows,r)


if __name__=='__main__':unittest.main()
