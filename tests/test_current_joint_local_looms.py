import sys,math,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from plan_current_joint_local_looms import solve_loop,basis,LENGTH,OUT,SHA
from plan_current_moving_looms import sub,norm,dot,mul


class JointLocalPilot(unittest.TestCase):
    def test_solved_loop_keeps_length_and_both_actual_tangents(self):
        for angle in (-15,0,15):
            t=math.radians(angle);start=[0,-45,0];end=[0,45*math.cos(t),45*math.sin(t)]
            end_axis=[0,math.sin(t),-math.cos(t)]
            q=solve_loop(start,[0,0,1],end,end_axis)
            self.assertIsNotNone(q)
            self.assertAlmostEqual(q['length_mm'],LENGTH,places=6)
            self.assertGreaterEqual(q['sampled_minimum_R_mm'],31)
            p=q['poles_mm'];u=sub(p[1],p[0]);v=sub(p[3],p[2])
            self.assertAlmostEqual(dot(mul(u,1/norm(u)),[0,0,1]),1,places=8)
            self.assertAlmostEqual(dot(mul(v,1/norm(v)),end_axis),1,places=8)

    def test_actual_axis_not_assumed_global_or_mirrored(self):
        n,v,b=basis([0,-.990268,.139173],1)
        self.assertGreater(n[1],0)
        self.assertAlmostEqual(dot(n,v),0,places=8)
        self.assertAlmostEqual(dot(n,b),0,places=8)
        self.assertAlmostEqual(dot(v,b),0,places=8)

    def test_current_pilot_is_not_whole_loom_or_selected_result(self):
        q=json.loads((OUT/'joint-local-loom-plan.json').read_text())
        for n,h in q['source_sha256'].items():self.assertEqual(SHA(ROOT/n),h,n)
        self.assertEqual(q['status'],'JOINT_LOCAL_PILOT_MATH_ONLY')
        self.assertFalse(q['W5_complete']);self.assertFalse(q['selected']);self.assertFalse(q['native_changed'])
        self.assertEqual({r['loom'] for r in q['loops']},{'FL2','FL3'})
        for row in q['loops']:
            self.assertEqual([p['angle'] for p in row['poses']],list(range(-15,16)))
            self.assertEqual(row['parent_stage'],'Hip');self.assertEqual(row['child_stage'],'Knee')
            self.assertEqual(row['independent_insulation_land_mm_each'],9)
            for p in row['poses']:
                self.assertAlmostEqual(p['curve']['length_mm'],LENGTH,places=6)
                self.assertAlmostEqual(sum(s['length_mm'] for s in p['parts']),row['guide_mm'],places=6)
                self.assertEqual(p['parts'][0]['length_mm'],9)
                self.assertAlmostEqual(p['parts'][-1]['length_mm'],9,places=7)
                for a,b in zip(p['parts'],p['parts'][1:]):self.assertLess(math.dist(a['end'],b['start']),1e-7)
        self.assertIn('Part__Feature117',q['complete_child_material_members'])


if __name__=='__main__':unittest.main()
