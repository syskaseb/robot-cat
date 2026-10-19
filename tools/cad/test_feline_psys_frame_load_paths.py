import unittest
from receive_feline_psys_frame_load_paths import reached


class AnchorGraph(unittest.TestCase):
    def test_each_split_solid_needs_its_own_path(self):
        nodes={'ClampSeat:1/solid:0','Rail/solid:0','Rail/solid:1'}
        edges=[dict(a='ClampSeat:1/solid:0',b='Rail/solid:0')]
        self.assertNotIn('Rail/solid:1',reached(nodes,edges,{'ClampSeat:1/solid:0'}))

    def test_a_different_existing_anchor_is_a_real_load_path(self):
        nodes={'ClampSeat:1/solid:0','ClampSeat:2/solid:0','Rail/solid:1'}
        edges=[dict(a='ClampSeat:2/solid:0',b='Rail/solid:1')]
        self.assertEqual(reached(nodes,edges,{'ClampSeat:1/solid:0','ClampSeat:2/solid:0'}),nodes)


if __name__=='__main__':unittest.main()
