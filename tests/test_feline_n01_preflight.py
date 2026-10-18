"""Pure, deterministic checks for N01 bounds; no FreeCAD or ROS required."""
import importlib.util
import math
import random
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('n01',Path(__file__).resolve().parents[1]/'tools/cad/compose_feline_n01_allocation.py')
n01=importlib.util.module_from_spec(spec);spec.loader.exec_module(n01)


class PreflightTests(unittest.TestCase):
    def test_quarter_arc_tangents(self):
        r=6
        part=dict(kind='arc',start=[0,0,0],mid=[r/math.sqrt(2),r*(1-1/math.sqrt(2)),0],end=[r,r,0])
        self.assertLess(math.dist(n01.tangent(part,True),[1,0,0]),1e-9)
        self.assertLess(math.dist(n01.tangent(part,False),[0,1,0]),1e-9)

    def test_degenerate_and_straight_bounds(self):
        self.assertEqual(n01.curvature_chord_bound([0,0,0],[1,0,0],[0,0,0],[0,1,0],6)['lower_bound_mm'],0)
        self.assertEqual(n01.curvature_chord_bound([0,0,0],[1,0,0],[40,0,0],[1,0,0],6)['lower_bound_mm'],40)

    def test_short_curve_uses_non_overcounting_fallback(self):
        lb=n01.curvature_chord_bound([0,0,0],[1,0,0],[6,6,0],[0,1,0],6)
        self.assertFalse(lb['intervals_disjoint'])
        self.assertLessEqual(lb['lower_bound_mm'],6*math.pi/2)

    def test_known_pi_candidate_fails_before_CAD(self):
        lb=n01.curvature_chord_bound([-40,0,8],[0,0,-1],[-33.5,14,-8],[0,1,0],6)
        self.assertGreater(6.5+lb['lower_bound_mm']+9+12,50)
        out=n01.curvature_chord_bound([-40,0,68.5],[0,0,1],[-95,0,43],[1,0,0],6)
        self.assertGreater(3+out['lower_bound_mm']+17,84.5)

    def test_bound_never_exceeds_constructed_bounded_curves(self):
        rng=random.Random(20261018)
        for _ in range(1000):
            x=y=theta=length=0.0
            for _ in range(rng.randint(2,12)):
                line=rng.uniform(0,30);x+=line*math.cos(theta);y+=line*math.sin(theta);length+=line
                turn=rng.uniform(-1.2,1.2);r=rng.uniform(6,30);sign=1 if turn>=0 else -1
                x+=sign*r*(math.sin(theta+turn)-math.sin(theta))
                y+=sign*r*(-math.cos(theta+turn)+math.cos(theta));theta+=turn;length+=r*abs(turn)
            lb=n01.curvature_chord_bound([0,0,0],[1,0,0],[x,y,0],[math.cos(theta),math.sin(theta),0],6)
            self.assertLessEqual(lb['lower_bound_mm'],length+1e-7)


if __name__=='__main__':unittest.main()
