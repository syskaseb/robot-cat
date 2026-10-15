import copy,json,math,unittest
from pathlib import Path
from shared_body36_macro_routes import plan,CHANGED,spatial_half_return,N,packed_front_prefixes

class MacroRoutesTest(unittest.TestCase):
    def test_concentric_corners_preserve_three_core_packing(self):
        import numpy as np
        from plan_body_fanout_layout import part_points
        root=Path(__file__).resolve().parents[2]
        f=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint/body36-recovery-layout.json'
        rows={r['wire']:r for r in json.loads(f.read_text())['rows']};prefixes=packed_front_prefixes(rows)
        for group in (('W004','W019','W020'),('W008','W030','W031')):
            for i,a in enumerate(group):
                aa=np.concatenate([part_points(p) for p in prefixes[a]])
                for b in group[:i]:
                    bb=np.concatenate([part_points(p) for p in prefixes[b]])
                    minimum=float(np.sqrt(np.min(np.sum((aa[:,None,:]-bb[None,:,:])**2,axis=2))))
                    self.assertGreaterEqual(minimum,2.598-1e-3,(a,b,minimum))

    def test_received_endpoints_budget_and_no_source_mutation(self):
        root=Path(__file__).resolve().parents[2]
        f=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint/body36-recovery-layout.json'
        data=json.loads(f.read_text());rows={r['wire']:r for r in data['rows']};original=copy.deepcopy(rows)
        current,candidates,failures=plan(rows)
        self.assertEqual(rows,original);self.assertEqual(set(candidates)|set(failures),set(CHANGED))
        for name,q in candidates.items():
            r=current[name];self.assertGreaterEqual(q['spare_before_trim_mm'],0);self.assertGreaterEqual(q['minimum_sampled_R_mm'],10)
            self.assertLess(math.dist(q['parts'][0]['start'],original[name].get('source_parts',[original[name]['source_land']])[0]['start']),1e-6)
            self.assertEqual(q['parts'][-1]['end'],original[name].get('receiving_parts',[original[name]['receiving_land']])[-1]['end'])
            for a,b in zip(q['parts'],q['parts'][1:]):self.assertLess(math.dist(a['end'],b['start']),1e-6)
        self.assertFalse(failures);self.assertEqual(len(candidates),9)
        self.assertEqual(current['W022']['receiving_grip_part_index'],original['W022']['receiving_grip_part_index']+1)
        print('macro math candidates',list(candidates),'failures',failures,flush=True)

    def test_spatial_return_preserves_cardinal_axis_and_real_radius(self):
        from plan_current_mta_interfaces import line
        from parallel_core_candidates import tangent
        for end in ([11,40,-28],[11,-3,-28]):
            p=[line([0,-5,0],[0,0,0])];spatial_half_return(p,end,N)
            self.assertLess(math.dist(p[-1]['end'],end),1e-6)
            self.assertLess(math.dist(tangent(p[-1]),[0,-1,0]),1e-6)
            for part in p:
                if part['kind']=='arc':self.assertEqual(part['radius_mm'],10)

if __name__=='__main__':unittest.main()
