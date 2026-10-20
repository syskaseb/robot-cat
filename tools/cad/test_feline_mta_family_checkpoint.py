"""Static acceptance must not hide sampled-motion failures or award N01."""
import gzip,json,unittest
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT


class FamilyCheckpoint(unittest.TestCase):
    def test_actual_nominal_channel_repair_keeps_foreign_hold(self):
        r=json.loads((OUT/'n01-MTA-rear-shoulders-scene.json').read_text())
        for p,h in r['source_sha256'].items():self.assertEqual(sha(ROOT/p),h,p)
        self.assertEqual(len(r['receiver_repairs']),1)
        repair=r['receiver_repairs'][0];before=repair['original_observed_row'];after=repair['current_row']
        self.assertFalse(before['ok']);self.assertTrue(after['ok'])
        self.assertEqual(before['gap_mm'],after['gap_mm'])
        self.assertEqual(after['gap_mm'],after['existing_actual_own_shoe_channel_mm'])
        self.assertEqual(after['ordinary_foreign_margin_unchanged_mm'],1.25)
        self.assertEqual(set(r['completed_static']),{'CustomPrefix:W041','CustomPrefix:W042','CustomPrefix:W044'})
        self.assertEqual(r['failures'],['CustomPrefix:W052|Ref_Material_current_S1_ring_2_0_0'])
        self.assertFalse(r['N01_complete']);self.assertFalse(r['native_changed'])

    def test_rear_shoulder_reuse_and_all_rest_received(self):
        r=json.loads((OUT/'n01-MTA-rear-shoulders.json').read_text())
        for p,h in r['source_sha256'].items():self.assertEqual(sha(ROOT/p),h,p)
        self.assertEqual(r['status'],'REAR_SHOULDER64_REST_RECEIVED_STATIC_MOTION_ACCESS_OPEN')
        self.assertEqual(r['byte_identical_actors_from_prior'],63)
        self.assertEqual(len(r['completed_rest']),64);self.assertFalse(r['failures'])
        self.assertFalse(r['N01_complete']);self.assertFalse(r['native_changed'])
        for n,recipe in r['recipes'].items():
            self.assertEqual(recipe['parts'][0]['start'],recipe['point_mm'])
            self.assertEqual(recipe['parts'][-1]['end'],recipe['routing_exit_mm'])
            self.assertTrue(all(abs(p['radius_mm']-25.2)<1e-6 for p in recipe['parts'] if p['kind']=='arc'))
        self.assertAlmostEqual(r['recipes']['CustomPrefix:W044']['routing_exit_mm'][0],-127.75)
        self.assertAlmostEqual(r['recipes']['CustomPrefix:W052']['routing_exit_mm'][0],-127.75)

    def test_whole_scene_stops_at_first_static_cause(self):
        r=json.loads((OUT/'n01-MTA-whole-scene.json').read_text())
        for p,h in r['source_sha256'].items():self.assertEqual(sha(ROOT/p),h,p)
        self.assertEqual(r['status'],'WHOLE_MTA_SCENE_STATIC_HOLD')
        self.assertEqual(r['inherited_rest_actor_count'],64)
        self.assertEqual(len(r['failures']),1);self.assertEqual(r['checks'],6)
        self.assertEqual(r['completed_motion'],[]);self.assertFalse(r['N01_complete'])

    def test_complete_kit_rest_does_not_award_whole_scene(self):
        r=json.loads((OUT/'n01-MTA-whole-corridor.json').read_text())
        for p,h in r['source_sha256'].items():self.assertEqual(sha(ROOT/p),h,p)
        self.assertEqual(r['status'],'COMPLETE_MTA_KIT_REST_RECEIVED_STATIC_MOTION_ACCESS_OPEN')
        self.assertEqual(len(r['geometry']),64);self.assertEqual(len(r['completed_rest']),64)
        self.assertFalse(r['failures']);self.assertFalse(r['N01_complete'])
        self.assertEqual(len(r['positive_roots']),4);self.assertEqual(len(r['print_groups']),2)
        for root in r['positive_roots'].values():
            self.assertGreater(root['parent_actual_overlap_mm3'],0)
            self.assertEqual(root['full_grip_arclength_mm'],[1.25,11.25])
        for recipe in r['factory_recipes'].values():
            self.assertGreater(recipe['project_factory100_margin_mm'],0)
            self.assertEqual(recipe['strip_mm'],11);self.assertEqual(recipe['rework_mm'],10)
        self.assertEqual(r['completed_static'],[]);self.assertEqual(r['completed_motion'],[])

    def test_static_does_not_qualify_motion(self):
        r=json.loads((OUT/'n01-MTA-four-fans-received.json').read_text())
        for p,h in r['source_sha256'].items():self.assertEqual(sha(ROOT/p),h,p)
        self.assertEqual(sha(ROOT/r['pair_rows']),r['pair_rows_sha256'])
        rows=json.loads(gzip.decompress((ROOT/r['pair_rows']).read_bytes()))
        static={k:v for k,v in rows.items() if '|motion:' not in k}
        self.assertEqual(len(static),129);self.assertTrue(all(v['ok'] for v in static.values()))
        self.assertEqual(len(r['inherited_own_grip_pairs']),2)
        for row in r['inherited_own_grip_pairs'].values():
            self.assertTrue(row['old_gap_NOT_inherited'])
            self.assertAlmostEqual(row['actual_current_gap_mm'],1.2)
            self.assertAlmostEqual(row['original_own_grip_gap_mm'],1.45)
            self.assertLess(row['actual_current_common_mm3'],1e-5)
            self.assertEqual(row['foreign_margin_unchanged_mm'],1.25)
        self.assertGreater(len(r['failures']),0)
        self.assertTrue(all('|motion:' in k for k in r['failures']))
        self.assertFalse(r['N01_complete']);self.assertFalse(r['native_changed'])
        self.assertTrue(r['whole_custom_grips_roots_moved_case_kits_tools_and_common123_still_OPEN'])


if __name__=='__main__':unittest.main()
