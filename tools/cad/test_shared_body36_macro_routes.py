import copy,json,math,unittest
from pathlib import Path
from shared_body36_macro_routes import plan,CHANGED,spatial_half_return,N,packed_front_prefixes

class MacroRoutesTest(unittest.TestCase):
    def test_only_two_real_material_conflicts_are_revised_without_margin_waiver(self):
        import subprocess
        from revise_shared_body36_routes import plan as revise
        root=Path(__file__).resolve().parents[2];folder='hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint/'
        parent=json.loads(subprocess.check_output(['git','show','3c81baf:'+folder+'body36-shared-macro-layout.json'],cwd=root))
        base=json.loads((root/folder/'body36-recovery-layout.json').read_text());rows,candidates,failures=revise(parent,base,material_only=True)
        self.assertFalse(failures);self.assertEqual(set(candidates),{'W008','W030'})
        for q in candidates.values():
            self.assertGreaterEqual(q['minimum_sampled_R_mm'],10);self.assertGreater(q['spare_before_trim_mm'],0)
    def test_received_bezier_splice_keeps_old_tail_and_under_support_join(self):
        from received_curve_splice import splice,split
        root=Path(__file__).resolve().parents[2]
        f=root/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint/body36-recovery-layout.json'
        base=json.loads(f.read_text());rows={r['wire']:r for r in base['rows']}
        row,q,error=splice(rows['W008'],packed_front_prefixes(rows)['W008'],base['routes']['W008'],2,2,54.74)
        self.assertIsNone(error);self.assertIsNotNone(q);self.assertAlmostEqual(row['free_end'][2],54.74,6)
        self.assertEqual(q['parts'][-1]['end'],base['routes']['W008']['parts'][-1]['end'])
        self.assertGreater(q['spare_before_trim_mm'],0);self.assertGreaterEqual(q['minimum_sampled_R_mm'],10)
        self.assertEqual(row['receiving_parts'][1:],base['routes']['W008']['parts'][3:])
        left,right=split(base['routes']['W008']['parts'][2],.5)
        self.assertEqual(left['end'],right['start'])
        self.assertAlmostEqual(left['length_mm']+right['length_mm'],base['routes']['W008']['parts'][2]['length_mm'],3)
        print('received splice W008',q['guide_mm'],q['spare_before_trim_mm'],flush=True)
    def test_witness_driven_revision_keeps_qualified_routes_and_all_terminals(self):
        import subprocess
        from revise_shared_body36_routes import plan as revise,PARENT
        root=Path(__file__).resolve().parents[2]
        folder='hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint/'
        parent=json.loads(subprocess.check_output(['git','show',PARENT+':'+folder+'body36-shared-macro-layout.json'],cwd=root));saved=copy.deepcopy(parent)
        base=json.loads((root/folder/'body36-recovery-layout.json').read_text())
        rows,candidates,failures=revise(parent,base)
        self.assertEqual(parent,saved);self.assertFalse(failures)
        self.assertEqual(set(candidates),{'W004','W008','W019','W022','W030','W069'})
        self.assertFalse(set(candidates)&set(parent['qualified_changed_routes']))
        original={r['wire']:r for r in base['rows']}
        for name,q in candidates.items():
            self.assertEqual(q['parts'][-1]['end'],original[name]['receiving_parts'][-1]['end'])
            self.assertGreaterEqual(q['minimum_sampled_R_mm'],10);self.assertGreater(q['spare_before_trim_mm'],0)
        self.assertGreater(candidates['W022']['spare_before_trim_mm'],20)

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
