import unittest, math
import open_prototype_source_receiving_family as G
import open_prototype_rr_receiving_branch as R
import open_prototype_source_group as B

class CoupledFamily(unittest.TestCase):
    def test_rebind_and_no_stale_source_routes(self):
        p=G.build();old=R.build()
        self.assertEqual((len(p['ports']),len(p['body_ends'])),(100,160))
        self.assertEqual(p['s1_routes'],[])
        for e in p['body_ends']:
            self.assertEqual(e['datum'],p['ports'].get(e['current_role']))
        self.assertEqual(p['permutation'],old['permutation'])
        self.assertEqual(next(r for r in p['tails'] if r['wire']=='W053'),
                         next(r for r in old['tails'] if r['wire']=='W053'))

    def test_entire_PI_and_three_FHAC_inputs(self):
        p=G.build();old=R.build()
        for h in p['holders']:
            if h['role'] not in ('F_PI','F_HY','F_HP','F_TY'):continue
            end=p['ports'][h['input_target']]
            B.check_path(h['input_segments'],h['input_mm'],end['point_mm'],6)
            self.assertLess(B.dot(B.segment_geometry(h['input_segments'][-1])[2],end['departure']),-0.999999)
            self.assertGreaterEqual(math.dist(h['input_segments'][-1]['start'],h['input_segments'][-1]['end']),9-1e-6)
            self.assertLessEqual(h['input_blank_mm'],50 if h['role']=='F_PI' else 84.5)
        a=next(h for h in p['holders'] if h['role']=='F_PI')
        b=next(h for h in old['holders'] if h['role']=='F_PI')
        for k in ('input_mm','output_mm','centre_mm','sleeve_start_mm','sleeve_end_mm','new_insulation_end_mm'):
            self.assertEqual(a[k],B.add(b[k],[-60,0,0]))

if __name__=='__main__':unittest.main()
