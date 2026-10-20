import unittest
import numpy as np
from plan_feline_tangent_corridor_network import transitions
from feline_corridor_delta import filter_existing
from feline_bundle_sections import certificate,square


class CorridorDelta(unittest.TestCase):
    def test_identical_field_reuses_all_existing_primitives(self):
        free=np.ones((13,13,13),bool);ids,g=transitions(free,4)
        actual,r=filter_existing(ids,g,free,4)
        self.assertEqual((actual!=g).nnz,0);self.assertEqual(r['removed_by_changed_space'],0)

    def test_changed_cells_remove_edges_without_inventing_new_geometry(self):
        free=np.ones((13,13,13),bool);ids,g=transitions(free,4);free[4,4,4]=False
        actual,r=filter_existing(ids,g,free,4)
        self.assertGreater(r['removed_by_changed_space'],0);self.assertLess(actual.nnz,g.nnz)
        self.assertEqual(actual.multiply(g).nnz,actual.nnz)

    def test_four_helu_keep_inner_wire_radius_in_r32(self):
        r=certificate(square(2.1),[2.1]*4,[25.2]*4,6,32)
        self.assertTrue(r['section_and_turn_fit']);self.assertGreater(r['guaranteed_minimum_wire_bend_mm'],25.2)


if __name__=='__main__':unittest.main()
