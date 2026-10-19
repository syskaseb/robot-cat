import unittest
import numpy as np
from propose_feline_current_corridors import astar,radius_bucket,macro_boundary,nearest_cell


class GuideMath(unittest.TestCase):
    def test_edt_indices_have_leading_coordinate_axis(self):
        from scipy.ndimage import distance_transform_edt
        free=np.zeros((12,15,11),bool);free[7,8,9]=True
        indices=distance_transform_edt(~free,return_distances=False,return_indices=True)
        self.assertTrue(np.array_equal(nearest_cell(indices,[10,12,10]),[7,8,9]))
    def test_virtual_boundary_does_not_invent_a_nine_mm_land(self):
        row=dict(id='FL/fixed',routing_exit_mm=[1,2,3],routing_exit_axis=[1,0,0],routing_boundary_status='CURRENT_MOUTH_PREFIX_ALLOCATION_OPEN',initial_jacket_land_mm=None)
        q,_,_=macro_boundary(row,{})
        self.assertTrue(np.array_equal(q,[1,2,3]))
    def test_received_lower_custom_uses_exact_prefix_length(self):
        row=dict(id='W026/custom/start',routing_exit_mm=[1,2,3],routing_exit_axis=[-1,0,0])
        q,_,s=macro_boundary(row,{row['id']:dict(point_mm=[1,2,3],prefix_mm=9.25)})
        self.assertTrue(np.array_equal(q,[-8.25,2,3]));self.assertTrue(s.startswith('RECEIVED_'))
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
