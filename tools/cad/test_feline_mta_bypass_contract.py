"""Constructive whole-family evidence is not a whole-N01 or physical PASS."""
import gzip,hashlib,json,subprocess,unittest
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT


def read(name):
    r=json.loads((OUT/name).read_text())
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    return r


class BypassContract(unittest.TestCase):
    def test_complete_current_mta_space_is_not_whole_harness_or_physical_pass(self):
        r=read('n01-MTA-low-stop-cradles-scene.json')
        self.assertEqual(r['status'],'WHOLE_MTA_STATIC36_RECEIVED_ASSEMBLY_ACCESS_AND_SHARED123_OPEN')
        self.assertEqual(len(r['geometry']),72)
        self.assertEqual(set(r['completed_static']),{p['name'] for p in r['geometry']})
        self.assertEqual(set(r['completed_motion']),set(r['completed_static']))
        self.assertTrue(r['motion_is_sampled_not_continuous']);self.assertFalse(r['failures'])
        path=ROOT/r['pair_rows'];self.assertEqual(sha(path),r['pair_rows_sha256'])
        rows=json.loads(gzip.decompress(path.read_bytes()))
        self.assertEqual(len(rows),r['checks']);self.assertTrue(all(v['ok'] for v in rows.values()))
        self.assertTrue(r['assembly_tools_and_common123_capacity_still_OPEN'])
        self.assertTrue(r['digital_nominal_retention_NOT_adhesive_strength_qualification'])
        self.assertFalse(r['N01_complete']);self.assertFalse(r['native_changed']);self.assertFalse(r['physical_pass'])

    def test_whole_case_bays_change_only_own_floor_material(self):
        r=read('n01-MTA-owned-case-bays.json');old=read('n01-MTA-bonded-root-unions.json')
        before={p['name']:p['sha256'] for p in old['geometry']};after={p['name']:p['sha256'] for p in r['geometry']}
        self.assertEqual([n for n in before if before[n]!=after[n]],['LowerBay:ForePanel'])
        self.assertEqual(r['byte_identical_actors_from_prior'],71)
        self.assertLess(r['case_bay_floor_new_material_mm3'],1e-5)
        for p in r['own_complete_case_bays'].values():self.assertGreaterEqual(p['new_gap_mm'],1.5-1e-6)
        self.assertTrue(all(p['current_positive_overlap_mm3']>0 for p in r['current_fore_floor_root_proofs'].values()))
        self.assertEqual(r['current_fore_print_union_solids'],1)
        self.assertFalse(r['native_changed']);self.assertFalse(r['N01_complete'])

    def test_low_stop_plan_uses_whole_world_and_preserves_all_wires(self):
        r=read('n01-MTA-low-stop-cradles.json');old=read('n01-MTA-owned-case-bays.json')
        before={p['name']:p['sha256'] for p in old['geometry']};after={p['name']:p['sha256'] for p in r['geometry']}
        self.assertEqual({n for n in before if before[n]!=after[n]},{'MTACradle:RL','MTACradle:RR'})
        self.assertEqual(r['byte_identical_actors_from_prior'],70)
        self.assertTrue(all(before[n]==after[n] for n in old['recipes']))
        for p in r['shared_low_stop_domains'].values():
            self.assertTrue(p['all_current_fixed_and36motion_considered'])
            self.assertGreaterEqual(p['minimum_case_XY_stop_height_mm'],1.5)
            self.assertLess(p['new_material_outside_old_mm3'],1e-5)
            for row in p['reductions']:
                if 'new_actual_whole_cradle_gap_mm' in row:self.assertGreaterEqual(row['new_actual_whole_cradle_gap_mm'],row['required_margin_mm'])
        self.assertEqual(r['rear_print_union_solids'],1)
        self.assertFalse(r['N01_complete']);self.assertFalse(r['physical_pass'])

    def test_fore_root_contract_has_actual_whole_print_not_a_foreign_waiver(self):
        r=read('n01-MTA-bonded-root-unions.json');old=read('n01-MTA-bonded-cradles.json')
        self.assertEqual(r['geometry'],old['geometry']);self.assertEqual(r['byte_identical_actors_from_prior'],72)
        proof=r['fore_root_print_union'];self.assertEqual(proof['solids'],1);self.assertTrue(proof['valid'])
        self.assertEqual(proof['root'],'StructureReserve:U1CarrierRoot0')
        self.assertEqual(set(r['print_groups']['LowerBay:ForePanel'])-set(old['print_groups']['LowerBay:ForePanel']),{proof['root']})
        self.assertTrue(proof['original_foreign_observation_preserved']);self.assertTrue(proof['no_native_change'])
        self.assertLess(max(proof['print_envelope_mm']),250)
        self.assertFalse(r['N01_complete']);self.assertFalse(r['physical_pass'])

    def test_bonded_cases_do_not_substitute_adhesive_for_wire_relief(self):
        r=read('n01-MTA-bonded-cradles.json');old=read('n01-MTA-body-head-clock.json')
        before={p['name']:p['sha256'] for p in old['geometry']};after={p['name']:p['sha256'] for p in r['geometry']}
        self.assertEqual(len(after),72);self.assertEqual(r['byte_identical_actors_from_prior'],67)
        self.assertEqual(set(before)-set(after),set(r['removed_actor_aliases']))
        self.assertTrue(all(after[n]==before[n] for n in old['recipes']))
        self.assertTrue(r['floor_change_material_subset']);self.assertLess(r['floor_new_material_mm3'],1e-5)
        self.assertEqual(r['uninstalled_rear_T18I_to_spares'],2)
        self.assertEqual(r['selected_VHB_roll_count_NOT_changed'],1);self.assertEqual(r['additional_selected_VHB_draw_mm'],36)
        for p in r['bonded_rear_cases'].values():
            self.assertEqual(p['patch_mm'],[8,18,.5]);self.assertTrue(p['independent_wire_grips_unchanged'])
            self.assertAlmostEqual(p['actual_case_land_coupon_area_mm2'],144)
            self.assertAlmostEqual(p['actual_floor_land_coupon_area_mm2'],144)
            self.assertGreaterEqual(p['minimum_local_floor_thickness_mm'],1.8)
            self.assertTrue(p['adhesion_cleaning_peel_temperature_and_actual_plastic_phase2_gate'])
        self.assertEqual(r['rear_print_union_solids'],1)
        self.assertEqual(len(r['completed_rest']),72);self.assertFalse(r['failures'])
        self.assertFalse(r['physical_pass']);self.assertFalse(r['N01_complete']);self.assertFalse(r['native_changed'])

    def test_rear_keepers_preserve_wire_and_fore_retention_geometry(self):
        r=read('n01-MTA-rear-keepers.json');old=read('n01-MTA-body-head-clock.json')
        before={p['name']:p['sha256'] for p in old['geometry']};after={p['name']:p['sha256'] for p in r['geometry']}
        self.assertEqual(len(after),76);self.assertEqual(r['byte_identical_actors_from_prior'],68)
        self.assertEqual({n for n in before if before[n]!=after[n]},
            {'CaseTie:RL','CaseTie:RLHead','CaseTie:RR','CaseTie:RRHead'})
        self.assertTrue(all(after[n]==before[n] for n in old['recipes']))
        self.assertEqual(len(r['completed_rest']),76);self.assertFalse(r['failures'])
        self.assertEqual(r['rear_print_union_solids'],1);self.assertLess(max(r['rear_print_envelope_mm']),250)
        self.assertTrue(all(p['actual_positive_overlap_mm3']>1 for p in r['new_root_proofs'].values()))
        for p in r['rear_keepers'].values():
            self.assertLess(p['working_loop_mm'],p['working_loop_budget_mm'])
            self.assertGreaterEqual(p['minimum_post_tunnel_side_wall_mm'],2.4)
            self.assertTrue(p['selected_bought_quantity_NOT_changed'])
        self.assertFalse(r['N01_complete']);self.assertFalse(r['native_changed']);self.assertFalse(r['physical_pass'])

    def test_four_full_wire_motions_do_not_award_kit_or_N01(self):
        r=read('n01-MTA-four-wires-motion.json');current=read('n01-MTA-body-head-clock.json')
        self.assertEqual(r['status'],'FOUR_FULL_MTA_WIRES_STATIC_AND36MOTION_RECEIVED_KIT_TOOLS_OPEN')
        self.assertEqual(set(r['completed_motion']),set(current['recipes']))
        self.assertEqual(r['pose_indices'],list(range(36)));self.assertTrue(r['motion_is_sampled_not_continuous'])
        geometry={p['name']:p['sha256'] for p in current['geometry']}
        for name,value in r['source_wire_actor_sha256'].items():self.assertEqual(geometry[name],value)
        path=ROOT/r['pair_rows'];self.assertEqual(sha(path),r['pair_rows_sha256'])
        rows=json.loads(gzip.decompress(path.read_bytes()));self.assertEqual(len(rows),r['checks'])
        self.assertTrue(all(v['ok'] and v['minimum_mm']==1.25 for v in rows.values()))
        self.assertTrue(r['kit_roots_tools_and_shared123_NOT_received']);self.assertFalse(r['N01_complete'])

    def test_prior_rear_hold_interfaces_currently_clear(self):
        r=read('n01-MTA-prior-motion-witnesses.json')
        self.assertEqual(r['status'],'EIGHT_PRIOR_REJECTIONS_CLEAR_ON_CURRENT_SHOES_NOT_WHOLE_KIT')
        self.assertEqual(r['checks'],8);self.assertFalse(r['failures'])
        path=ROOT/r['pair_rows'];self.assertEqual(sha(path),r['pair_rows_sha256'])
        rows=json.loads(gzip.decompress(path.read_bytes()))
        self.assertEqual(len(rows),8)
        for row in rows.values():
            self.assertTrue(row['ok']);self.assertGreaterEqual(row['gap_mm'],1.25)
        self.assertFalse(r['N01_complete']);self.assertFalse(r['native_changed'])

    def test_full_body_tie_budget_and_single_head_delta(self):
        r=read('n01-MTA-body-head-clock.json');prior=read('n01-MTA-body-retention.json')
        before={p['name']:p['sha256'] for p in prior['geometry']};after={p['name']:p['sha256'] for p in r['geometry']}
        self.assertEqual(len(after),72)
        self.assertEqual([n for n in before if before[n]!=after[n]],['CaseTie:FLHead'])
        self.assertEqual(r['byte_identical_actors_from_prior'],71)
        self.assertEqual(len(r['completed_rest']),72);self.assertFalse(r['failures'])
        for tie in r['body_ties'].values():
            self.assertTrue(tie['selected_quantity_NOT_changed'])
            self.assertEqual(tie['band_nominal_thickness_mm'],1.2)
            self.assertEqual(tie['full_head_budget_mm'],[5,4.3,5.3])
            self.assertLessEqual(tie['nominal_rectangular_centreline_loop_mm'],tie['loop_budget_mm'])
            self.assertEqual(tie['loop_budget_mm'],100)
        p=r['planning'];self.assertTrue(any(a<p['chosen_centre_Z_mm']<b for a,b in p['free_centre_Z_mm']))
        self.assertEqual(p['nominal_head_band_fuse_solids'],1)
        self.assertTrue(p['actual_whole_head_outer']['ok'])
        self.assertFalse(r['N01_complete']);self.assertFalse(r['native_changed']);self.assertFalse(r['physical_pass'])

    def test_full_band_floor_changes_only_one_printed_actor(self):
        r=read('n01-MTA-full-band-slots.json');prior=read('n01-MTA-S1-complete-bypass.json')
        before={p['name']:p['sha256'] for p in prior['geometry']};after={p['name']:p['sha256'] for p in r['geometry']}
        self.assertEqual([n for n in before if before[n]!=after[n]],['LowerBay:ForePanel'])
        self.assertEqual(r['byte_identical_actors_from_prior'],63)
        p=r['inherited_rest_by_material_subset'];self.assertLess(p['new_material_outside_original_mm3'],1e-5)
        self.assertTrue(p['valid_single_solid']);self.assertEqual(p['connected_print_solids'],1)
        self.assertLess(max(p['print_envelope_mm']),250)
        self.assertEqual(len(r['named_interface_pairs']),4)
        for pair in r['named_interface_pairs'].values():
            self.assertGreaterEqual(pair['gap_mm'],.2-1e-6)
            self.assertLess(pair['whole_common_mm3'],1e-5)
            self.assertEqual(pair['foreign_margin_NOT_changed_mm'],1.25)
        self.assertEqual(len(r['completed_rest']),64);self.assertFalse(r['N01_complete']);self.assertFalse(r['native_changed'])

    def test_complete_module_and_derived_corridor(self):
        r=read('n01-MTA-S1-complete-bypass.json');p=r['planning']
        self.assertEqual(p['complete_module_count'],10)
        self.assertAlmostEqual(p['chosen_X_mm'],min(b[0][0] for b in p['complete_selected_S1_members'].values())-3.75)
        self.assertTrue(any(a<p['chosen_Y_mm']<b for a,b in p['vertical_free_domains_Y_mm']))
        self.assertTrue(p['full_new_wire_outer']['ok'])
        self.assertEqual(len(r['completed_rest']),64);self.assertFalse(r['failures'])
        self.assertEqual(r['changed_actors'],['CustomPrefix:W052'])
        self.assertFalse(r['N01_complete']);self.assertFalse(r['native_changed']);self.assertFalse(r['physical_pass'])

    def test_63_actual_geometry_identities(self):
        r=read('n01-MTA-S1-complete-bypass.json');prior=read('n01-MTA-rear-shoulders.json')
        before={p['name']:p['sha256'] for p in prior['geometry']};after={p['name']:p['sha256'] for p in r['geometry']}
        self.assertEqual(set(before),set(after))
        self.assertEqual([n for n in before if before[n]!=after[n]],['CustomPrefix:W052'])
        wire=r['recipes']['CustomPrefix:W052']
        self.assertEqual(wire['parts'][:3],prior['recipes']['CustomPrefix:W052']['parts'][:3])
        self.assertTrue(all(abs(p['radius_mm']-25.2)<1e-6 for p in wire['parts'] if p['kind']=='arc'))

    def test_exact_slots_preserve_original_negative_observation(self):
        r=read('n01-MTA-own-floor-slots.json');self.assertEqual(len(r['received_pairs']),4)
        for key,p in r['received_pairs'].items():
            self.assertEqual('|'.join(sorted(p['exact_own_head_slot_pair'])),key)
            self.assertGreaterEqual(p['gap_mm'],.2-1e-6);self.assertLess(p['whole_common_mm3'],1e-5)
            self.assertEqual(p['foreign_margin_NOT_changed_mm'],1.25)
        self.assertFalse(r['original_observations']['ArcGrip:W041:head|LowerBay:RearPanel']['ok'])
        snap=r['original_source_snapshot']
        raw=subprocess.run(['git','show',snap['commit']+':'+snap['pair_rows_path']],cwd=ROOT,check=True,stdout=subprocess.PIPE).stdout
        self.assertEqual(hashlib.sha256(raw).hexdigest(),snap['pair_rows_sha256'])
        old=json.loads(gzip.decompress(raw))
        self.assertEqual(old['ArcGrip:W041:head|LowerBay:RearPanel'],r['original_observations']['ArcGrip:W041:head|LowerBay:RearPanel'])
        self.assertFalse(r['N01_complete']);self.assertFalse(r['native_changed'])


if __name__=='__main__':unittest.main()
