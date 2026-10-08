import math
import unittest
import open_prototype_shared_space as S


class SharedSpace(unittest.TestCase):
    def test_all_nine_nets_once_not_stage_acceptance(self):
        p=S.build_plan()
        self.assertEqual(len({r['wire'] for g in p['groups'] for r in g['rows']}),9)
        self.assertFalse(p['selected']);self.assertFalse(p['stage_completed'])
        self.assertFalse(p['physical_pass']);self.assertFalse(p['body_widening'])

    def test_topology_under_actual_roof_not_translated_torso(self):
        p=S.build_plan()
        self.assertEqual(p['torso_world_bounds_mm'][-1],158)
        for g in p['groups']:
            self.assertLessEqual(max(x[2] for x in g['centre_points_mm']),149)
            self.assertGreaterEqual(g['first_free_mm'],9)
            self.assertGreaterEqual(g['last_free_mm'],9)

    def test_transported_packing_and_continuity(self):
        for g in S.build_plan()['groups']:
            for row in g['rows']:
                for a,b in zip(row['segments'],row['segments'][1:]):
                    self.assertLess(math.dist(a['end'],b['start']),1e-8)
            for k in range(len(g['rows'][0]['segments'])):
                for i,a in enumerate(g['rows']):
                    for b in g['rows'][i+1:]:
                        for point in ('start','end'):
                            self.assertAlmostEqual(math.dist(a['segments'][k][point],b['segments'][k][point]),2.1)

    def test_entire_bundle_cross_sections_have_two_mm_planning_margin(self):
        gap=S.build_plan()['shared_level_separation']
        self.assertGreaterEqual(gap['minimum_centre_gap_mm'],gap['bundle_diameter_mm']+2)


if __name__=='__main__':unittest.main()
