import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/cad'))
from plan_current_leg_terminations import OUT,SHA

class CurrentLegTerminations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=json.loads((OUT/'leg-terminations-plan.json').read_text())
    def test_36_distinct_cores_are_12_not_36_factory_cables(self):
        rows=self.p['wires'];self.assertEqual(len(rows),36)
        self.assertEqual(len({r['wire'] for r in rows}),36)
        self.assertEqual(len({r['loom'] for r in rows}),12)
        for loom in {r['loom'] for r in rows}:self.assertEqual({r['core'] for r in rows if r['loom']==loom},{'D','G','V'})
        self.assertEqual(self.p['factory_cables'],12);self.assertEqual(self.p['six_packs'],2)
    def test_current_end_inputs_are_pinned(self):
        for n,h in self.p['source_sha256'].items():self.assertEqual(SHA(ROOT/n),h,n)
    def test_straight_capacity_does_not_claim_fanout_or_fit(self):
        self.assertFalse(self.p['selected']);self.assertFalse(self.p['W5_complete']);self.assertFalse(self.p['physical_pass'])
        self.assertFalse(self.p['rejected'])
        for r in self.p['wires']:
            self.assertGreaterEqual(r['optimistic_remaining_mm'],0)
            self.assertIsNone(r['actual_cut_mm']);self.assertIn('OPEN',r['route_and_independent_relief'])

if __name__=='__main__':unittest.main()
