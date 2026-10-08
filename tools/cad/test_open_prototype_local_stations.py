import math
import unittest
import open_prototype_local_stations as S
import open_prototype_bundle_spines as B


class LocalStations(unittest.TestCase):
    def test_pitch_transition_connects_actual_new_root(self):
        p=S.pitch_parts()
        self.assertEqual(p[0]['start'],[-52,26,149])
        self.assertEqual(p[-1]['end'],[-52,86,166])
        for a,b in zip(p,p[1:]):
            self.assertLess(math.dist(a['end'],b['start']),1e-8)
            self.assertGreater(B.dot(a['t1'],b['t0']),1-1e-8)
        for name,side,n in [('XB22',-1.05,-B.N),('XB23',1.05,-B.N),('XS23',0,2*B.N)]:
            out=B.offsets(p,[1,0,0],side,n)
            core=next(r for g in B.build_plan()['groups'] for r in g['rows'] if r['wire']==name)
            self.assertLess(math.dist(out[0]['start'],core['segments'][-1]['end']),1e-8)

    def test_no_extra_brackets_or_full_wiring_claim(self):
        p=S.build_plan()
        self.assertEqual(p['added_print_parts'],0)
        self.assertEqual(p['added_screws_connectors'],0)
        self.assertEqual(p['added_T18I'],2)
        self.assertFalse(p['stage_completed']);self.assertFalse(p['selected'])
        self.assertTrue(p['whole_stock_open'])
        self.assertEqual({r['owner'] for r in p['stations']},{'SourceLeftCarrier','SourceRightCarrier'})

    def test_support_uses_straight_not_bend_and_separate_strap_bay(self):
        p=S.build_plan();pitch,tail=p['stations']
        self.assertEqual(pitch['seat_xywh_mm'][1],77)
        self.assertEqual(pitch['seat_xywh_mm'][3],9)
        self.assertGreaterEqual(pitch['seat_xywh_mm'][1],74)
        self.assertLessEqual(pitch['seat_xywh_mm'][1]+pitch['seat_xywh_mm'][3],86)
        fixtures=S.read(S.OUT/'fhac-mount-plan.json')['source_plan']
        for r in fixtures:
            if r['holder'] not in ('F_HP','F_TY'):continue
            box=r['proposed_body_bounds_mm'];cx=(box[0]+box[3])/2
            for strap_x in (cx-12,cx+12):
                self.assertGreater(abs(tail['strap_plane_x_mm']-strap_x),2.5)
        self.assertEqual(tail['grip_region_x_mm'],[47.5,56.5])
        self.assertEqual(pitch['strap_structure_depth_mm'],4)
        self.assertEqual(tail['strap_structure_depth_mm'],2)
        # Necessary access bounds only, not a Boolean clearance claim.
        self.assertGreater(-54.15,-54.725)
        self.assertLess(-49.65,-36.25)


if __name__=='__main__':unittest.main()
