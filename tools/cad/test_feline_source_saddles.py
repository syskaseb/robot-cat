import unittest
import FreeCAD
from feline_source_saddles import build
from plan_feline_battery_f0_joint import path


class SourceSaddles(unittest.TestCase):
    def test_current_source_overlay_reuses_three_HP_and_five_U1_without_new_contacts(self):
        from compose_feline_received_source_boundaries import current
        base,rows,_=current();index={e['id']:e for e in rows}
        self.assertEqual(len(base['portions']),123);self.assertEqual(len(rows),246)
        for w in ('XS13','XS23','XS33'):
            self.assertEqual(index[w+'/extra/start']['routing_exit_mm'][1],41)
        for eid in ('XB22/extra/end','XB23/extra/start','XS23/extra/end'):
            self.assertEqual(index[eid]['routing_exit_mm'][0],-35.)
            self.assertEqual(index[eid]['support_owner'],'HPJR:carrier')
            self.assertFalse(index[eid]['full_middle_route_accepted'])

    def test_five_U1_grips_have_whole_print_static_and36_receipt_not_N01(self):
        import json
        from plan_feline_layout import OUT
        r=json.loads((OUT/'n01-U1-frontband-common-received.json').read_text())
        self.assertFalse(r['failures']);self.assertEqual(len(r['completed_static']),29)
        self.assertEqual(len(r['completed_motion']),29)
        self.assertTrue(all(p['valid'] and p['solids']==1 and max(p['envelope_mm'])<250 for p in r['whole_prints'].values()))
        self.assertTrue(all(':bare|' in key for key in r['reused_unchanged_source_queries']))
        self.assertFalse(r['N01_complete']);self.assertFalse(r['physical_pass']);self.assertFalse(r['native_changed'])

    def test_three_flat_U1_lands_keep9mm_R12_6_and_full_selected_heads(self):
        import json
        from plan_feline_layout import OUT
        from receive_feline_rrp_shared_height import load
        r=json.loads((OUT/'n01-U1-frontband-common-plan.json').read_text());shapes=load(r)
        self.assertEqual(len(r['lands']),5);self.assertEqual(r['selected_T18I'],4)
        self.assertTrue(r['all_heads_above_jackets']);self.assertTrue(r['no_selected_bought_SKU_change'])
        for w in ('XS13','XS23','XS33'):
            p,q=r['lands'][w]['grip9_mm'];self.assertAlmostEqual(FreeCAD.Vector(*p).distanceToPoint(FreeCAD.Vector(*q)),9.)
            self.assertAlmostEqual(shapes['U1Relief:'+w+':head'].Volume,5*4.3*5.3)
            for part in r['specs'][w+'/extra/start']['parts']:
                if part['kind']=='arc':self.assertEqual(part['radius_mm'],12.6)

    def test_V_clamp_post_is_own_base_only_for_its_nylon(self):
        from receive_feline_u1_common_restraints import minimum
        post='U1Relief:ForePost0';band='U1Relief:XSbundle:band'
        plan=dict(intended_insulation_mates={},whole_clamp_Y_mm=[32,41],print_groups={'fore':[post,'U1Relief:XSbundle:pad']})
        self.assertEqual(minimum(post,band,{},plan,{},set())[0],.2)
        self.assertEqual(minimum(post,'U1Five:XS13:bare',{},plan,{},set())[0],1.25)
        self.assertEqual(minimum('unrelated_printed_frame',band,{},plan,{},set())[0],1.25)

    def test_same_T18I_head_is_a_mate_not_an_independent_stock_piece(self):
        from receive_feline_u1_common_restraints import minimum
        head='U1Relief:XS13:head';band='U1Relief:XS13:band';other='U1Relief:XS33:band'
        meta={n:dict(kind='T18I') for n in (head,band,other)}
        plan=dict(intended_insulation_mates={})
        self.assertEqual(minimum(head,band,meta,plan,{},set())[0],0.)
        self.assertEqual(minimum(head,other,meta,plan,{},set())[0],.2)

    def test_U1_intrinsic_seat_policy_never_waives_foreign_or_other_wire(self):
        from map_feline_source_allocations import inherited_u1_limit
        seat='Ref_Material_U1_AnchorLeft_0_0'
        self.assertEqual(inherited_u1_limit('U1Local:XL01:jacket',seat)[0],0.)
        self.assertEqual(inherited_u1_limit('U1Local:XL01:bare',seat)[0],.2)
        self.assertEqual(inherited_u1_limit('U1Local:XL01:jacket','FactoryW044')[0],1.25)
        self.assertEqual(inherited_u1_limit('U1Under:XL01:jacket',seat)[0],1.25)
        self.assertEqual(inherited_u1_limit('U1Local:XL01:jacket','Ref_Material_Pi4NominalPCB_0_0')[0],1.25)

    def test_reconciled_U1_receipt_preserves_negative_and_exact_nine_touches(self):
        import json
        from plan_feline_layout import OUT
        r=json.loads((OUT/'n01-U1-intrinsic-mates-reconciled.json').read_text())
        prior=json.loads((OUT/'n01-inherited-local-source-neighbor-map.json').read_text())
        self.assertTrue(prior['failures']);self.assertFalse(r['failures'])
        self.assertFalse(r['N01_complete']);self.assertFalse(r['new_wire_or_native_geometry'])
        self.assertEqual(r['reused_queries'],len(prior['checks']))
        touched=[v for v in r['corrected_policy_pairs'].values() if 'actual_common_volume_mm3' in v]
        self.assertEqual(len(touched),9)
        self.assertTrue(all(v['actual_common_volume_mm3']==0 for v in touched))

    def test_U1_remaining_five_whole_pair_accounts_for_bare_and_fixed_arm(self):
        import json
        from plan_feline_layout import OUT
        r=json.loads((OUT/'n01-U1-remaining-five-coupled-plan.json').read_text())
        gate=json.loads((OUT/'n01-U1-remaining-five-coupled-plan-neighbors.json').read_text())
        self.assertEqual(len(r['specs']),5);self.assertEqual(len(r['geometry']),10)
        self.assertFalse(gate['failures']);self.assertEqual(len(gate['completed']),10)
        self.assertEqual(len(gate['reused_exact_queries']),19)
        lo,hi=r['coupled_E2_pitch_interval_mm']
        self.assertGreater(r['E2_layer_pitch_mm'],lo);self.assertLess(r['E2_layer_pitch_mm'],hi)
        self.assertFalse(r['selected_parts_or_pad_identities_changed']);self.assertFalse(r['N01_complete'])

    def test_source_root_whole_case_bypass_not_a_partial_or_print_PASS(self):
        import json
        from plan_feline_layout import OUT
        r=json.loads((OUT/'n01-source-restraints-head-case-bypass.json').read_text())
        self.assertFalse(r['failures']);self.assertEqual(len(r['completed_static']),27)
        self.assertEqual(len(r['completed_motion']),27)
        self.assertTrue(r['all14_U1_local_sources_included'])
        self.assertEqual(r['current_lower_connectivity_proof']['solids'],1)
        self.assertTrue(r['current_lower_connectivity_proof']['within250_margin'])
        self.assertFalse(r['N01_complete']);self.assertFalse(r['physical_pass']);self.assertFalse(r['native_changed'])

    def test_underside_plan_keeps_all14_named_pads_and_lengths(self):
        import json
        from plan_feline_layout import OUT
        from receive_feline_rrp_shared_height import load
        r=json.loads((OUT/'n01-U1-whole14-underside-plan.json').read_text());actors=load(r)
        self.assertEqual(len(r['specs']),14);self.assertEqual(len(actors),28)
        self.assertFalse(r['selected_parts_changed']);self.assertFalse(r['electrical_identities_changed'])
        old=json.loads((OUT/'n01-current-source-MTA-boundary-overlay.json').read_text())['U1_local_prefix_source_allocations']
        for eid,source in old.items():
            target=r['specs'][eid]
            self.assertEqual(target['pad_world_mm'],source['pad_world_mm'])
            self.assertEqual(target['radius_mm'],source['radius_mm'])
            self.assertAlmostEqual(sum(__import__('feline_source_saddles').segment(p).Length for p in source['parts']),
                                   sum(__import__('feline_source_saddles').segment(p).Length for p in target['parts']),places=6)
        self.assertFalse(r['N01_complete'])

    def test_E2_uses_actual_carrier_pads_not_old_pin_coordinates(self):
        import json
        from plan_feline_layout import OUT
        r=json.loads((OUT/'n01-U1-whole14-underside-plan.json').read_text());spec=r['specs']
        self.assertEqual(spec['XP02.module/extra/end']['selected_carrier_pad_identity'],'XP02.board')
        self.assertAlmostEqual(spec['XP02.module/extra/end']['pad_world_mm'][0],29.37)
        self.assertAlmostEqual(spec['XP03.module/extra/end']['pad_world_mm'][0],26.83)
        a=r['updates']['XP02.module/extra/end']['jacket_routing_point_mm']
        b=r['updates']['XP03.module/extra/end']['jacket_routing_point_mm']
        self.assertAlmostEqual(abs(a[2]-b[2]),3.)
        self.assertTrue(r['whole225mm_Molex_corridors_NOT_received'])

    def test_working_register_has_current_source_and_MTA_not_old_mouths(self):
        import json
        from compose_feline_source_mta_boundaries import current
        from receive_feline_existing_lower_caps import current as old
        from plan_feline_layout import OUT
        base,rows,_=current();_,prior,_=old();index={r['id']:r for r in rows}
        self.assertEqual(len(base['portions']),123)
        self.assertEqual([r['id'] for r in rows],[r['id'] for r in prior])
        self.assertEqual(len(rows),246)
        src=json.loads((OUT/'n01-F0-access-stack.json').read_text())
        self.assertEqual(index['W075/retained0/start']['point_mm'],src['recipes']['W075_factory']['parts'][0]['start'])
        self.assertEqual(index['W041/custom/start']['routing_exit_mm'],[109.49999971389771,83.64999999999999,45.26])
        self.assertTrue(index['W076/retained1/start']['source_restraint_shared_shelf_NOT_accepted'])
        for before,after in zip(prior,rows):
            for k in ('id','wire','portion_id','endpoint','group'):self.assertEqual(before[k],after[k])
            if before['point_mm'] is None:self.assertIsNone(after['point_mm'])

    def test_current_HP_register_requires_selected_radius_not_legacy_receipt(self):
        import json
        from compose_feline_received_source_boundaries import current
        from plan_feline_layout import OUT
        base,rows,_=current()
        proof=json.loads((OUT/'n01-HP-selected-R12p6-received.json').read_text())
        for g in proof['geometry']:
            r=next(e for e in rows if e.get('prefix_geometry_owner')==g['name'])
            self.assertEqual(r['received_prefix_R_mm'],12.6)
            self.assertEqual(r['source_prefix_length_mm'],g['path_length_mm'])
            self.assertEqual(r['jacket_grip9_mm'],g['source_full9_mm'])
            self.assertIn('HEAD_MOTION_SKIN_OPEN',r['routing_boundary_status'])
        self.assertEqual(len(rows),246)
        self.assertEqual(len(base['portions']),123)

    def test_tie_pad_contact_is_mating_not_foreign_clearance(self):
        from receive_feline_source_restraints import local_limit
        p='SourceGrip:POSTIN:'
        meta={p+'pad':dict(kind='PETG',print_group='upper'),p+'band':dict(kind='T18I',print_group='upper'),p+'head':dict(kind='T18I',print_group='upper')}
        self.assertEqual(local_limit(p+'band',p+'pad',meta,{}, {'POSTIN':{'wire':'factory'}},{}),0.)
        self.assertEqual(local_limit(p+'head',p+'pad',meta,{}, {'POSTIN':{'wire':'factory'}},{}),.2)
        self.assertEqual(local_limit(p+'band','foreign_wire',meta,{}, {'POSTIN':{'wire':'factory'}},{}),1.25)

    def test_full_nine_on_first_R12_arc_no_extra_length(self):
        r=path([0,0,0],[2**-.5,2**-.5,0],[('turn',[-2**-.5,2**-.5,0])],12.4)
        kit,rec=build(r['parts'][0],.3,[0,0,-1],7.)
        self.assertEqual(rec['full_jacket_grip_arclength_mm'],[.3,9.3])
        self.assertEqual(rec['extra_wire_length_mm'],0)
        self.assertAlmostEqual(kit['head'].Volume,5*4.3*5.3,places=5)

    def test_early_vertical_R25_grip_and_whole_head(self):
        r=path([0,0,0],[0,0,-1],[('turn',[-3**.5/2,-.5,0])],25.2)
        kit,rec=build(r['parts'][0],3,[-.5,3**.5/2,0],9)
        self.assertEqual(rec['full_jacket_grip_arclength_mm'],[3,12])
        self.assertEqual(len(kit['pad'].Solids),1)

    def test_reject_invented_grip_beyond_existing_segment(self):
        r=path([0,0,0],[1,0,0],[('line',8)],12.4)
        with self.assertRaises(AssertionError):build(r['parts'][0],0,[0,0,-1],4.5)


if __name__=='__main__':unittest.main()
