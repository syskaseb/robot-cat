"""Negative observations stay negative; no prospective current-provider yet."""
import gzip,json,unittest
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT


def receipt(name):
    r=json.loads((OUT/name).read_text())
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    if 'pair_rows' in r:assert sha(ROOT/r['pair_rows'])==r['pair_rows_sha256']
    return r


class FactoryDiagnostics(unittest.TestCase):
    def test_whole_kit_domain_before_new_cad(self):
        r=receipt('n01-factory-rear-joint-bay-plan.json')
        self.assertEqual(len(r['full_rear_kit_members']),28)
        self.assertGreater(r['actual_clip_queries'],0)
        self.assertTrue(all(x['actual_clipped_solid_volume_mm3']>0 for x in r['projection_rows']))
        delta=r['chosen_whole_kit_shift_X_mm'];self.assertIsNotNone(delta)
        self.assertTrue(any(a<delta<b for a,b in r['shared_intervals_X_mm']))
        self.assertFalse(r['N01_complete']);self.assertFalse(r['native_changed'])

    def test_whole_nominal_lengths_include_strip_and_rework(self):
        r=receipt('n01-factory-saddles-received.json')
        for w,p in r['recipes'].items():
            self.assertEqual(p['R_mm'],25.2);self.assertEqual(p['radius_mm'],2.1)
            self.assertEqual(p['strip_mm'],11);self.assertEqual(p['rework_mm'],10)
            self.assertGreater(p['project_factory100_margin_mm'],0)
            a,b=p['root']['full9_arclength_interval_mm'];self.assertAlmostEqual(b-a,9)
            self.assertFalse(p['selected_parts_changed'])
        self.assertFalse(r['N01_complete']);self.assertFalse(r['physical_pass'])

    def test_full_motion_has_real_open_shoes(self):
        r=receipt('n01-factory-inputs-current-received.json')
        self.assertEqual(len(r['completed_motion']),41)
        self.assertEqual(len(r['failures']),8)
        self.assertTrue(all(k.startswith(('CaseBase:W044_Joint|motion:','CaseBase:W052_Joint|motion:')) for k in r['failures']))
        self.assertLess(r['structural_floor_removed_mm3'],1e-5)
        self.assertEqual(r['retained_root_output_combined_unit_solids'],1)
        self.assertFalse(r['N01_complete'])

    def test_profile_not_false_current_after_six_improvements(self):
        r=receipt('n01-factory-inputs-profile-received.json')
        self.assertEqual(r['status'],'FACTORY_SHOE_PROFILE_HOLDS')
        self.assertEqual(len(r['failures']),2)
        self.assertEqual(r['new_moving_pair_queries'],8)
        self.assertEqual(r['byte_identical_actor_count'],39)
        self.assertFalse(r['N01_complete']);self.assertFalse(r['native_changed'])
        for proof in r['shoe_profile_proofs'].values():
            self.assertLess(proof['new_material_outside_old_mm3'],1e-5)
            self.assertLess(proof['old_floor_root_lost_mm3'],1e-5)
            self.assertTrue(proof['entire_upper_boss_and_lower_R3p15_core_preserved'])


if __name__=='__main__':unittest.main()
