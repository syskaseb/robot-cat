"""Focused pure checks of the current Stage3 endpoint contract."""
import unittest
import open_prototype_wiring_endpoints as E


class EndpointContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = E.read(E.OUT)

    def test_preserves_all_body_net_identities(self):
        old = E.read(E.BASE / 'layout.json')['body_conductors']
        identity = lambda rows: {(r['id'],r['a'],r['b'],r['net']) for r in rows}
        self.assertEqual(identity(old), identity(self.plan['body_conductors']))
        self.assertEqual(len(identity(old)), 80)

    def test_all_current_sources_unchanged(self):
        for path, digest in self.plan['source_sha256'].items():
            self.assertEqual(E.sha(E.ROOT / path), digest, path)

    def test_twelve_factory_looms_keep_one_plug(self):
        self.assertEqual(len(self.plan['leg_looms']), 12)
        for loom in self.plan['leg_looms']:
            self.assertTrue(loom['source_world_frame_retained'])
            self.assertEqual(loom['factory_plugs_installed'], 1)
            self.assertFalse(loom['pin_cavity_order_known'])

    def test_reservations_never_become_invented_pin_points(self):
        ends = [e for r in self.plan['body_conductors'] for e in r['ends'] if 'physical_loom' in e]
        self.assertEqual(len(ends), 36)
        for e in ends:
            self.assertNotIn('point_mm', e)
            self.assertEqual(e['status'], 'CABLE_EXIT_RESERVATION')
            self.assertFalse(e['pin_cavity_order_known'])

    def test_each_wago_port_within_current_casing(self):
        specs = E.read(E.BASE / 'mounting-checkpoint/distribution-mount-plan.json')['distribution']
        by_name = {r['native']:r for r in specs}
        checked = set()
        for row in self.plan['body_conductors']:
            for e in row['ends']:
                if e.get('native') not in by_name:
                    continue
                b = self.plan['components'][e['native']]['bounds_mm']
                x,y,z = e['point_mm']
                self.assertTrue(b[0] <= x <= b[3], e['role'])
                self.assertTrue(b[1]-1e-7 <= y <= b[4]+1e-7, e['role'])
                self.assertTrue(b[2] <= z <= b[5], e['role'])
                self.assertTrue(e['datum_is_not_manufacturer_pin'])
                checked.add(e['native'])
        self.assertEqual(len(checked), 17)  #3 auxiliary buses occur only in boundary

    def test_old_route_lengths_cannot_be_current_cut_list(self):
        for row in self.plan['body_conductors']:
            self.assertIsNone(row['actual_cut_mm'])
            self.assertNotIn('nominal_CP2_blank_mm', row)
        self.assertFalse(self.plan['stage_completed'])
        self.assertFalse(self.plan['W5_complete'])

    def test_all_five_short_source_branches_screened(self):
        self.assertEqual({r['holder'] for r in self.plan['short_source_length_screen']},
            {'F_PI','F_AUX','F_HY','F_HP','F_TY'})
        for row in self.plan['short_source_length_screen']:
            self.assertTrue(row['bound_not_route_or_safety_acceptance'])

    def test_shared_holder_plan_keeps_prefuse_inputs_short(self):
        from open_prototype_wiring_source_layout import build
        plan = build()
        self.assertEqual(len(plan['source_plan']), 5)
        self.assertFalse(plan['candidate_self_bbox_pairs'])
        self.assertFalse(plan['selected'])
        for row in plan['source_plan']:
            self.assertGreaterEqual(row['input_recipe']['entry_straight_mm'], 9)
            self.assertLess(row['nominal_input_blank_mm'], 84.5)
            if row['holder'] in ('F_PI','F_AUX'):
                self.assertLess(row['nominal_input_blank_mm'], 50)
            self.assertTrue(row['both_output_route_and_independent_load_path_pending'])

    def test_port_permutation_is_confined_to_one_existing_bus(self):
        from open_prototype_wiring_source_layout import build
        plan = build()
        mapping = plan['proposed_same_bus_port_permutation']
        self.assertEqual(set(mapping), set(mapping.values()))
        self.assertTrue(all(a.split('.')[0] == b.split('.')[0] for a,b in mapping.items()))
        self.assertFalse(plan['electrical_nets_or_installed_holder_counts_changed'])

    def test_all_mta_exit_reservations_lie_on_current_body_faces(self):
        ends = [e for r in self.plan['distribution_boundary'] for e in r['resolved_datums'].values()
            if e.get('native','').startswith('MTA_')]
        self.assertEqual(len(ends), 8)
        for e in ends:
            b = self.plan['components'][e['native']]['bounds_mm']
            p = e['point_mm']
            self.assertAlmostEqual(p[0], b[0] if e['role'].endswith('.in') else b[3])
            self.assertAlmostEqual(p[1], (b[1]+b[4])/2)
            self.assertAlmostEqual(p[2], (b[2]+b[5])/2)
            self.assertNotIn('extension_port_mm', e)

    def test_shared_five_input_proof_is_current_not_physical_acceptance(self):
        proof = E.read(E.BASE / 'wiring-checkpoint/source-layout-fit.json')
        for path,digest in proof['source_sha256'].items():
            self.assertEqual(E.sha(E.ROOT/path),digest,path)
        self.assertFalse(proof['material_intersections'])
        self.assertFalse(proof['reservation_intersections'])
        self.assertFalse(proof['self_intersections'])
        self.assertFalse(proof['errors'])
        self.assertFalse(proof['selected'])
        self.assertFalse(proof['physical_pass'])
        self.assertEqual(len(proof['five_current_input_routes']),5)
        for r in proof['five_current_input_routes']:
            self.assertTrue(r['swept_solid_valid'])
            self.assertTrue(r['factory_OD_and_R6_not_measured'])
            self.assertGreaterEqual(r['insulated_entry_grip_straight_mm'],9)

    def test_scope_covers_every_wire_edge_and_keeps_four_outputs_open(self):
        from open_prototype_wiring_scope import build
        scope = build()
        source = E.read(E.ROOT/'hardware/electronics/full-cat/connection-map-e4-r1/netlist.json')
        expected = {e['id'] for e in source['edges'] if e['kind']=='wire'}
        covered = {i for r in scope['physical_pair_groups'] for i in r['graph_ids']}
        self.assertEqual(expected,covered)
        self.assertEqual(scope['circuit_wire_edges'],129)
        self.assertEqual(scope['distinct_unordered_wire_pairs'],128)
        self.assertEqual(scope['scopes']['FOUR_MOVED_FHAC_OUTPUTS; LOAD_ENDPOINT_AND_ROUTE_OPEN'],4)
        self.assertEqual(scope['scopes']['LEGACY_SOURCE_920MM; LENGTH_AND_RESTRAINT_RECONCILIATION_OPEN'],2)
        self.assertFalse(scope['stage_completed'])

    def test_pi_output_pair_has_current_evidence_and_no_extra_joint(self):
        p=E.read(E.BASE/'wiring-checkpoint/source-output-plan.json')
        for path,digest in p['source_sha256'].items():self.assertEqual(E.sha(E.ROOT/path),digest,path)
        self.assertEqual(p['status'],'PI_OUTPUT_PATH_CHECKED_SUPPORTS_OPEN')
        self.assertFalse(p['material_or_changed_contacts'])
        self.assertFalse(p['reservation_contacts'])
        self.assertFalse(p['errors']);self.assertFalse(p['self_errors'])
        self.assertEqual(p['splice']['new_connector_or_splice_count'],0)
        self.assertEqual(p['splice']['bare_overlap_mm'],8)
        self.assertEqual(p['splice']['intact_overlap_each_side_mm'],6)

    def test_pi_stock_accounts_strip_and_whole_package_corridor(self):
        p=E.read(E.BASE/'wiring-checkpoint/source-output-plan.json')
        self.assertAlmostEqual(p['W077']['required_blank_mm'],p['W077']['insulated_route_mm']+8)
        self.assertLessEqual(p['W077']['nominal_fit_blank_mm'],p['W077']['factory_minimum_mm'])
        self.assertAlmostEqual(p['W078']['required_blank_mm'],p['W078']['insulated_route_mm']+16)
        self.assertGreater(p['W078']['nominal_fit_blank_mm'],p['W078']['required_blank_mm'])
        plan=p['shared_descent_plan']
        self.assertEqual(set(plan['package_left_limits_mm']),{'holder_budget','input_insulation','retained_left_rail'})
        self.assertAlmostEqual(p['planned_insulated_descent_x_mm']+plan['insulation_radius_mm'],
            min(plan['package_left_limits_mm'].values())-plan['clearance_design_mm'])

    def test_pi_two_independent_grips_never_bear_on_bare_joint(self):
        p=E.read(E.BASE/'wiring-checkpoint/source-output-plan.json');sp=p['splice']
        first,second=sp['required_independent_grips'];half=first['length_mm']/2
        self.assertEqual(first['wire'],'W077');self.assertEqual(second['wire'],'W078')
        self.assertAlmostEqual(first['centre_mm'][0]-half,sp['factory_insulation_boundary_mm'][0]+6)
        self.assertAlmostEqual(second['centre_mm'][0]+half,sp['extension_insulation_boundary_mm'][0]-6)
        self.assertEqual(p['MAIN']['insulated_grip_straight_mm'],9)
        self.assertTrue(all(r['status']=='LOAD_DATUM_OPEN_NO_CENTRE_AS_PIN' for r in p['planned_output_connections'] if r['holder']!='F_PI'))
        self.assertFalse(p['stage_completed']);self.assertFalse(p['selected'])

    def test_pi_saddle_mating_reopen_proof_retains_source_and_no_contacts(self):
        folder=E.BASE/'wiring-checkpoint'
        proof=E.read(folder/'pi-wire-support-checks.json')
        verified=E.read(folder/'pi-wire-support-verification.json')
        for p in (proof,verified):
            for path,digest in p['source_sha256'].items():self.assertEqual(E.sha(E.ROOT/path),digest,path)
            self.assertEqual(E.sha(folder/'PiWireSupportAssembly.FCStd'),p['native_sha256'])
            self.assertFalse(p['stage_completed']);self.assertFalse(p['physical_pass'])
        self.assertFalse(proof['material_neighbour_or_reservation_contacts']);self.assertFalse(proof['errors'])
        self.assertEqual(proof['continuous_service_slide_mm'],[0,35,0])
        self.assertTrue(verified['relocated_fresh_process']);self.assertTrue(verified['source_unchanged'])
        for a,b in zip(verified['initial_volumes_mm3'],verified['restored_volumes_mm3']):self.assertAlmostEqual(a,b,places=5)


if __name__ == '__main__':
    unittest.main()
