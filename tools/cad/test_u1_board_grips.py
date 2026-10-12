import unittest
import plan_u1_board_grips as P


class BoardGripPlanTests(unittest.TestCase):
    def setUp(self):self.p=P.allocation()

    def test_all_nine_remaining_board_ends_once(self):
        ends=[n for g in self.p['groups'] for n in g['ends']]
        self.assertEqual(set(ends),{'XL01/b','XL07/b','XL10/b','XL08/b','XL09/a',
            'XL02/a','XS11/b','XS21/b','XS31/b'})
        self.assertEqual(len(ends),9)
        self.assertEqual(sum(g.get('T18R',0) for g in self.p['groups']),3)
        self.assertEqual(self.p['lacing_blanks_mm'],[150,150,150])

    def test_existing_stack_unchanged_and_no_new_screws(self):
        self.assertTrue(self.p['original_foot_eye_and_bolt_stack_unchanged'])
        self.assertEqual(self.p['new_screws'],0)
        self.assertEqual(self.p['replaces'],['U1_AnchorLeft','U1_AnchorRight'])

    def test_fine_wires_share_one_flat_seat(self):
        seats=[p for p in self.p['pads'] if p['name']=='FineSeat']
        self.assertEqual(len(seats),1)
        self.assertGreater(seats[0]['bounds_mm'][4]-seats[0]['bounds_mm'][1],2*1.27+.8)
        self.assertFalse(self.p['selected']);self.assertFalse(self.p['physical_pass'])

    def test_original_band_and_head_interfaces_not_filled(self):
        cuts={c['name']:c for c in self.p['cuts']}
        self.assertEqual(cuts['ExistingBandPassage']['bounds_mm'][2],86.3202)
        self.assertGreaterEqual(cuts['ExistingHeadClearance']['radius_mm'],1.9+.2)


if __name__=='__main__':unittest.main()
