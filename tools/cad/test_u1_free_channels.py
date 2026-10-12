import unittest
import plan_u1_free_channels as F
import plan_current_main_pi_wiring as M
from check_u1_common_routes import self_screen


class OpenSpace:
    def clear(self,parts,ignore=()):return True


class ClosedSpace:
    def clear(self,parts,ignore=()):return False


class ChannelTests(unittest.TestCase):
    def test_self_screen_distinguishes_local_neighbours_from_distant_return(self):
        self.assertFalse(self_screen([[i*.25,0,60] for i in range(200)],1))
        self.assertTrue(self_screen([[0,0,60],[10,0,60],[10,10,60],[0,10,60],[0,0,60.1]],1))

    def test_empty_space_preserves_endpoint_tangents_and_curvature(self):
        parts,states=F.search(OpenSpace(),[0,0,60],M.U,[40,0,60],M.U,5,200,max_states=20)
        self.assertIsNotNone(parts)
        self.assertEqual(parts[0]['start'],[0,0,60]);self.assertEqual(parts[-1]['end'],[40,0,60])
        self.assertLess(F.validate(parts,5),200)
        self.assertLessEqual(states,20)

    def test_blocked_scene_terminates_without_partial_route(self):
        parts,states=F.search(ClosedSpace(),[0,0,60],M.U,[40,0,60],M.U,5,200,max_states=20)
        self.assertIsNone(parts);self.assertEqual(states,1)

    def test_disconnected_or_kinked_parts_are_rejected(self):
        with self.assertRaises(AssertionError):F.validate([M.line([0,0,60],[0,0,70]),M.line([1,0,70],[1,0,80])],5)
        with self.assertRaises(AssertionError):F.validate([M.line([0,0,60],[0,0,70]),M.line([0,0,70],[10,0,70])],5)


if __name__=='__main__':unittest.main()
