"""Contracts for one shared source candidate, not physical clearance."""
import unittest
import open_prototype_source_bypass as G

class SourceBypass(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=G.build_geometry(bus_undercross=True,allocated_ports=True)
        cls.old=G.T.build()

    def test_four_complete_curved_routes_and_separate_grip_lands(self):
        self.assertEqual({r['wire'] for r in self.p['s1_routes']},{'W064','W065','W067','W068'})
        for r in self.p['s1_routes']:
            self.assertAlmostEqual(G.B.check_path(r['segments'],r['barrel_mm'],
                self.p['ports'][r['target']]['point_mm'],25.2),r['centreline_mm'])
            self.assertGreaterEqual(len(r['insulation_grip_lands']),2)
            for land in r['insulation_grip_lands']:
                self.assertGreaterEqual(__import__('math').dist(land['start_mm'],land['end_mm']),9-1e-7)
            self.assertGreaterEqual(r['nominal_fit_blank_mm'],r['centreline_mm']+28.452)
        short=next(r for r in self.p['s1_routes'] if r['wire']=='W067')
        self.assertTrue(short['short_entry_is_not_grip'])
        self.assertAlmostEqual(G.B.segment_geometry(short['segments'][0])[0],2)
        self.assertLess(G.B.segment_geometry(short['segments'][-1])[0],1)

    def test_all_receiving_modules_and_factory_tails_preserved(self):
        for key in ('stations','mta','holders','tails'):
            self.assertEqual(self.p[key],self.old[key],key)
        self.assertEqual(len(self.p['body_ends']),160)
        self.assertEqual({(e['wire'],e['net'],e['original_role']) for e in self.p['body_ends']},
                         {(e['wire'],e['net'],e['original_role']) for e in self.old['body_ends']})

    def test_sys_same_potential_slot_assignment_is_bijective(self):
        expected={'W043':'P_SYS.1','W066':'P_SYS.5','W067':'P_SYS.3','W068':'P_SYS.4'}
        current={e['wire']:e['current_role'] for e in self.p['body_ends'] if e['current_role'].startswith('P_SYS.')}
        self.assertEqual(current,expected)
        self.assertEqual(len(set(current.values())),4)
        for e in self.p['body_ends']:
            if e['datum'] is not None:self.assertEqual(e['datum'],self.p['ports'][e['current_role']])

    def test_shared_paths_have_no_known_sampled_crossing_but_not_selected(self):
        report=G.S.F.F.proximity(self.p)
        self.assertFalse([r for r in report['near_pairs'] if r['status']=='REJECT_PLANNING_PROXIMITY'])
        self.assertFalse(self.p['selected'])
        self.assertFalse(self.p['stage_completed'])
        self.assertEqual(self.p['s1_module']['whole_rotation_deg'],90)
        self.assertTrue(self.p['s1_geometry_changed'])

if __name__=='__main__':unittest.main()
