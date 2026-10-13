import json
import math
import unittest
from plan_remaining_loom_roots import OUT, build


class RemainingRoots(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = [json.loads((OUT/p).read_text()) for p in (
            'leg-source-near-member-plan.json', 'leg-extension-budget-plan.json',
            'complete-source-carriers-plan.json')]
        cls.groups = build(*cls.inputs)
        cls.lands = [r for g in cls.groups for r in g['lands']]

    def test_complete_single_ownership(self):
        self.assertEqual(len(self.groups), 12)
        self.assertEqual(len(self.lands), 36)
        self.assertEqual(len({r['id'] for r in self.lands}), 36)
        self.assertEqual(sum(r['owner_stage']=='Body' for r in self.lands), 12)
        self.assertEqual(sum(r['owner_stage'].endswith('_Hip') for r in self.lands), 8)
        self.assertEqual(sum(r['owner_stage'].endswith('_Knee') for r in self.lands), 16)

    def test_exact_knee_end_segments(self):
        by_id = {r['id']:r for r in self.lands}
        for row in self.inputs[0]['knees']:
            pose = next(p for p in row['poses'] if p['angle']==0)
            for name, segment in [('Fixed',pose['parts'][0]),('Moving',pose['parts'][-1])]:
                actual=by_id[row['loom']+'/Knee/'+name]
                self.assertEqual(actual['start_world_mm'],segment['start'])
                self.assertEqual(actual['end_world_mm'],segment['end'])
                self.assertAlmostEqual(math.dist(segment['start'],segment['end']),9)

    def test_splices_stay_outside_sleeve_zone_and_on_source(self):
        for group in self.groups:
            if 'sleeve_zone' not in group:
                continue
            zone=group['sleeve_zone']
            splice_lands=[r for r in group['lands'] if '/Splice/' in r['id']]
            self.assertEqual(len(splice_lands),2)
            self.assertEqual(zone['sleeve_count'],3)
            self.assertIsNone(zone['sleeve_SKU'])
            for land in splice_lands:
                self.assertEqual(land['owner_stage'],group['owner_stage'])
                distance=math.dist(land['centre_world_mm'],zone['centre_world_mm'])
                self.assertAlmostEqual(distance,38.5)
                self.assertAlmostEqual(distance-4.5-zone['length_project_mm']/2,2)

    def test_inputs_not_rewritten(self):
        baseline=json.dumps(self.inputs,sort_keys=True)
        build(*self.inputs)
        self.assertEqual(json.dumps(self.inputs,sort_keys=True),baseline)


if __name__=='__main__':
    unittest.main()
