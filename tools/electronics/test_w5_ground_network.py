import unittest
from w5_ground_network_plan import profile, ports, attached_ends, recipes
from w5_space_plan_inputs import family


class GroundNetworkTest(unittest.TestCase):
    def test_battery_is_selected_lapp_not_tkd(self):
        p = profile('W001')
        self.assertEqual((p['wire_sku'], p['OD_mm'], p['radius_mm']), ('LAPP0107001', 3.1, 12.4))
        for wire in ('W025', 'W036', 'W061', 'W062', 'W063'):
            self.assertEqual((profile(wire)['OD_mm'], profile(wire)['radius_mm']), (4.2, 21))

    def test_one_complete_scope_not_twenty_six_free_ends(self):
        ends, routes = recipes()
        self.assertEqual((len(ends), len(routes)), (26, 21))
        self.assertTrue(all(r['body_route_complete'] for r in routes))
        self.assertEqual(sum(r['moving_route'] for r in routes), 12)
        self.assertEqual({r['wire'] for r in routes}, {r['wire'] for r in attached_ends()})

    def test_original_g1_cage_labels_and_common_g2_standoff(self):
        datums = ports()
        self.assertEqual(datums['G1.1']['point_mm'], [77, 20.5, 113.5])
        self.assertEqual(datums['G1.2']['point_mm'], [77, -9.5, 113.5])
        self.assertTrue(all(datums['G2.' + str(i)]['point_mm'][2] == 119.5 for i in range(1, 6)))

    def test_adjacent_fillets_fit_without_radius_reduction(self):
        _, routes = recipes()
        self.assertTrue(all(r['radius_mm'] >= 10 for r in routes))
        w = next(r for r in routes if r['wire'] == 'W060')
        self.assertTrue(w['supplier_radius_unknown'])
        self.assertEqual(w['retained_tail_radius_bound_mm'], 6)

    def test_planning_never_treats_hardware_or_candidate_wires_as_petg(self):
        self.assertEqual(family('SourceCover'), 'printed_owner_change_allowed_not_automatically_free_space')
        for key in ('SourceHoodHardware/Bolt0', 'SourceInlet/PlatformNut0_WORLD', 'P_SYS_received'):
            self.assertEqual(family(key), 'received_bought_or_structural_reservation')
        for key in ('ReceivedD/W013', 'ReceivedV/W047'):
            self.assertEqual(family(key), 'unselected_leg_route_coupled_scope')
        self.assertEqual(family('G1_NEW_BODY'), 'ground_block_placement_may_change')


if __name__ == '__main__': unittest.main()
