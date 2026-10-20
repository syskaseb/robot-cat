import json,unittest
import FreeCAD
from plan_feline_layout import OUT
from feline_mta_curved_grips import construct


class CurvedGripConstruction(unittest.TestCase):
    def test_all_four_complete_grips_before_scene(self):
        r=json.loads((OUT/'n01-MTA-tilted-fans.json').read_text())
        self.assertEqual(len(r['recipes']),4)
        for recipe in r['recipes'].values():
            kit,proof=construct(recipe)
            self.assertEqual(set(kit),{'pad','band','head'})
            self.assertEqual(proof['full_grip_arclength_mm'],[1.25,11.25])
            self.assertGreater(proof['root_pad_common_mm3'],0)
            self.assertEqual(proof['wire_length_added_mm'],0)
            self.assertTrue(proof['root_parent_and_full_scene_and_pull_test_OPEN'])


if __name__=='__main__':unittest.main()
