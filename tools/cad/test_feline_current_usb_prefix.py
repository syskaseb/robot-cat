import math,unittest
import numpy as np
from fit_feline_current_usb_space import pi_prefix,bus_prefix,scoring_points,biarc_join


class CoupledUSBPrefix(unittest.TestCase):
    def test_spatial_biarc_preserves_endpoints_tangents_and_exact_R(self):
        p=np.array([0.,0,0]);q=np.array([60.,60,20]);t=np.array([1.,0,0]);u=np.array([0.,1.,0])
        for ratio in (.1,.5,1.,2.,10.):
            j=biarc_join(p,t,q,u,ratio);a,b=j['arcs']
            self.assertTrue(np.allclose(a['points_mm'][0],p));self.assertTrue(np.allclose(b['points_mm'][0],q))
            self.assertTrue(np.allclose(a['points_mm'][-1],b['points_mm'][-1]))
            self.assertTrue(np.allclose(np.array(a['junction_tangent']),-np.array(b['junction_tangent'])))
            self.assertTrue(np.allclose(a['start_tangent'],t));self.assertTrue(np.allclose(b['start_tangent'],-u))
            for arc in (a,b):
                centre=np.array(arc['start_mm'])+arc['R_mm']*np.array(arc['normal'])
                self.assertTrue(np.allclose(np.linalg.norm(np.array(arc['points_mm'])-centre,axis=1),arc['R_mm']))
                self.assertAlmostEqual(arc['length_mm'],arc['R_mm']*arc['angle_rad'])

    def test_variable_angles_keep_residual_point_count_constant(self):
        for angle in (0,.001,.05,.1,.3,.5,math.pi/2):
            _,_,p,_=pi_prefix([0,0,0],angle,-1.)
            _,_,b,_=bus_prefix([100,0,0],angle,-2.)
            points,weights=scoring_points(p,np.zeros((193,3)),b)
            self.assertEqual(len(points),299);self.assertEqual(len(weights),299)
            self.assertEqual(weights[0],0);self.assertTrue(np.all(weights[53:246]==1))
    def test_zero_sweep_retains_three_entry_and_full_nine(self):
        q=np.array([1.,2.,3.]);tip,t,points,L=pi_prefix(q,0,-1.)
        self.assertTrue(np.allclose(t,[-1,0,0]));self.assertTrue(np.allclose(tip,q+[-12,0,0]))
        self.assertEqual(L,12);self.assertTrue(np.allclose(points[-1],tip))
    def test_partial_turn_does_not_reduce_R_or_grip(self):
        q=np.array([1.,2.,3.]);angle=math.pi/6;clock=-math.pi/3
        tip,t,points,L=pi_prefix(q,angle,clock);b=np.array([0,math.cos(clock),math.sin(clock)])
        a=q+[-3,0,0];arc=points[2:43];centre=a+30*b
        self.assertTrue(np.allclose(np.linalg.norm(arc-centre,axis=1),30))
        self.assertAlmostEqual(np.linalg.norm(t),1)
        self.assertAlmostEqual(np.linalg.norm(points[-1]-points[-10]),9)
        self.assertAlmostEqual(L,12+30*angle);self.assertTrue(np.allclose(points[-1],tip))


if __name__=='__main__':unittest.main()
