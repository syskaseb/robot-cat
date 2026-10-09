import unittest,math
import open_prototype_aux_fanout_plan as F
import open_prototype_aux_fanout_choice as G
import open_prototype_source_group as B

class SharedFanout(unittest.TestCase):
    def test_three_inputs_lengths_and_straights(self):
        p=G.build()
        for role,last,limit in [('F_PI',9,50),('F_HY',27,84.5),('F_HP',18,84.5),('F_TY',9,84.5)]:
            h=next(h for h in p['holders'] if h['role']==role)
            B.check_path(h['input_segments'],h['input_mm'],p['ports'][h['input_target']]['point_mm'],6)
            self.assertLessEqual(h['input_blank_mm'],limit)
            self.assertGreaterEqual(math.dist(h['input_segments'][-1]['start'],h['input_segments'][-1]['end']),last-1e-6)
            self.assertLess(B.dot(B.segment_geometry(h['input_segments'][-1])[2],p['ports'][h['input_target']]['departure']),-1+1e-7)

    def test_complete_outputs_receivers_and_one_current_endset(self):
        p=G.build();base=F.build()
        for h in p['holders']:B.check_path(h['output_segments'],h['output_mm'],min_radius=6)
        self.assertEqual(len(p['body_ends']),160)
        self.assertEqual(len(p['ports']),100)
        self.assertEqual(p['permutation'],base['permutation'])
        for e in p['body_ends']:self.assertEqual(e['datum'],p['ports'].get(e['current_role']))
        for r in p['protected_receiving_rows']:
            B.check_path(r['segments'],end=r['station_mm'],min_radius=12.6)
            self.assertGreaterEqual(math.dist(r['segments'][-1]['start'],r['segments'][-1]['end']),9-1e-7)
            h=next(h for h in p['holders'] if h['role']==r['holder'])
            B.check_path(h['output_segments']+r['segments'],h['output_mm'],r['station_mm'])
        self.assertEqual(p['s1_routes'],[])

    def test_mutual_screen_before_CAD(self):
        p=G.compact()
        self.assertFalse(any(r['status']=='REJECT_PLANNING_PROXIMITY' for r in p['mutual_path_preflight']['near_pairs']))
        self.assertFalse(p['selected']);self.assertFalse(p['stage_completed'])

if __name__=='__main__':unittest.main()
