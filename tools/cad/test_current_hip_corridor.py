"""Fast contracts for one asymmetric Hip architecture, no CAD rebuild/writes."""
import copy,math,unittest
from plan_current_underframe_hip import family,hip_curve
from plan_current_moving_looms import add,sub,rotation


class HipCorridorContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.rows=family('fixed-high-moving-low')

    def test_every_angle_preserves_length_radius_and_both_grip_lands(self):
        self.assertEqual(len(self.rows),12)
        for r in self.rows:
            for angle in range(-15,16):
                q=hip_curve(r,angle);self.assertIsNotNone(q,(r['section'],angle))
                self.assertAlmostEqual(sum(p['length_mm'] for p in q),190,places=5)
                self.assertGreaterEqual(min(p.get('radius_mm',1e9) for p in q),31)
                self.assertAlmostEqual(q[0]['length_mm'],9)
                self.assertAlmostEqual(q[-1]['length_mm'],9)

    def test_no_root_teleport_and_no_broken_join(self):
        for r in self.rows:
            for angle in (-15,0,15):
                q=hip_curve(r,angle);pv=r['pivot_mm']
                target=add(pv,rotation(sub(r['moving_anchor_rest_world_mm'],pv),r['joint_axis'],angle))
                self.assertLess(math.dist(q[0]['start'],r['fixed_anchor_world_mm']),1e-7)
                self.assertLess(math.dist(q[-1]['end'],target),1e-7)
                for a,b in zip(q,q[1:]):self.assertLess(math.dist(a['end'],b['start']),1e-7)

    def test_high_root_is_fixed_not_a_moving_mast(self):
        before=copy.deepcopy(self.rows)
        for r in self.rows:
            self.assertEqual(r['fixed_anchor_world_mm'][2],150)
            self.assertEqual(r['moving_anchor_rest_world_mm'][2],65)
            hip_curve(r,15)
        self.assertEqual(self.rows,before)


if __name__=='__main__':unittest.main()
