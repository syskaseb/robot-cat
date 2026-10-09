import math
import unittest
from open_prototype_power_island_plan import build
from open_prototype_entry_chambers import occupancy
from open_prototype_wiring_endpoints import BASE, read


class SharedPlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.plan=build(True)

    def test_twenty_roles_not_twenty_new_parts(self):
        p=self.plan
        self.assertEqual(len(p['stations']),20)
        self.assertEqual(len(p['ports']),100)
        self.assertEqual(len(p['body_ends']),160)

    def test_complete_same_bus_bijections(self):
        m=self.plan['permutation']
        for bus in {k.split('.')[0] for k in m}:
            old={f'{bus}.{n}' for n in range(1,6)}
            self.assertEqual({m.get(k,k) for k in old},old)
        loads=occupancy(read(BASE/'wiring-checkpoint/routing-scope-plan.json'),m)
        self.assertEqual(sum(bool(loads[k]) for k in self.plan['ports']),86)
        self.assertTrue(all(len(loads[k])<=1 for k in self.plan['ports']))

    def test_mta_eight_physical_ends_bound(self):
        p=self.plan
        self.assertEqual(len(p['tails']),8)
        for t in p['tails']:
            self.assertTrue(any(e['wire']==t['wire'] and e['current_role']==t['target'] for e in p['body_ends']))
            self.assertLessEqual(t['required_blank_mm'],100)
            self.assertTrue(t['factory_limit_not_catalog'])
            self.assertLess(math.dist(t['recipe']['segments'][-1]['end'],p['ports'][t['target']]['point_mm']),1e-7)

    def test_five_inputs_both_case_exits(self):
        self.assertEqual(len(self.plan['holders']),5)
        for h in self.plan['holders']:
            self.assertAlmostEqual(math.dist(h['input_mm'],h['output_mm']),51)
            self.assertLessEqual(h['input_blank_mm'],h['prefuse_project_limit_mm'])
            self.assertTrue(h['output_status'].startswith('OPEN'))
            self.assertEqual(h['input_segments'][0]['start'],h['input_mm'])
            self.assertEqual(h['input_segments'][-1]['end'],self.plan['ports'][h['input_target']]['point_mm'])

    def test_segment_continuity(self):
        rows=[r['recipe']['segments'] for r in self.plan['tails']]+[r['input_segments'] for r in self.plan['holders']]
        for parts in rows:
            for a,b in zip(parts,parts[1:]):self.assertLess(math.dist(a['end'],b['start']),1e-7)

    def test_no_partial_credit_or_old_source_mount(self):
        p=self.plan
        for flag in ('selected','stage_completed','W5_complete','physical_pass'):self.assertFalse(p[flag])
        self.assertIn('INVALIDATED',p['f0']['source_routes_and_mounts'])
        self.assertIn('OPEN',p['s1']['routes_status'])


if __name__=='__main__':unittest.main()
