import unittest
import numpy as np
from receive_feline_current_tangent_links import portal_centres,local_field_proposal
from feline_tangent_routes import arc


class CurvaturePortals(unittest.TestCase):
    def test_heading_and_radius_define_reach_not_nearest_position(self):
        p=portal_centres([0,0,0],[1,0,0],[0,1,0],16)
        self.assertTrue(np.allclose(p[0],[16,16,0]))
        self.assertTrue(np.allclose(portal_centres([0,0,0],[1,0,0],[1,0,0],16)[0],[32,0,0]))
        opposite=portal_centres([0,0,0],[1,0,0],[-1,0,0],16)
        self.assertEqual(len(opposite),4)
        self.assertEqual(len({tuple(v) for v in opposite}),4)
        self.assertTrue(all(abs(v[0])<1e-8 and abs(np.linalg.norm(v)-32)<1e-8 for v in opposite))

    def test_tilted_actual_departure_keeps_its_tangent_and_circle_radius(self):
        d=np.array([0.,-.5,-np.sqrt(.75)])
        for t in np.vstack((np.eye(3),-np.eye(3))):
            p=portal_centres([10,20,30],d,t,16)[0]
            r=arc([10,20,30],d,p)
            self.assertAlmostEqual(r['radius'],16,places=6)
            self.assertTrue(np.allclose(r['end_tangent'],t,atol=1e-6))

    def test_local_hold_never_becomes_clearance_and_foreign_holds_survive(self):
        fields={k:np.full((24,24,24),100.) for k in ('rigid_signed_distance','motion36_signed_distance','outer_distance')}
        fields.update(origin_mm=np.zeros(3),inside=np.ones((24,24,24),bool))
        q=np.array([2.,2.,2.]);points=np.array([q,[5.,2.,2.],[18.,2.,2.]])
        fields['rigid_signed_distance'][2,2,2]=-100
        r=local_field_proposal(points,1.,fields,q)
        self.assertEqual(r['status'],'LOCAL_RIGID_FIELD_HOLD_EXACT_WHOLE_LINK_REQUIRED')
        self.assertTrue(r['exact_entire_link_NOT_received']);self.assertEqual(r['skipped_actual_geometry_samples'],0)
        fields['rigid_signed_distance'][18,2,2]=-100
        self.assertIsNone(local_field_proposal(points,1.,fields,q))
        fields['rigid_signed_distance'][18,2,2]=100
        fields['motion36_signed_distance'][2,2,2]=-100
        self.assertIsNone(local_field_proposal(points,1.,fields,q))


if __name__=='__main__':unittest.main()
