import sys
import unittest
from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from plan_feline_atlas_corridor_guide import grid_graph


class AtlasGraph(unittest.TestCase):
    def test_no_edge_through_blocked_cell(self):
        m=np.ones((3,1,1),dtype=bool);m[1,0,0]=False
        ids,r,c,w=grid_graph(m)
        self.assertEqual(len(r),0)
        self.assertEqual(ids[1,0,0],-1)

    def test_metric_and_connectivity(self):
        ids,r,c,w=grid_graph(np.ones((3,2,1),dtype=bool),4)
        g=coo_matrix((w,(r,c)),shape=(6,6)).tocsr()
        d=dijkstra(g,indices=int(ids[0,0,0]))
        self.assertEqual(d[ids[2,1,0]],12)


if __name__=='__main__':unittest.main()
