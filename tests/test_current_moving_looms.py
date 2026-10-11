import json,math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/cad'))
from plan_current_moving_looms import OUT,metrics,curve_length,sub,norm,dot

class MovingLoomPlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=json.loads((OUT/'moving-looms-plan.json').read_text())
    def test_complete_math_family_is_not_material_or_W5_acceptance(self):
        self.assertEqual(self.p['status'],'PROJECT_FLEX_ALLOCATION_ONLY')
        self.assertEqual(len(self.p['looms']),12)
        self.assertFalse(self.p['selected']);self.assertFalse(self.p['W5_complete'])
        for r in self.p['looms']:
            self.assertEqual(set(r['cores']),{'D','G','V'});self.assertFalse(r['manufacturer_flex_data_verified'])
            self.assertEqual(r['rejected_poses'],0);self.assertGreater(r['body_fanout_budget_remaining_mm'],400)
    def test_exact_length_and_sampled_radius_at_all84_poses(self):
        count=0
        for r in self.p['looms']:
            for v in r['poses']:
                count+=1;qq=v.get('spans_mm',[v.get('poles_mm')])
                length=sum(curve_length(q) for q in qq)
                for q in qq:self.assertGreaterEqual(metrics(q,600)[1],30)
                length+=sum(q['length_mm'] for q in v.get('return_parts_mm',[]))
                self.assertAlmostEqual(length,r['constant_flex_budget_mm'],places=3)
        self.assertEqual(count,84)
    def test_knee_return_continuity_and_no_fictitious_clamp(self):
        for r in self.p['looms']:
            if not r['loom'].endswith('2'):continue
            for v in r['poses']:
                self.assertTrue(v['intermediate_waypoint_is_not_a_support'])
                q=v['spans_mm'][0];parts=v['return_parts_mm']
                self.assertLess(math.dist(q[-1],parts[0]['start']),1e-8)
                a=sub(q[-1],q[-2]);b=sub(parts[0]['end'],parts[0]['start'])
                self.assertAlmostEqual(dot(a,b)/norm(a)/norm(b),1)
                self.assertEqual([p['kind'] for p in parts],['line','arc','arc','line'])
                self.assertEqual([p['radius_mm'] for p in parts if p['kind']=='arc'],[35,35])
                for one,two in zip(parts,parts[1:]):self.assertLess(math.dist(one['end'],two['start']),1e-8)
                self.assertLess(math.dist(parts[-1]['end'],r['body_dock_mm']),1e-8)

if __name__=='__main__':unittest.main()
