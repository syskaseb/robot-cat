import unittest
import FreeCAD
from feline_source_saddles import build
from plan_feline_battery_f0_joint import path


class SourceSaddles(unittest.TestCase):
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
