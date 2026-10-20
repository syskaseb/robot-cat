import unittest
import numpy as np
from check_feline_current_corridor_links import link,field_test


class CurrentLinks(unittest.TestCase):
    def test_quarter_circle_has_true_radius_and_endpoints(self):
        parts,points,R,ok=link([0,0,0],[1,0,0],[20,20,0],[0,1,0],20)
        self.assertTrue(ok);self.assertAlmostEqual(R,20)
        np.testing.assert_allclose(points[[0,-1]],[[0,0,0],[20,20,0]],atol=1e-8)

    def test_small_radius_not_promoted_by_connected_nodes(self):
        self.assertFalse(link([0,0,0],[1,0,0],[5,5,0],[0,1,0],20)[3])

    def test_outside_is_not_clamped(self):
        fields=dict(origin_mm=np.zeros(3),inside=np.ones((8,8,8),bool))
        result=field_test(np.array([[-1,2,2],[3,2,2]]),1,fields)
        self.assertEqual(result['samples_outside'],1)
        self.assertIn('NOT_PART_COLLISION',result['status'])


if __name__=='__main__':unittest.main()
