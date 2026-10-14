import math
import unittest
import FreeCAD as A
from spatial_down_up_flex import build
from plan_current_moving_looms import rotation, add, mul, exact_turn_to
import current_body_fanout_material as M


class SpatialFlexTests(unittest.TestCase):
    def test_both_sides_all31_tangencies_endpoints_and_lengths(self):
        for side in (-1,1):
            start=[-50,-side*55,41]
            for angle in range(-15,16):
                exit=rotation([0,0,1],[1,0,0],angle)
                bridge=[-.8,side*.6,0]
                for middle_length in (85,90,95):
                    first=exact_turn_to(add(start,[0,0,-60]),[0,0,-1],bridge,31.5)
                    second=exact_turn_to(add(first['end'],mul(bridge,middle_length)),bridge,exit,31.5)
                    end=add(second['end'],mul(exit,50))
                    length=60+middle_length+50+first['length_mm']+second['length_mm']
                    parts=build(start,end,exit,length)
                    self.assertIsNotNone(parts,(side,angle,length))
                    edges=[M.P.wire([p]).Edges[0] for p in parts]
                    self.assertAlmostEqual(sum(p['length_mm'] for p in parts),length,places=6)
                    self.assertLess(A.Vector(*parts[-1]['end']).distanceToPoint(A.Vector(*end)),1e-6)
                    for a,b in zip(edges,edges[1:]):
                        self.assertGreater(a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter)),1-1e-7)

    def test_impossible_short_curve_rejected(self):
        self.assertIsNone(build([0,0,0],[20,10,0],[0,0,1],30))


if __name__=='__main__': unittest.main()
