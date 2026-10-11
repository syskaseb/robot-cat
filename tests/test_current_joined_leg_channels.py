import json,math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/cad'))
from plan_current_joined_leg_looms import OUT,SHA
from screen_current_joined_leg_looms import screen_rows
from plan_current_mta_interfaces import line
from plan_current_moving_looms import metrics

class JoinedLegChannels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=json.loads((OUT/'leg-fanout-channels-plan.json').read_text())
        cls.screen=json.loads((OUT/'leg-fanout-channels-screen.json').read_text())
        cls.ends={r['wire']:r for r in json.loads((OUT/'leg-terminations-plan.json').read_text())['wires']}

    def test_one_complete_36_end_candidate_not36_factory_purchases(self):
        self.assertEqual(set(self.plan['routes']),set(self.ends));self.assertEqual(len(self.ends),36)
        self.assertEqual(len({r['loom'] for r in self.plan['routes'].values()}),12)
        for name,r in self.plan['routes'].items():
            self.assertEqual(r['parts'][-1]['end'],self.ends[name]['body_point_mm'])
            self.assertAlmostEqual(r['parts'][-1]['length_mm'],9)
            self.assertGreaterEqual(r['remaining_mm'],0)
            self.assertIsNone(r['actual_cut_mm'])
            for a,b in zip(r['parts'],r['parts'][1:]):self.assertLess(math.dist(a['end'],b['start']),1e-6)

    def test_nominal_shared_candidate_does_not_claim_material_motion_or_W5(self):
        self.assertEqual(self.screen['status'],'COMMON_NOMINAL_48_PATHS_PROXIMITY_ONLY')
        self.assertEqual(self.screen['rejected'],[])
        self.assertFalse(self.screen['motion_qualified'])
        for p in (self.plan,self.screen):
            for key in ('selected','W5_complete','physical_pass'):self.assertFalse(p[key])
            for name,h in p['source_sha256'].items():self.assertEqual(SHA(ROOT/name),h,name)

    def test_sampling_chords_do_not_replace_exact_curve_length_or_radius(self):
        found=0
        for r in self.plan['routes'].values():
            for q in r['parts']:
                if q['kind']!='bezier':continue
                found+=1;length,radius,_=metrics(q['poles_mm'],240)
                self.assertAlmostEqual(length,q['length_mm'],places=5)
                self.assertGreaterEqual(radius,9.99)
        self.assertGreater(found,0)

    def test_own_aggregate_join_does_not_waive_later_self_crossing(self):
        bundle=dict(wire='Loom/test',OD_mm=6,segments=[line([0,0,0],[0,0,10])])
        core=dict(wire='core',OD_mm=2,segments=[line([1.2,0,10],[1.2,0,15])])
        meta=({'Loom/test':[0,0,10]},{'Loom/test':(bundle['segments'],[0])},
              {'core':'Loom/test'},{'core':[1.2,0,10]})
        self.assertFalse([q for q in screen_rows([],[bundle,core],meta) if q['status']=='REJECT_PLANNING_PROXIMITY'])
        core['segments'].append(line([1.2,0,15],[1.2,0,0]))
        self.assertTrue([q for q in screen_rows([],[bundle,core],meta) if q['status']=='REJECT_PLANNING_PROXIMITY'])

if __name__=='__main__':unittest.main()
