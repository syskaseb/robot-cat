import unittest
import numpy as np
from scipy.sparse.csgraph import dijkstra
from propose_feline_sparse_corridors import grid_graph


class SparseGraph(unittest.TestCase):
    def test_cannot_jump_a_thin_original_voxel_wall(self):
        free=np.ones((9,9,9),bool);free[3,:,:]=False
        ids,g=grid_graph(free);distance=dijkstra(g,directed=False,indices=int(ids[1,2,2]))
        self.assertFalse(np.isfinite(distance[int(ids[3,2,2])]))
    def test_original_grid_door_is_retained(self):
        free=np.ones((9,9,9),bool);free[3,:,:]=False;free[3,4,4]=True
        ids,g=grid_graph(free);distance=dijkstra(g,directed=False,indices=int(ids[1,2,2]))
        self.assertAlmostEqual(distance[int(ids[3,2,2])],4)
    def test_odd_and_even_shape_and_nonnegative_penalty(self):
        for n in (8,9,12,13):
            free=np.ones((n,n+1,n+2),bool);ids,g=grid_graph(free,np.full(free.shape,3.))
            self.assertGreater(g.nnz,0);self.assertTrue(np.all(g.data>=2))
            self.assertEqual(g.shape[0],free[::2,::2,::2].sum())


if __name__=='__main__':unittest.main()
