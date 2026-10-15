import unittest
from receiver_entry_chambers import blocked


class EntryChamberTests(unittest.TestCase):
    def test_real_w004_required_r10_entry_is_blocked_by_w021_beam(self):
        q=blocked([-119.75,84,121.5],[0,0,-1],10,[-121.25,74.5,113.725,-117.25,90.5,117.725])
        self.assertIsNotNone(q)
        self.assertLess(q['maximum_transverse_before_face_mm'],.75)
        self.assertGreater(min(q['transverse_inside_margins_mm']),1.49)

    def test_no_proof_is_not_clearance_or_generic_bbox_collision(self):
        b=[-121.25,74.5,113.725,-117.25,90.5,117.725]
        self.assertIsNone(blocked([-130,84,121.5],[0,0,-1],10,b))
        self.assertIsNone(blocked([-119.75,84,121.5],[0,0,1],10,b))
        self.assertIsNone(blocked([-119.75,84,121.5],[0,0,-1],2,b))


if __name__=='__main__':unittest.main()
