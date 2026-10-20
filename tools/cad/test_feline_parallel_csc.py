"""Endpoint geometry, not collision or factory-stock approval."""
import math
import unittest
import numpy as np
from plan_feline_jpwm_factory_middle import parallel_csc,planar_csc
from feline_source_saddles import segment


class ParallelCSC(unittest.TestCase):
    def test_short_offset_has_two_roots_inside_equal_sign_endpoints(self):
        parts=parallel_csc([55.17,38.4,-18.5],[95.7,0,-18.5],[1,0,0])
        self.assertTrue(np.allclose(parts[0]['start'],[55.17,38.4,-18.5]))
        self.assertTrue(np.allclose(parts[-1]['end'],[95.7,0,-18.5]))
        self.assertEqual(len(parts),3)
        self.assertGreater(sum(segment(p).Length for p in parts),math.hypot(40.53,38.4))
        for p in parts:
            if p['kind']=='arc':self.assertAlmostEqual(p['radius_mm'],12.4)
        edges=[segment(p) for p in parts]
        for a,b in zip(edges,edges[1:]):
            self.assertLess((a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length,1e-7)

    def test_previously_bracketed_large_offset_still_works(self):
        parts=parallel_csc([0,0,0],[90,80,0],[1,0,0])
        self.assertTrue(np.allclose(parts[-1]['end'],[90,80,0]))

    def test_impossible_prescribed_radius_is_not_relaxed(self):
        with self.assertRaisesRegex(ValueError,'prescribed radius'):
            parallel_csc([0,0,0],[1,1,0],[1,0,0])

    def test_behind_receiver_keeps_full_circles_and_tangents(self):
        parts=planar_csc([42.77,30,-12.5],[0,1,0],[116,-24.3,-12.5],[0,1,0])
        self.assertTrue(np.allclose(parts[0]['start'],[42.77,30,-12.5]))
        self.assertTrue(np.allclose(parts[-1]['end'],[116,-24.3,-12.5]))
        edges=[segment(p) for p in parts]
        self.assertLess((edges[0].tangentAt(edges[0].FirstParameter)-__import__('FreeCAD').Vector(0,1,0)).Length,1e-7)
        self.assertLess((edges[-1].tangentAt(edges[-1].LastParameter)-__import__('FreeCAD').Vector(0,1,0)).Length,1e-7)
        for a,b in zip(edges,edges[1:]):
            self.assertLess((a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length,1e-7)
        self.assertTrue(all(p.get('radius_mm',12.4)>=12.4 for p in parts))


if __name__=='__main__':unittest.main()
