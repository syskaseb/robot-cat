"""Regression: a wire-only obstruction must block shared graph primitives."""
import unittest
import numpy as np
from plan_feline_current_joint_tangent_space import available_room
from plan_feline_tangent_corridor_network import transitions


class HarnessRoom(unittest.TestCase):
    def field(self):
        return {k:np.full((9,9,9),100.) for k in (
            'rigid_signed_distance','motion36_signed_distance',
            'outer_distance','harness_signed_distance')}

    def test_wire_obstruction_between_clear_nodes_blocks_edge(self):
        f=self.field();f['harness_signed_distance'][2,0,0]=0.
        radius=1.55
        self.assertLess(available_room(f)[2,0,0], radius)
        ids,graph=transitions(available_room(f)>=radius,4)
        self.assertEqual(graph[ids[0,0,0]*6,ids[1,0,0]*6],0)

    def test_existing_rigid_motion_outer_clearances_are_preserved(self):
        for key,allowance in [('rigid_signed_distance',2.45),
                              ('motion36_signed_distance',2.45),
                              ('outer_distance',4.45),('harness_signed_distance',1.4)]:
            f=self.field();f[key][0,0,0]=5.
            self.assertAlmostEqual(available_room(f)[0,0,0],5.-allowance)

    def test_missing_harness_fails_closed(self):
        f=self.field();del f['harness_signed_distance']
        with self.assertRaises(KeyError):available_room(f)


if __name__=='__main__':unittest.main()
