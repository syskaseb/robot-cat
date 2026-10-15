import copy,json,math,unittest
from pathlib import Path
from joint_clearance_corridors import plan
from parallel_core_candidates import tangent

def initial_tangent(part):
    q=copy.deepcopy(part);q['start'],q['end']=q['end'],q['start']
    if 'poles_mm' in q:q['poles_mm'].reverse()
    return [-x for x in tangent(q)]

class JointCorridorTests(unittest.TestCase):
    def test_all_four_complete_tangent_chains_fit_received_budgets(self):
        folder=Path(__file__).resolve().parents[2]/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint'
        parent=json.loads((folder/'body36-shared-macro-layout.json').read_text())
        base=json.loads((folder/'body36-recovery-layout.json').read_text())
        rows,proposals,failures=plan(parent,base)
        self.assertFalse(failures,failures)
        for n,q in proposals.items():
            self.assertGreaterEqual(q['spare_before_trim_mm'],0,n)
            self.assertGreaterEqual(q['minimum_sampled_R_mm'],10,n)
            for a,b in zip(q['parts'],q['parts'][1:]):
                self.assertLess(math.dist(a['end'],b['start']),1e-6,n)
                self.assertGreater(sum(x*y for x,y in zip(tangent(a),initial_tangent(b))),.999999,n)
            self.assertEqual(q['parts'][-1],rows[n]['receiving_parts'][-1])

if __name__=='__main__':unittest.main()
