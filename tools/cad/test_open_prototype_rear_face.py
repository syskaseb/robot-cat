"""Ordered common-entry contracts; not native or physical qualification."""
import math, unittest
import open_prototype_rear_face as G
from open_prototype_entry_chambers import occupancy

class RearFace(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=G.build_geometry(ordered_columns=True);cls.old=G.G.T.build()

    def test_four_source_paths_and_two_real_grip_lands(self):
        for r in self.p['s1_routes']:
            self.assertAlmostEqual(G.B.check_path(r['segments'],r['barrel_mm'],self.p['ports'][r['target']]['point_mm'],25.2),r['centreline_mm'])
            self.assertGreaterEqual(len(r['insulation_grip_lands']),2)
            for g in r['insulation_grip_lands']:self.assertGreaterEqual(math.dist(g['start_mm'],g['end_mm']),9-1e-7)

    def test_all_four_rear_arrivals_current_and_bijective(self):
        p=self.p
        self.assertEqual({e['wire']:e['current_role'] for e in p['body_ends'] if e['current_role'].startswith('P_REAR.')},
                         {'W044':'P_REAR.3','W052':'P_REAR.4','W065':'P_REAR.5'})
        self.assertEqual(next(h for h in p['holders'] if h['role']=='F_AUX')['input_target'],'P_REAR.1')
        loads=occupancy(G.B.read(G.OUT/'routing-scope-plan.json'),p['permutation'])
        self.assertEqual(sum(bool(loads[n]) for n in p['ports']),86)
        self.assertTrue(all(len(loads[n])<=1 for n in p['ports']))
        for e in p['body_ends']:
            if e['datum'] is not None:self.assertEqual(e['datum'],p['ports'][e['current_role']])

    def test_port_face_and_routing_direction(self):
        case=next(s for s in self.p['stations'] if s['role']=='P_REAR')
        for i in range(1,6):
            d=self.p['ports'][f'P_REAR.{i}']
            self.assertAlmostEqual(d['point_mm'][1],case['centre_mm'][1]+case['size_mm'][1]/2)
            self.assertEqual(d['departure'],G.B.NORTH)
        for wire in ('W044','W052'):
            r=next(t for t in self.p['tails'] if t['wire']==wire)
            G.B.check_path(r['segments'],r['segments'][0]['start'],self.p['ports'][r['target']]['point_mm'],6)
            self.assertLessEqual(r['required_blank_mm'],r['assumed_factory_limit_mm'])
            self.assertGreaterEqual(len(r['independent_grip_lands']),2)
        h=next(h for h in self.p['holders'] if h['role']=='F_AUX')
        G.B.check_path(h['input_segments'],h['input_mm'],self.p['ports'][h['input_target']]['point_mm'],6)
        self.assertLessEqual(h['input_blank_mm'],h['factory_minimum_mm'])
        self.assertGreaterEqual(len(h['input_grip_lands']),2)

    def test_unchanged_interfaces_preserved(self):
        self.assertEqual(self.p['mta'],self.old['mta'])
        for name in ('stations','holders','tails'):
            key='wire' if name=='tails' else 'role'
            excluded={'P_REAR'} if name=='stations' else {'F_AUX'} if name=='holders' else {'W044','W052'}
            self.assertEqual([r for r in self.p[name] if r[key] not in excluded],
                             [r for r in self.old[name] if r[key] not in excluded])
        a=next(r for r in self.p['holders'] if r['role']=='F_AUX')
        b=next(r for r in self.old['holders'] if r['role']=='F_AUX')
        for k in ('centre_mm','output_segments','sleeve_start_mm','sleeve_end_mm','new_insulation_end_mm'):self.assertEqual(a[k],b[k])

    def test_common_paths_have_no_known_sample_crossing(self):
        bad=[r for r in G.G.S.F.F.proximity(self.p)['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY']
        self.assertFalse(bad)
        self.assertFalse(self.p['selected']);self.assertFalse(self.p['stage_completed'])

if __name__=='__main__':unittest.main()
