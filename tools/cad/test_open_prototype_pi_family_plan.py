import unittest,math
import open_prototype_pi_family_plan as G
import open_prototype_source_receiving_family as F
import open_prototype_source_group as B

class PIFamily(unittest.TestCase):
    def test_whole_family_and_port_binding(self):
        p=G.build();old=F.build()
        self.assertEqual(p['s1_module'],old['s1_module'])
        self.assertEqual(p['permutation'],old['permutation'])
        for name in ('F_HY','F_HP','F_TY'):
            self.assertEqual(next(h for h in p['holders'] if h['role']==name),next(h for h in old['holders'] if h['role']==name))
        for e in p['body_ends']:self.assertEqual(e['datum'],p['ports'].get(e['current_role']))
        h=next(h for h in p['holders'] if h['role']=='F_PI')
        self.assertLess(math.dist(h['centre_mm'],[33,27,101.5]),1e-7)
        for name in ('input','output'):B.check_path(h[name+'_segments'],h[name+'_mm'],min_radius=6)
        self.assertLess(math.dist(h['output_mm'],[33,26,76]),1e-7)
        self.assertEqual(h['sleeve_start_mm'],[33,32.75,67])
        self.assertGreaterEqual(h['sleeve_start_mm'][1]-3,28)
        self.assertGreater(B.dot(B.segment_geometry(h['output_segments'][-1])[2],B.NORTH),1-1e-7)
        self.assertLess(B.dot(B.segment_geometry(h['input_segments'][-1])[2],p['ports'][h['input_target']]['departure']),-0.999999)

if __name__=='__main__':unittest.main()
