"""Constructive whole-family evidence is not a whole-N01 or physical PASS."""
import gzip,hashlib,json,subprocess,unittest
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT


def read(name):
    r=json.loads((OUT/name).read_text())
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    return r


class BypassContract(unittest.TestCase):
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
