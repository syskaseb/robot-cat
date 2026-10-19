"""Actual source datums and provenance guards, not whole N01 acceptance."""
import json
import math
import unittest
from pathlib import Path

OUT=Path(__file__).resolve().parents[2]/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class ActiveDatums(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads((OUT/'n01-active-Pi-BUS-datums.json').read_text())

    def test_board_thickness_uses_parallel_source_faces_not_group_centre(self):
        for b in self.p['boards']:
            a,c=b['large_plane_faces']
            n=a['normal']
            delta=[y-x for x,y in zip(a['centre_mm'],c['centre_mm'])]
            self.assertAlmostEqual(abs(sum(x*y for x,y in zip(n,delta))),1.6,places=5)
            self.assertAlmostEqual(sum(x*y for x,y in zip(n,c['normal'])),-1,places=6)
        bus=self.p['boards'][1]
        x=sum(face['centre_mm'][0] for face in bus['large_plane_faces'])/2
        self.assertAlmostEqual(x,130.5,places=5)
        self.assertGreater(abs(x-126),4)

    def test_pi_mounting_axes_are_four_actual_cylinders(self):
        holes=self.p['boards'][0]['cylindrical_surfaces']
        self.assertEqual(len(holes),4)
        n=self.p['boards'][0]['large_plane_faces'][0]['normal']
        for h in holes:
            self.assertAlmostEqual(h['radius_mm'],1.375)
            self.assertAlmostEqual(abs(sum(a*b for a,b in zip(n,h['axis']))),1)

    def test_eleven_unique_jacket_mouths_have_unit_departure_axes(self):
        mouths=self.p['occupied_jacket_mouths']
        self.assertEqual(len(mouths),11)
        self.assertEqual(len({tuple(m['point_mm']) for m in mouths}),11)
        for m in mouths:self.assertAlmostEqual(math.dist(m['departure_axis'],[0,0,0]),1)

    def test_pi_budgets_remain_reservations_and_USB_assumptions_unchanged(self):
        rows=[r for r in self.p['Pi_BUS_parts'] if r['name'].startswith('PiBudget:')]
        contract=json.loads((OUT/'n01-pi-full-port-contract.json').read_text())
        self.assertEqual(len(rows),len(contract['parts'])+len(contract['additional_reservations'])+1)
        self.assertTrue(all(r['kind']=='reservation' for r in rows))
        cable=self.p['USB_project_contract']
        self.assertEqual((cable['catalogue_total_mm'],cable['project_external_target_mm'],cable['project_OD_mm'],cable['minimum_fixed_project_R_mm']),(500,452,5,30))
        self.assertTrue(cable['external452_mm_is_project_mould_allowance_not_supplier_guarantee'])
        self.assertFalse(self.p['selected']);self.assertFalse(self.p['N01_complete'])
        self.assertEqual((self.p['shared_portions'],self.p['shared_ends']),(123,246))

    def test_local_USB_layer_has_two_mm_window_not_whole_volume_approval(self):
        c=self.p['necessary_local_layer_constraints']
        self.assertEqual(c['USB_axis_Z_interval_mm'],[86.75,88.75])
        for a,b in zip(c['necessary_inverted_Pi_PCB_Z_interval_mm'],[92.05,94.05]):self.assertAlmostEqual(a,b)
        self.assertTrue(c['NOT_globally_free_volume']);self.assertTrue(c['no_new_pose_chosen'])
        self.assertIn('MAIN whole stack',c['unresolved_exclusions'])


class RearPlanningGates(unittest.TestCase):
    def test_USB_whole_length_volume_and_both_full_lands(self):
        p=json.loads((OUT/'n01-joint-rear-service-bay-plan.json').read_text())
        self.assertTrue(p['USB_valid']);self.assertEqual(p['USB_solids'],1)
        self.assertAlmostEqual(p['USB_length_mm'],452,places=5)
        expected=math.pi*2.5**2*p['USB_length_mm']
        self.assertAlmostEqual(p['USB_volume_mm3'],expected,delta=expected*1e-4)
        self.assertAlmostEqual(math.dist(*p['source_full9_mm']),9)
        bus=p['BUS_first3_and_full9_mm']
        self.assertAlmostEqual(math.dist(bus[0],bus[1]),3)
        self.assertAlmostEqual(math.dist(bus[1],bus[2]),9)
        self.assertGreaterEqual(p['coil']['minimum_spline_R_mm'],30)
        self.assertFalse(p['sampled_self_contact']);self.assertFalse(p['N01_complete'])

    def test_joint_BUS_pose_uses_actual_mouth_not_group_centre(self):
        p=json.loads((OUT/'n01-joint-rear-service-bay-plan.json').read_text())
        old=json.loads((OUT/'n01-physical-cable-contract.json').read_text())['usb']['bus_jacket_mouth_mm']
        a=math.radians(p['BUS_relative_placement']['rotation_X_deg']);c,s=math.cos(a),math.sin(a)
        rotated=[old[0],c*old[1]-s*old[2],s*old[1]+c*old[2]]
        q=[x+y for x,y in zip(rotated,p['BUS_relative_placement']['translation_mm'])]
        self.assertLess(math.dist(q,p['BUS_new_mouth_mm']),1e-8)
        self.assertAlmostEqual(p['BUS_actual_source_PCB_datum_mm'][0],130.5,places=5)

    def test_bridge_preserves_eight_real_holes_and_positive_load_path(self):
        p=json.loads((OUT/'n01-two-flank-tail-bridge-plan.json').read_text())
        holes=p['original_P0_four_D2p6_and_tail_four_D3p4_axes']
        self.assertEqual(len(holes),8);self.assertTrue(all(h['filled_mm3']<1e-5 for h in holes))
        self.assertEqual(sorted(round(h['radius_mm'],1) for h in holes),[1.3]*4+[1.7]*4)
        self.assertTrue(p['new_valid']);self.assertEqual(p['new_solids'],1)
        self.assertLess(p['kept_material_missing_mm3'],1e-6)
        self.assertTrue(all(j['positive_common_mm3']>5 for j in p['joints']))
        self.assertGreaterEqual(p['USB_whole_gap_mm'],1.25);self.assertFalse(p['N01_complete'])

    def test_received_Pi_source_has_seven_ends_not_seven_complete_grip_kits(self):
        p=json.loads((OUT/'n01-fore-coil-service-deck-received.json').read_text())
        rows=[r for r in p['geometry'] if r['role'] in ('PiRigid','PiFlexible')]
        self.assertEqual(len(rows),35)
        self.assertEqual(sum(r['role']=='PiFlexible' for r in rows),7)
        self.assertTrue(all(not r['name'].endswith(':grip') for r in rows))

    def test_after_turn_carrier_keeps_factory_geometry_and_full9(self):
        p=json.loads((OUT/'n01-fpwm-after-turn-carrier-plan-v3.json').read_text())
        self.assertEqual(p['status'],'F_PWM_AFTER_TURN_CARRIER_LOCAL_PLAN_RECEIVED')
        self.assertEqual(len(p['retired_old_printed_grips_only']),6)
        self.assertEqual(len(p['unchanged_factory_records']),5)
        self.assertEqual(p['selected_ties'],3)
        self.assertTrue(p['full_factory_curves_unchanged'])
        for land in p['lands']:self.assertAlmostEqual(math.dist(land['start_mm'],land['end_mm']),9)
        self.assertGreater(p['positive_frame_joint_mm3'],5)
        self.assertTrue(all(r['ok'] and r['common_mm3']<1e-5 for r in p['checks']))
        seams=[r for r in p['checks'] if r.get('tangent_boundary_evidence')]
        self.assertEqual(len(seams),2)
        for r in seams:
            for pair in r['tangent_boundary_evidence']['witness_pairs_mm']:
                self.assertLess(math.dist(*pair),1e-5)
                for point in pair:self.assertAlmostEqual(point[1],62.6,places=5)
        self.assertTrue(p['additional_case_tie_stock_not_yet_allocated'])
        self.assertFalse(p['N01_complete']);self.assertFalse(p['physical_pass'])

    def test_carrier_constructor_matches_saved_material_not_only_json_flags(self):
        import hashlib
        from plan_feline_usb_service_bight import fpwm_after_turn_carrier
        p=json.loads((OUT/'n01-fpwm-after-turn-carrier-plan-v3.json').read_text())
        carrier,ties,info=fpwm_after_turn_carrier()
        shapes={'carrier':carrier,**ties}
        self.assertEqual(set(shapes),{r['name'] for r in p['geometry']})
        for row in p['geometry']:
            actual=hashlib.sha256(shapes[row['name']].exportBrepToString().encode()).hexdigest()
            self.assertEqual(actual,row['sha256'],row['name'])

    def test_whole_fore_recipe_recovers_P_REAR_and_rejects_missing_part(self):
        from plan_feline_usb_service_bight import complete_source_station_groups
        p=json.loads((OUT/'n01-fore-coil-service-deck-received.json').read_text())
        rows=[r for r in p['geometry'] if r['name'].startswith('Station:')]
        metadata={r['name']:{'group':r['role']} for r in rows}
        self.assertEqual(complete_source_station_groups(p,metadata),{'FR_P','P_REAR','RR_P'})
        rear=[r['name'] for r in rows if r['role']=='P_REAR'];self.assertEqual(len(rear),9)
        metadata.pop(rear[-1])
        with self.assertRaises(AssertionError):complete_source_station_groups(p,metadata)

    def test_full_boot_gets_space_beyond_minimum_land_without_shortening_USB(self):
        p=json.loads((OUT/'n01-joint-rear-boot-budget-plan.json').read_text())
        self.assertEqual(p['allocated_BUS_outside_tangent_mm'],30)
        self.assertAlmostEqual(p['USB_length_mm'],452,places=5)
        self.assertGreaterEqual(p['coil']['minimum_spline_R_mm'],30)
        self.assertAlmostEqual(math.dist(*p['BUS_first3_and_full9_mm'][1:]),9)
        receipt=json.loads((OUT/'n01-joint-rear-boot-intrinsic-received.json').read_text())
        self.assertEqual(receipt['status'],'USB_FULL_BOOT_CORE_INTRINSIC_CLEAR_WORLD_OPEN')
        self.assertEqual(len(receipt['checks']),7);self.assertTrue(all(r['ok'] for r in receipt['checks']))
        boot=next(r for r in receipt['checks'] if r['part']=='CurrentBUS:USB_C_Overmould')
        self.assertEqual(boot['positive_common_mm3'],0)
        self.assertFalse(receipt['N01_complete'])


if __name__=='__main__':unittest.main()
