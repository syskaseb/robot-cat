import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from feline_tangent_routes import arc,biarc,quarter_prefix,samples,length,min_radius,norm,sub,reverse


class TangentRoutes(unittest.TestCase):
    def test_quarter_known_length_endpoints(self):
        p=quarter_prefix((0,0,0),(1,0,0),(0,1,0))
        self.assertAlmostEqual(length(p),12+15*math.pi)
        self.assertEqual(p[-1]['end'],[33,39,0])
        self.assertAlmostEqual(min_radius(p),30)

    def test_circle_is_recovered_by_biarc(self):
        for r in (.25,.5,1,2,4):
            p=biarc((0,0,0),(1,0,0),(30,30,0),(0,1,0),r)
            self.assertAlmostEqual(length(p),15*math.pi)
            self.assertAlmostEqual(min_radius(p),30)
            self.assertLess(norm(sub(p[0]['end'],p[1]['start'])),1e-9)

    def test_arc_end_and_reverse(self):
        s=arc((1,2,3),(0,1,0),(1,32,33));points=list(samples(s))
        self.assertLess(norm(sub(points[-1],s['end'])),1e-8)
        self.assertLess(norm(sub(reverse(s)['end'],s['start'])),1e-8)

    def test_no_backward_straight_or_loop(self):
        with self.assertRaises(ValueError):arc((0,0,0),(1,0,0),(-1,0,0))
        with self.assertRaises(ValueError):arc((0,0,0),(1,0,0),(-1,1,0))

    def test_3d_tangent_join_and_endpoint(self):
        p=biarc((0,0,0),(1,0,0),(100,80,70),(0,0,1))
        self.assertLess(norm(sub(list(samples(p[-1]))[-1],(100,80,70))),1e-8)
        self.assertGreater(min_radius(p),0)


if __name__=='__main__':unittest.main()
