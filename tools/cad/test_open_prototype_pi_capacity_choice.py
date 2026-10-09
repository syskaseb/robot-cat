import unittest,math
import open_prototype_pi_capacity_choice as G
import open_prototype_source_receiving_family as F
import open_prototype_source_group as B

class CapacityChoice(unittest.TestCase):
    def test_whole_family_current_ends_and_preserved_partials(self):
        p=G.build();old=F.build()
        self.assertEqual(p['s1_module'],old['s1_module'])
        self.assertEqual(p['permutation'],old['permutation'])
        for role in ('F_HY','F_HP','F_TY','F_AUX'):
            self.assertEqual(next(h for h in p['holders'] if h['role']==role),next(h for h in old['holders'] if h['role']==role))
        self.assertEqual(p['s1_routes'],[])
        for e in p['body_ends']:self.assertEqual(e['datum'],p['ports'].get(e['current_role']))
        h=next(h for h in p['holders'] if h['role']=='F_PI')
        self.assertLess(h['input_blank_mm'],50)
        self.assertLess(math.dist(h['centre_mm'],[7,-37,101.5]),1e-7)
        self.assertLess(math.dist(h['output_mm'],[7,-36,76]),1e-7)
        for side in ('input','output'):B.check_path(h[side+'_segments'],h[side+'_mm'],min_radius=6)
        self.assertGreater(B.dot(B.segment_geometry(h['output_segments'][-1])[2],B.EAST),1-1e-7)
        self.assertLess(B.dot(B.segment_geometry(h['input_segments'][-1])[2],p['ports'][h['input_target']]['departure']),-1+1e-7)

if __name__=='__main__':unittest.main()
