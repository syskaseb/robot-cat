import math
import unittest
import open_prototype_source_layout as L


class SourceLayout(unittest.TestCase):
    def test_common_recipe_datums_include_quarter_radius(self):
        p=L.build_plan()
        self.assertEqual(len(p['factory_paths']),4)
        self.assertEqual(len(p['sleeves']),4)
        for r in p['factory_paths']:
            self.assertEqual(len(r['segments']),3)
            self.assertAlmostEqual(math.dist(r['segments'][-1]['start'],r['segments'][-1]['end']),15)
        self.assertFalse(p['selected'])
        self.assertTrue(p['ground_casing_frames_unchanged'])
        self.assertTrue(p['AUX_insulated_stub']['unknown_U1_not_connected'])

    def test_whole_source_scope_and_covered_grips(self):
        p=L.build_plan()
        self.assertEqual(len(p['rows']),9)
        self.assertEqual(len(p['common_PWM']),3)
        for r in p['rows']:
            self.assertEqual(r['independent_source_grip_mm'],9)
            if r['wire'].startswith('XB') and r['wire'].endswith('2'):
                self.assertEqual(r['source_straight_mm'],21.5)
            for a,b in zip(r['segments'],r['segments'][1:]):
                end=a['poles'][-1] if a['kind']=='bezier' else a['end']
                start=b['poles'][0] if b['kind']=='bezier' else b['start']
                self.assertLess(math.dist(end,start),1e-7)
            for e in r['segments']:
                if e['kind']=='bezier':
                    self.assertGreaterEqual(e['curvature']['minimum_radius_mm'],13)
                elif e['kind']=='arc':
                    a,b,c=e['start'],e['mid'],e['end']
                    area=.5*math.sqrt(L.B.dot(L.B.cross(L.B.sub(b,a),L.B.sub(c,a)),L.B.cross(L.B.sub(b,a),L.B.sub(c,a))))
                    self.assertGreaterEqual(math.dist(a,b)*math.dist(b,c)*math.dist(c,a)/(4*area),13-1e-7)


if __name__=='__main__':unittest.main()
