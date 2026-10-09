"""Analytic routing must not invent a smooth/radius-valid path."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
import open_prototype_source_group as B
from open_prototype_tangent_routes import biarc, terminated, tangent_arc


class TangentRoutes(unittest.TestCase):
    def test_quarter(self):
        p=biarc([0,0,0],B.EAST,[100,100,0],B.NORTH)
        self.assertAlmostEqual(B.check_path(p),math.pi*50)
        self.assertAlmostEqual(B.segment_geometry(p[0])[3],100)

    def test_parallel_3d(self):
        p=biarc([0,0,0],B.EAST,[100,60,30],B.EAST)
        B.check_path(p,[0,0,0],[100,60,30],25.2)
        self.assertGreater(B.dot(B.segment_geometry(p[0])[1],B.EAST),.999999)
        self.assertGreater(B.dot(B.segment_geometry(p[-1])[2],B.EAST),.999999)

    def test_unequal_tangent_lengths(self):
        for ratio in (.25,.5,1,2,4):
            B.check_path(biarc([0,0,0],B.EAST,[100,100,0],B.NORTH,ratio),min_radius=25.2)

    def test_rigid_rotation_preserves_length(self):
        p=biarc([0,0,0],B.EAST,[100,60,30],B.EAST)
        rotate=lambda q:[-q[1]+17,q[2]-3,-q[0]+11]
        q=[{k:rotate(v) if k in ('start','mid','end') else v for k,v in s.items()} for s in p]
        self.assertAlmostEqual(B.check_path(q),B.check_path(p))

    def test_short_bend_rejected(self):
        with self.assertRaises(AssertionError):biarc([0,0,0],B.EAST,[10,10,0],B.NORTH)

    def test_opposite_collinear_rejected(self):
        with self.assertRaises(ValueError):tangent_arc([0,0,0],B.EAST,[-10,0,0])

    def test_terminal_lands_are_straight(self):
        p=terminated([0,0,0],B.EAST,[118,100,0],B.NORTH)
        self.assertEqual(p[0]['kind'],'line');self.assertEqual(p[-1]['kind'],'line')
        self.assertAlmostEqual(B.segment_geometry(p[0])[0],9)
        self.assertAlmostEqual(B.segment_geometry(p[-1])[0],9)
        B.check_path(p,[0,0,0],[118,100,0],25.2)


if __name__=='__main__':unittest.main()
