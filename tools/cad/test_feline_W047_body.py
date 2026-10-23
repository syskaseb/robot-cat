"""Whole fixed body evidence is not a whole factory loom or N01 award."""
import json
import unittest
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_tangent_routes import length,min_radius
from solve_feline_W047_simple_graph import self_conflict


class W047Body(unittest.TestCase):
    def test_received_geometry_and_scope(self):
        p=json.loads((OUT/'n01-current-W047-complete-body-plan.json').read_text())
        recipe=p['middle_recipe'];parts=recipe['parts']
        self.assertAlmostEqual(length(parts),p['middle_length_mm'],places=6)
        self.assertGreaterEqual(min_radius(parts),12.4)
        self.assertGreaterEqual(self_conflict(parts,[None]*len(parts))[0],.2)
        self.assertEqual([r['id'] for r in p['current_boundaries']],['W047/body/start','W047/body/end'])
        self.assertTrue(all(r['ok'] for r in p['checks'].values()))
        self.assertEqual(p['sampled_poses'],36)
        self.assertEqual(p['motion_actors_covered'],3888)
        self.assertTrue(p['whole900_moving_side_stock_supports_and_complete123_OPEN'])
        self.assertFalse(p['N01_complete'])
        self.assertFalse(p['physical_pass'])
        self.assertEqual(sha(ROOT/p['bundle']),p['bundle_sha256'])
        for path,h in p['source_sha256'].items():self.assertEqual(sha(ROOT/path),h,path)


if __name__=='__main__':unittest.main()
