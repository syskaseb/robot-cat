import unittest
import numpy as np
from propose_feline_current_corridors import astar,radius_bucket


class GuideMath(unittest.TestCase):
    def test_radius_is_never_rounded_down(self):
        for radius in (1.05,1.1,1.55,1.7,2.1,2.4,2.5,3.1,3.5,5.,6.):
            self.assertGreaterEqual(radius_bucket(radius)+1e-9,radius)
        self.assertEqual(radius_bucket(2.4),2.5)
    def test_goes_around_occupied_solid_cells(self):
        mask=np.ones((9,9,9),bool);mask[4,:7,:7]=False
        r=astar(mask,[1,1,1],[7,1,1],np.full(mask.shape,10.))
        self.assertTrue(r['points']);self.assertGreater(r['length_mm'],6)
        for a,b in zip(r['points'],r['points'][1:]):
            steps=max(abs(x-y) for x,y in zip(a,b))
            for i in range(steps+1):
                p=tuple(int(round(x+(y-x)*i/max(steps,1))) for x,y in zip(a,b));self.assertTrue(mask[p])
    def test_disconnected_is_not_global_infeasibility(self):
        mask=np.ones((7,7,7),bool);mask[3,:,:]=False
        r=astar(mask,[1,1,1],[5,1,1],np.full(mask.shape,10.))
        self.assertFalse(r['points']);self.assertTrue(r['bounded_search_not_infeasibility'])
    def test_penalty_prefers_existing_wire_free_cells(self):
        mask=np.ones((7,7,7),bool);penalty=np.zeros(mask.shape);penalty[3,0:4,0:4]=100
        r=astar(mask,[1,1,1],[5,1,1],np.full(mask.shape,10.),soft_penalty=penalty)
        self.assertTrue(r['points']);self.assertGreater(r['length_mm'],4)
        self.assertTrue(r['weighted_guide_not_proven_shortest'])


if __name__=='__main__':unittest.main()
