import math
import unittest
import open_prototype_source_fanouts as F


class Fanouts(unittest.TestCase):
    def test_straight_curve_has_no_false_radius_limit(self):
        g=F.curvature_gate([[0,0,0],[10,0,0],[20,0,0],[30,0,0]])
        self.assertIsNone(g['minimum_radius_mm'])

    def test_quarter_circle_bezier_extrema(self):
        k=4*(math.sqrt(2)-1)/3;r=20
        g=F.curvature_gate([[r,0,0],[r,k*r,0],[k*r,r,0],[0,r,0]])
        self.assertTrue(19.8<g['minimum_radius_mm']<20)

    def test_plan_all_nine_no_unknown_pinout_or_selection(self):
        p=F.build_plan()
        self.assertEqual(len(p['rows']),9);self.assertEqual(len(p['common_PWM_outlet']),3)
        self.assertFalse(p['selected']);self.assertFalse(p['stage_completed'])
        self.assertTrue(p['unknown_U1_not_connected'])
        for r in p['rows']:
            for curve in (s for s in r['segments'] if s['kind']=='bezier'):
                self.assertGreaterEqual(curve['curvature']['minimum_radius_mm'],13)
            for curve in (s for s in r['segments'] if s['kind']=='arc'):
                a,b,c=curve['start'],curve['mid'],curve['end']
                area=.5*math.sqrt(sum(x*x for x in F.B.cross(F.B.sub(b,a),F.B.sub(c,a))))
                radius=math.dist(a,b)*math.dist(b,c)*math.dist(c,a)/(4*area)
                self.assertGreaterEqual(radius,13)
            for a,b in zip(r['segments'],r['segments'][1:]):
                end=a['poles'][-1] if a['kind']=='bezier' else a['end']
                start=b['poles'][0] if b['kind']=='bezier' else b['start']
                self.assertLess(math.dist(end,start),1e-7)


if __name__=='__main__':unittest.main()
