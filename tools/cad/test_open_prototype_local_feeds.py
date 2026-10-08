"""Pure shared-route contract: no source pins, fake radius or partial points."""
import math
import unittest
import open_prototype_local_feeds as F


class LocalFeedPlan(unittest.TestCase):
    def setUp(self):
        self.p=F.build_plan()

    def test_nine_distinct_local_roles(self):
        self.assertEqual(len(self.p['rows']),9)
        self.assertEqual(len({r['wire'] for r in self.p['rows']}),9)
        self.assertEqual({r['group'] for r in self.p['rows']},{'HY','HP','TY'})

    def test_all_minimum_bends_and_grips_preserved(self):
        for r in self.p['rows']:
            F.corner_offsets(r['points_mm'],12.6)
            self.assertGreaterEqual(r['first_intact_straight_mm'],9-1e-8)
            self.assertGreaterEqual(r['last_intact_straight_mm'],9-1e-8)
            self.assertAlmostEqual(r['length_mm'],F.rounded_length(r['points_mm'],12.6))

    def test_distinct_yaw_packing_not_three_coincident_paths(self):
        rows=[r for r in self.p['rows'] if r['group']=='HY']
        for i,a in enumerate(rows):
            for b in rows[i+1:]:
                self.assertAlmostEqual(math.dist(a['points_mm'][-1],b['points_mm'][-1]),2.1)

    def test_motor_returns_not_signal_board_ground(self):
        roles={r['wire']:r['logical_source'] for r in self.p['rows']}
        self.assertEqual([roles[k] for k in ('XB13','XB23','XB33')],['G_AUX.3','G_AUX.4','G_TAIL.2'])

    def test_pitch_support_not_inherited_from_removed_cover(self):
        for r in self.p['rows']:
            self.assertEqual(r['current_pitch_anchor_open'],r['group']=='HP')
            self.assertTrue(r['endpoint_is_local_insulation_boundary_not_servo_pin'])

    def test_no_partial_acceptance_or_cut_claim(self):
        self.assertFalse(self.p['selected'])
        self.assertFalse(self.p['physical_pass'])
        self.assertFalse(self.p['stage_completed'])
        for r in self.p['rows']:
            self.assertIsNone(r['nominal_fit_blank_mm'])
            self.assertIsNone(r['actual_cut_mm'])
            self.assertFalse(r['route_qualified'])


if __name__=='__main__':unittest.main()
