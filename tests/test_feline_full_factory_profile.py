import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from plan_feline_full_factory_domains import full_profile_points


class FullFactoryProfile(unittest.TestCase):
    def test_arc_and_full_straight_sleeve(self):
        q=np.array([10,20,30]);d=np.array([1,0,0]);b=np.array([0,1,0])
        parts,end,tip=full_profile_points(q,d,b,9)
        np.testing.assert_allclose(end,q+d*21.4+b*12.4)
        np.testing.assert_allclose(tip,end+b*14)
        self.assertAlmostEqual(np.linalg.norm(parts['sleeve'][-1]-parts['sleeve'][0]),20)
        np.testing.assert_allclose(parts['sleeve'][0],end)
        self.assertAlmostEqual(np.linalg.norm(parts['custom'][-1]-parts['custom'][0]),26)
        np.testing.assert_allclose(parts['custom'][0],tip-b*8)

    def test_every_sampled_first_fits_nominal100_not_supplier_guarantee(self):
        for first in (9,18,27,36,45,54,63):
            self.assertLessEqual(3+first+12.4*np.pi/2+14,100)

    def test_rigid_rotated_geometry(self):
        q=np.array([0.,0,0]);d=np.array([0.,0,-1]);b=np.array([1.,1,0])/np.sqrt(2)
        parts,end,tip=full_profile_points(q,d,b,36)
        self.assertAlmostEqual(float(np.dot(d,b)),0)
        np.testing.assert_allclose(end,q+d*48.4+b*12.4)
        np.testing.assert_allclose(parts['factory'][0],q)
        np.testing.assert_allclose(parts['factory'][-1],tip)


if __name__=='__main__':unittest.main()
