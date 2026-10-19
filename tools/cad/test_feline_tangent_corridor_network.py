import unittest
import numpy as np
from plan_feline_tangent_corridor_network import primitive,transitions


class Tangents(unittest.TestCase):
    def test_arc_has_real_radius_and_correct_tangents(self):
        p=primitive([1,0,0],[0,1,0],16)
        self.assertTrue(np.allclose(p[0],[0,0,0]))
        self.assertTrue(np.allclose(p[-1],[16,16,0]))
        self.assertTrue(np.allclose(np.linalg.norm(p-[0,16,0],axis=1),16))
        self.assertLess(np.linalg.norm(np.diff(p,axis=0),axis=1).max(),.5)

    def test_no_corner_shortcut_through_blocked_intermediate_cell(self):
        free=np.ones((13,13,13),bool);free[2,:,:]=False
        ids,graph=transitions(free,4)
        start=ids[0,1,1]*6;target=ids[1,1,1]*6
        self.assertEqual(graph[start,target],0)


if __name__=='__main__':unittest.main()
