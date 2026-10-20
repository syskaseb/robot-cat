import math,unittest
import numpy as np
import FreeCAD as A
from feline_spatial_csc import spatial_csc
from feline_source_saddles import segment


class SpatialCSC(unittest.TestCase):
    def check_curve(self,p,a,q,b):
        rows=spatial_csc(p,a,q,b);edges=[segment(r) for r in rows]
        self.assertTrue(np.allclose(rows[0]['start'],p,atol=2e-6))
        self.assertTrue(np.allclose(rows[-1]['end'],q,atol=2e-6))
        self.assertLess((edges[0].tangentAt(edges[0].FirstParameter)-A.Vector(*a)).Length,2e-6)
        self.assertLess((edges[-1].tangentAt(edges[-1].LastParameter)-A.Vector(*b)).Length,2e-6)
        for left,right in zip(edges,edges[1:]):
            self.assertLess((left.tangentAt(left.LastParameter)-right.tangentAt(right.FirstParameter)).Length,2e-6)
        for r in rows:
            if r['kind']=='arc':self.assertAlmostEqual(r['radius_mm'],12.4)
        return sum(e.Length for e in edges)

    def test_ground_three_dimensional_endpoint_heading(self):
        length=self.check_curve([128,66,80.595],[0,0,1],[5.7,0,68.5],[1,0,0])
        self.assertGreaterEqual(length,math.dist([128,66,80.595],[5.7,0,68.5]))

    def test_upper_source_opposed_direction_does_not_require_giant_biarc(self):
        self.check_curve([-99.57,33.85,100.858],[-math.sqrt(.5),0,math.sqrt(.5)],
                         [10,29.3,66.5],[0,-1,0])

    def test_portal_to_module_end_with_prescribed_radius(self):
        self.check_curve([42.77,31.25,42],[0,0,1],[10,-19.3,66.5],[0,1,0])


if __name__=='__main__':unittest.main()
