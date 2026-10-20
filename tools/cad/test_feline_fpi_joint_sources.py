"""Scoped static receipt cannot silently become N01 or full wiring."""
import json,unittest
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_fpi_joint_sources import construct


class FPIJointSources(unittest.TestCase):
    def test_full_four_lands_nominal_selected_roles(self):
        actors,meta,lands,pins=construct(True)
        self.assertEqual(len(actors),14)
        self.assertEqual(len(lands),4)
        for r in lands.values():
            self.assertEqual(r['full9_arclength_mm'][1]-r['full9_arclength_mm'][0],9.)
            self.assertEqual(r['extra_wire_mm'],0)
            self.assertIn(r['radius_mm'],(1.05,2.))
        self.assertEqual(lands['F_PI.out']['source_part_index'],1)

    def test_whole_static_and_explicit_missing_scopes(self):
        r=json.loads((OUT/'n01-FPI-four-source-curved-output.json').read_text())
        self.assertEqual(r['status'],'FPI_FOUR_GRIPS_CURRENT_STATIC_RECEIVED_ROOTS_MOTION_TOOLS_OPEN')
        self.assertEqual(len(r['completed_static']),12)
        self.assertFalse(r['failures']);self.assertFalse(r['N01_complete'])
        self.assertTrue(r['roots_case_retention_tools_and_motion_OPEN'])
        self.assertEqual(r['unchanged_pairs_reused'],37)
        self.assertEqual(sha(ROOT/r['bundle']),r['bundle_sha256'])
        self.assertEqual(sha(ROOT/r['pair_rows']),r['pair_rows_sha256'])

    def test_service_budget_holds_are_not_hidden(self):
        r=json.loads((OUT/'n01-FPI-side-central-cap-access.json').read_text())
        self.assertEqual(r['status'],'FPI_SIDE_CENTRAL_CAP_SERVICE_SPACE_HOLD')
        self.assertEqual(sum(not v['ok'] for v in r['checks'].values()),2)
        self.assertFalse(r['N01_complete'])


if __name__=='__main__':unittest.main()
