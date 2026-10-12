import unittest
import plan_u1_grouped_grips as P


class GroupedGripPlanTests(unittest.TestCase):
    def setUp(self):self.p=P.allocation()

    def test_actual_hole_axes_not_private_board_copies(self):
        self.assertEqual(self.p['mount_axes_mm']['GPIOGrip'],[[-15.5,24.5],[42.5,24.5]])
        self.assertEqual(self.p['mount_axes_mm']['PCAGrip'],[[-35.825,-9.525],[-35.825,9.525]])

    def test_each_target_insulation_end_has_one_group(self):
        ends=[e for g in self.p['lands'] for e in g['wires']]
        self.assertEqual(len(ends),12)
        self.assertEqual(len(set(ends)),12)
        self.assertEqual(sum(g['T18R'] for g in self.p['lands']),4)
        self.assertEqual(len(self.p['bands']),8)

    def test_thin_band_fits_between_gpio_rows(self):
        self.assertLess(1.4+self.p['tie_supplier']['thickness_mm'],2.54)
        self.assertTrue(self.p['tie_supplier']['head_is_project_reservation'])
        self.assertFalse(self.p['selected']);self.assertFalse(self.p['physical_pass'])

    def test_fine_pwm_common_seat_not_thin_individual_grooves(self):
        seats=[r for r in self.p['pads'] if r['name']=='PWMSeat']
        self.assertEqual(len(seats),1)
        self.assertGreater(seats[0]['bounds_mm'][3]-seats[0]['bounds_mm'][0],7)


if __name__=='__main__':unittest.main()
