import sys
import unittest
from pathlib import Path
import numpy as np
from scipy.interpolate import make_interp_spline
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from feline_cubic_curvature import extrema,exact_length,clamped_knots


class CubicCurvature(unittest.TestCase):
    def test_straight(self):
        c=np.array([[0,0,0],[10,0,0],[20,0,0],[30,0,0]],float);k=clamped_knots(4)
        r=extrema(k,c);self.assertTrue(r['regular']);self.assertIsNone(r['minimum_radius_mm'])
        self.assertAlmostEqual(exact_length(k,c)[0],30)

    def test_interior_parabola_extremum_not_only_endpoints(self):
        u=np.linspace(0,1,4);c=np.column_stack((u,(u-.4)**2,np.zeros(4)));b=make_interp_spline(u,c,k=3)
        r=extrema(b.t,b.c);self.assertAlmostEqual(r['minimum_radius_mm'],.5,places=7)
        self.assertAlmostEqual(r['spans'][0]['maximum_u'],.4,places=6)

    def test_scaled_rotated_curve(self):
        u=np.linspace(0,1,4);b=make_interp_spline(u,np.column_stack((u,(u-.4)**2,np.zeros(4))),k=3)
        rotation=np.array([[0,0,1],[1,0,0],[0,1,0]])
        c=(b.c@rotation.T)*10+np.array([5,7,9]);self.assertAlmostEqual(extrema(b.t,c)['minimum_radius_mm'],5,places=6)

    def test_cusp_is_not_infinite_radius_PASS(self):
        c=np.array([[0,0,0],[0,0,0],[0,0,0],[1,0,0]],float)
        self.assertFalse(extrema(clamped_knots(4),c)['regular'])


if __name__=='__main__':unittest.main()
