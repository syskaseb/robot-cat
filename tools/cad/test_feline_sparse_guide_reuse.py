import unittest
import numpy as np
from propose_feline_sparse_corridors import guide_cells_clear


class RecheckGuide(unittest.TestCase):
    def test_intermediate_blocked_cell_is_not_skipped(self):
        free=np.ones((7,7,7),bool);origin=np.zeros(3);points=[[0,2,2],[6,2,2]]
        self.assertTrue(guide_cells_clear(points,origin,free))
        free[3,2,2]=False
        self.assertFalse(guide_cells_clear(points,origin,free))

    def test_diagonal_and_outside_are_not_accepted(self):
        free=np.ones((7,7,7),bool);origin=np.zeros(3)
        self.assertFalse(guide_cells_clear([[0,0,0],[2,2,0]],origin,free))
        self.assertFalse(guide_cells_clear([[-1,0,0],[2,0,0]],origin,free))


if __name__=='__main__':unittest.main()
