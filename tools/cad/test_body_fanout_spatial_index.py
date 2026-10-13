"""Hierarchical planning index must not omit any brute-force triangle hit."""
import unittest
import numpy as np
from fast_carrier_reservations import TriangleBucket
from plan_body_fanout_layout import Scene


class SpatialIndexTest(unittest.TestCase):
    def test_new_prefix_names_and_other_wire_clearance(self):
        data=dict(triangles=np.array([[[100.,100,0],[102,100,0],[100,102,0]]]),
                  triangle_ids=np.array([0]),material_names=np.array(['far']),
                  wire_points=np.empty((0,3)),wire_names=np.array([],dtype=str),
                  wire_ids=np.array([],dtype=int),wire_radii=np.array([]),
                  low=np.array([-200]*3),high=np.array([200]*3))
        scene=Scene(data)
        scene.add_points('new/W013/source',np.array([[0.,0,0],[0,0,5]]))
        points=np.array([[0.,0,2.5]])
        row=dict(wire='W013',loom='RL1',bundle_root_world_mm=[-10]*3,receiver_point_mm=[-20]*3)
        self.assertTrue(scene.clear(points,row))
        self.assertFalse(scene.clear(points,dict(row,wire='W014')))

    def test_all_size_levels_and_cell_boundaries(self):
        rng=np.random.default_rng(615)
        triangles=[]
        for scale in (.5,7.9,8.1,27.9,28.1,97.9,98.1,200):
            for _ in range(4):
                c=rng.uniform(-150,150,3)
                triangles.append(c+rng.uniform(-.5,.5,(3,3))*scale)
        triangles=np.asarray(triangles)
        data=dict(triangles=triangles,triangle_ids=np.arange(len(triangles)),
                  wire_points=np.empty((0,3)),wire_names=np.array([]),wire_ids=np.array([],dtype=int),
                  wire_radii=np.array([]),material_names=np.array([str(i) for i in range(len(triangles))]))
        scene=Scene(data)
        brute=TriangleBucket([(t,i) for i,t in enumerate(triangles)])
        points=list(rng.uniform(-180,180,(120,3)))
        for t in triangles:
            points.extend((t[0],t.mean(axis=0),t.mean(axis=0)+[1.2,0,0]))
        for point in points:
            self.assertEqual(scene.material_hit(point) is None,brute.hit(point,(1.25,1.25,1.25)) is None)


if __name__=='__main__':unittest.main()
