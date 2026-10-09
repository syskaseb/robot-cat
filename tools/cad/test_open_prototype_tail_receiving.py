import unittest
import open_prototype_rl_tail_group as T
B=T.B

class TailReceiving(unittest.TestCase):
    def test_whole_factory_joint_changes_together(self):
        p=T.build();h=next(h for h in p['holders'] if h['role']=='F_TY')
        B.check_path(h['output_segments'],h['output_mm'],min_radius=6)
        self.assertLessEqual(h['output_prefix_mm'],84.5)
        for key,offset in [('sleeve_start_mm',-17.25),('sleeve_end_mm',9.25),('new_insulation_end_mm',18.25)]:
            self.assertEqual(h[key],B.add(h['output_segments'][-1]['end'],B.mul(B.DOWN,offset)))
        r=next(r for r in p['protected_receiving_rows'] if r['wire']=='XB32')
        B.check_path(r['segments'],r['segments'][0]['start'],[68,-45,130],12.6)
        B.check_path(h['output_segments']+r['segments'])
        self.assertAlmostEqual(B.segment_geometry(r['segments'][-1])[0],9)
        self.assertTrue(r['moving_continuation_not_qualified'])

    def test_mta_both_factory_ends_and_ledgers_retained(self):
        p=T.build()
        for r in p['tails']:
            if r['wire'] not in ('W044','W045'):continue
            self.assertLessEqual(r['required_blank_mm'],100)
            self.assertIn(r['target'],[e['current_role'] for e in p['body_ends'] if e['wire']==r['wire']])
            B.check_path(r['segments'],end=p['ports'][r['target']]['point_mm'],min_radius=r['min_radius_mm'])
        report=T.F.F.proximity(p)
        self.assertFalse(any(r['status']=='REJECT_PLANNING_PROXIMITY' for r in report['near_pairs']))

if __name__=='__main__':unittest.main()
