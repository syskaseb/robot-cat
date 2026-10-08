import math
import unittest
import open_prototype_bundle_spines as B


class SharedTrunks(unittest.TestCase):
    def test_three_trunks_nine_distinct_wires_not_whole_stage(self):
        p=B.build_plan()
        self.assertEqual(len(p['groups']),3)
        self.assertEqual(len({r['wire'] for g in p['groups'] for r in g['rows']}),9)
        self.assertFalse(p['selected']);self.assertFalse(p['stage_completed'])
        self.assertFalse(p['physical_pass'])
        self.assertGreater(len(p['open_interfaces']),5)

    def test_packing_and_continuity_at_every_edge(self):
        for g in B.build_plan()['groups']:
            for r in g['rows']:
                for a,b in zip(r['segments'],r['segments'][1:]):
                    self.assertLess(math.dist(a['end'],b['start']),1e-8)
            for k in range(len(g['rows'][0]['segments'])):
                for i,a in enumerate(g['rows']):
                    for b in g['rows'][i+1:]:
                        for point in ('start','end'):
                            self.assertAlmostEqual(math.dist(a['segments'][k][point],b['segments'][k][point]),2.1)
                        if a['segments'][k]['kind']=='arc':
                            self.assertAlmostEqual(math.dist(a['segments'][k]['mid'],b['segments'][k]['mid']),2.1)

    def test_radius_not_shrunk_and_nine_mm_straights(self):
        p=B.build_plan()
        self.assertGreater(p['guaranteed_individual_radius_lower_bound_mm'],12.6)
        for g in p['groups']:
            self.assertGreaterEqual(g['first_free_mm'],9)
            self.assertGreaterEqual(g['last_free_mm'],9)

    def test_pitch_avoids_obsolete_cover_and_pi_ato_lane(self):
        g=next(g for g in B.build_plan()['groups'] if g['group']=='HP')
        self.assertEqual(g['centre_points_mm'][-1],[-52,26,149])
        self.assertTrue(any('New fixed pitch anchor' in x for x in B.build_plan()['open_interfaces']))


if __name__=='__main__':unittest.main()
