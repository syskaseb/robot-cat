import unittest,math
import open_prototype_biarc as A
import open_prototype_s1_northern_bypass as N
B=A.B

class TangentSources(unittest.TestCase):
    def test_source_ports_follow_current_end_ledger(self):
        import open_prototype_s1_shared_routes as S
        p=S.F.build();rows=S.source_specs(p)
        self.assertEqual(dict((w,t) for w,_,t in rows)['W065'],'P_REAR.5')
        self.assertNotEqual(dict((w,t) for w,_,t in rows)['W065'],next(h['input_target'] for h in p['holders'] if h['role']=='F_AUX'))
        for row in p['tails']:
            if row['wire'] in {e['wire'] for e in p['body_ends']}:
                self.assertIn(row['target'],[e['current_role'] for e in p['body_ends'] if e['wire']==row['wire']])
    def test_exact_three_dimensional_tangents(self):
        for first in (32,40,60,80,110):
            parts=A.connect([132.2,43.123,85],B.NORTH,[81.8,42.5,124.221923828125],B.UP,first)
            B.check_path(parts)
            self.assertGreater(B.dot(B.segment_geometry(parts[1])[1],B.NORTH),1-1e-7)
            self.assertGreater(B.dot(B.segment_geometry(parts[-2])[2],B.UP),1-1e-7)
    def test_northern_front_changes_whole_topology(self):
        parts=N.connect([120.2,34.123,85],B.NORTH,[-38,33,131],B.WEST,60)
        B.check_path(parts,parts[0]['start'],[-38,33,131],25.2)
        self.assertEqual(parts[0]['end'],[120.2,43.123,85])
        self.assertAlmostEqual(B.segment_geometry(parts[-1])[0],9)
        self.assertGreater(parts[1]['end'][1],68)

if __name__=='__main__':unittest.main()
