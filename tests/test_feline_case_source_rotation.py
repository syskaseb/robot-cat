import itertools
import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from receive_feline_global_case_candidates import matrix_rotation,bounds_near,placement


class SourceRotation(unittest.TestCase):
    def test_all_six_are_proper_not_reflections(self):
        dimensions=np.array([51,20.25,22])
        for perm in itertools.permutations(range(3)):
            r=matrix_rotation(perm)
            np.testing.assert_allclose(r.T@r,np.eye(3))
            self.assertAlmostEqual(np.linalg.det(r),1)
            expect=np.empty(3)
            for source,world in enumerate(perm):expect[world]=dimensions[source]
            np.testing.assert_allclose(abs(r)@dimensions,expect)
            self.assertAlmostEqual(placement(r,[0,0,0]).Rotation.Q[0]**2+sum(x*x for x in placement(r,[0,0,0]).Rotation.Q[1:]),1)

    def test_bbox_is_only_a_pair_screen(self):
        a=[np.array([0,0,0]),np.array([1,1,1])]
        b=[np.array([3,0,0]),np.array([4,1,1])]
        self.assertFalse(bounds_near(a,b,1.25))
        self.assertTrue(bounds_near(a,b,2))


if __name__=='__main__':unittest.main()
