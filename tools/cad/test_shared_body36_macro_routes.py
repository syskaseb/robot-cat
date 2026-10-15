import copy,json,math,unittest
from pathlib import Path
from shared_body36_macro_routes import plan,CHANGED

class MacroRoutesTest(unittest.TestCase):
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
        self.assertEqual(current['W022']['receiving_grip_part_index'],original['W022']['receiving_grip_part_index']+1)
        print('macro math candidates',list(candidates),'failures',failures,flush=True)

if __name__=='__main__':unittest.main()
