"""Pure contracts for the one rounded factory family, not physical approval."""
import json,math,unittest
from plan_fixed_underneck_rounds import OUT,RESERVE,START,PIVOT
from plan_current_moving_looms import add,sub,mul,cross,dot,norm,rotation


def unit(v):return mul(v,1/norm(v))


def endpoints(p):
    if p['kind']=='line':
        t=unit(sub(p['end'],p['start']));return t,t
    a=sub(p['mid'],p['start']);b=sub(p['end'],p['start']);n=cross(a,b)
    centre=add(p['start'],mul(add(mul(cross(b,n),dot(a,a)),mul(cross(n,a),dot(b,b))),1/(2*dot(n,n))))
    start=unit(sub(p['start'],centre));middle=unit(sub(p['mid'],centre));end=unit(sub(p['end'],centre))
    assert abs(math.dist(p['start'],centre)-p['radius_mm'])<1e-7
    angle=math.acos(max(-1,min(1,dot(start,middle))))+math.acos(max(-1,min(1,dot(middle,end))))
    assert abs(angle*p['radius_mm']-p['length_mm'])<1e-7
    return unit(cross(n,start)),unit(cross(n,end))


class RoundedFactory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=json.loads((OUT/'fixed-underneck-rounds-plan.json').read_text())

    def test_uncut_all_poses(self):
        self.assertEqual({q['yaw'] for q in self.p['poses']},set(range(-15,16)))
        for q in self.p['poses']:
            self.assertAlmostEqual(sum(s['length_mm'] for s in q['parts'])+self.p['prefix_mm'],250,places=6)
            self.assertAlmostEqual(q['parts'][0]['length_mm'],9,places=7)
            self.assertAlmostEqual(q['parts'][-1]['length_mm'],9,places=7)

    def test_all_virtual_joins_tangent(self):
        for q in self.p['poses']:
            for a,b in zip(q['parts'],q['parts'][1:]):
                self.assertLess(math.dist(a['end'],b['start']),1e-7)
                self.assertGreater(dot(endpoints(a)[1],endpoints(b)[0]),1-1e-7)

    def test_one_fixed_receiver_and_real_yaw_start(self):
        for q in self.p['poses']:
            expected=add(PIVOT,rotation(sub(START,PIVOT),[0,0,1],q['yaw']))
            self.assertLess(math.dist(expected,q['parts'][0]['start']),1e-7)
            self.assertEqual(q['parts'][-1]['end'],[self.p['fixed_receiver_XZ_mm'][0],self.p['fixed_receiver_Y_mm'],self.p['fixed_receiver_XZ_mm'][1]])
            self.assertLessEqual(q['conservative_upperY_mm'],100+1e-7)
            self.assertGreaterEqual(q['minimum_radius_mm'],31.5)

    def test_no_selection_or_safety_claim(self):
        for key in ('selected','native_changed','W2_complete','W3_complete','physical_pass'):self.assertFalse(self.p[key])
        self.assertTrue(self.p['factory_profile_and_dynamic_radius_provisional'])


if __name__=='__main__':unittest.main()
