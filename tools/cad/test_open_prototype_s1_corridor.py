import unittest
import open_prototype_s1_lower_corridor as G

class RejectedSourceCorridor(unittest.TestCase):
    def test_rejected_family_cannot_be_current(self):
        with self.assertRaisesRegex(AssertionError,'Rejected lowerS1'):
            G.build()
    def test_archived_routes_and_known_short_straight(self):
        # Archive the failed9mm grip constraint, never relabel it as qualified.
        p=G.B.read(G.PLAN)['family']
        self.assertEqual({r['wire'] for r in p['s1_routes']},{'W064','W065','W067','W068'})
        for r in p['s1_routes']:
            G.B.check_path(r['segments'],r['barrel_mm'],p['ports'][r['target']]['point_mm'],25.2)
            self.assertGreaterEqual(G.B.segment_geometry(r['segments'][-1])[0],9-1e-7)
        known=next(r for r in p['s1_routes'] if r['wire']=='W067')
        self.assertAlmostEqual(G.B.segment_geometry(known['segments'][0])[0],8.677,places=6)
        self.assertLess(G.B.segment_geometry(known['segments'][0])[0],9)
        h=next(h for h in p['holders'] if h['role']=='F_PI')
        self.assertLessEqual(h['input_blank_mm'],50)
    def test_same_net_port_and_full_module_binding(self):
        p=G.B.read(G.PLAN)['family']
        self.assertEqual(next(r['target'] for r in p['s1_routes'] if r['wire']=='W068'),'P_SYS.3')
        occupied=[r['current_role'] for r in p['body_ends'] if r['current_role'].startswith('P_SYS.')]
        self.assertNotIn('P_SYS.5',occupied)
        self.assertEqual(len(occupied),len(set(occupied)))
        for r in p['body_ends']:
            if r['current_role'] in p['ports']:self.assertEqual(r['datum'],p['ports'][r['current_role']])
        for ring in p['s1_module']['rings']:
            self.assertAlmostEqual(ring['eye_mm'][2],60)
            self.assertAlmostEqual(G.B.segment_geometry(G.B.line(ring['eye_mm'],ring['barrel_mm']))[0],22.123)

if __name__=='__main__':unittest.main()
