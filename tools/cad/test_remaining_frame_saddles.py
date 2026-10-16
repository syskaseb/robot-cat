import json,unittest
from build_remaining_frame_saddles import native_recipe,OUT
from check_main_p0_placement import SavedShapes


class FrameSaddleTests(unittest.TestCase):
    def test_native_adapter_changes_no_bounds_or_frozen_recipe(self):
        p=json.loads((OUT/'remaining25-saddle-roots.json').read_text())
        rows=[r for r in p['groups'] if r['owner'].endswith('FixedCarrier')]
        self.assertEqual(len(rows),30)
        for r in rows:
            old=json.dumps(r['recipe'],sort_keys=True);new=native_recipe(r['recipe'])
            self.assertEqual([q['bounds_mm'] for q in new['pads']],r['recipe']['pads'])
            self.assertEqual(json.dumps(r['recipe'],sort_keys=True),old)

    def test_source_copy_has_all_four_actual_native_parent_histories(self):
        p=json.loads((OUT/'current-body-source-native-set.json').read_text())
        names=SavedShapes().doc(OUT/'local-source-retention-native/FramesSourceRetentionCurrent.FCStd')
        owners=[r for r in p['prints'] if r['part'].endswith('FixedCarrier')]
        self.assertEqual(len(owners),4)
        for r in owners:self.assertIn(r['native_object'],names)


if __name__=='__main__':unittest.main()
