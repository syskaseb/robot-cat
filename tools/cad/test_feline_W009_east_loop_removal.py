import json
import unittest
import FreeCAD
from plan_feline_layout import OUT
from plan_feline_W009_east_loop_removal import recipe
from receive_feline_rrp_shared_height import load
import feline_tangent_routes as ft


class EastLoopRemoval(unittest.TestCase):
    def test_recipe_continuous_and_radius(self):
        r = recipe()
        self.assertGreaterEqual(ft.min_radius(r['parts']), 12.4)
        self.assertAlmostEqual(r['length_mm'], 568.0302307341602)
        for a, b in zip(r['parts'], r['parts'][1:]):
            self.assertLess(ft.norm(ft.sub(a['end'], b['start'])), 1e-6)
            ta = a.get('end_tangent', ft.unit(ft.sub(a['end'], a['start'])))
            tb = b.get('tangent', ft.unit(ft.sub(b['end'], b['start'])))
            self.assertLess(ft.norm(ft.sub(ta, tb)), 1e-6)

    def test_saved_partial_receipt_reopens_without_awarding_N01(self):
        p = OUT/'W009-W069-harness-corridor/W009-east-loop-removed.json'
        packet = json.loads(p.read_text())
        actors = load(packet)
        self.assertEqual(set(actors), {'CurrentMiddle:W009'})
        self.assertTrue(actors['CurrentMiddle:W009'].isValid())
        self.assertEqual(len(actors['CurrentMiddle:W009'].Solids), 1)
        self.assertTrue(all(r['ok'] for r in packet['checks'].values()))
        self.assertFalse(packet['whole_scene_received'])
        self.assertFalse(packet['N01_complete'])
        self.assertEqual(len(packet['unrecovered']), 276)


if __name__ == '__main__':
    unittest.main()
