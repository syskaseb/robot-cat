"""Geometric contracts for rigid channels, without claiming obstacle clearance."""
import math
import unittest
from rigid_tangent_channel import candidates, turn


class RigidChannels(unittest.TestCase):
    def test_quarter(self):
        p,d=turn([0,0,0],[1,0,0],[0,1,0],math.pi/2,31.5)
        self.assertLess(math.dist(p[-1]['end'],[31.5,31.5,0]),1e-8)
        self.assertLess(math.dist(d,[0,1,0]),1e-8)
    def test_endpoints_and_radii(self):
        for end in ([90,60,0],[5,38,30],[40,-60,-30],[-20,20,80]):
            rows=candidates([0,0,0],[1,0,0],end,[0,1,0])
            self.assertTrue(rows)
            for row in rows:
                parts=row['parts'];self.assertLess(math.dist(parts[0]['start'],[0,0,0]),1e-6)
                self.assertLess(math.dist(parts[-1]['end'],end),1e-6)
                self.assertGreater(row['guide_mm'],0)
                for p in parts:
                    if p['kind']=='arc':self.assertGreaterEqual(p['radius_mm'],31.5)
                for a,b in zip(parts,parts[1:]):self.assertLess(math.dist(a['end'],b['start']),1e-6)
    def test_nonorthogonal_rejected(self):
        with self.assertRaises(AssertionError):candidates([0,0,0],[1,0,0],[20,20,0],[1,0,0])


if __name__=='__main__':unittest.main()
