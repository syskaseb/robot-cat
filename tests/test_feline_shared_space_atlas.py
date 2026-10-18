import json
import sys
import unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class SharedAtlas(unittest.TestCase):
    def test_complete36_pose_accounting_and_no_duplicate_keys(self):
        p=json.loads((OUT/'n01-shared-space-atlas-received.json').read_text())
        keys=[r['key'] for r in p['parts']];self.assertEqual(len(keys),len(set(keys)))
        groups={}
        for r in p['parts']:
            if r['category']=='motion36':groups.setdefault(r['source'],set()).add(r['pose_index'])
        self.assertEqual(len(groups),108)
        self.assertTrue(all(v==set(range(36)) for v in groups.values()))

    def test_named_planning_beams_only_not_MAIN_channel(self):
        p=json.loads((OUT/'n01-reservation-ownership-plan.json').read_text())
        names=[r['name'] for r in p['reallocated_provisional_beams']]
        self.assertEqual(len(names),5)
        self.assertNotIn('StructureReserve:UpperStrip-1',names)
        self.assertTrue(p['all_actual_materials_unchanged'])
        for r in p['reallocated_provisional_beams']:
            self.assertEqual(r['source_record']['origin'],'backbone_R4_rectangular_recipe_only')

    def test_conservative_mask_and_service_not_a_PASS(self):
        p=json.loads((OUT/'n01-reservation-ownership-plan.json').read_text())
        a=np.load(ROOT/p['field'],allow_pickle=False)
        self.assertFalse(np.any(a['conservative']&~a['nominal']))
        self.assertFalse(np.any(a['nominal']&a['service']))
        self.assertFalse(p['selected']);self.assertFalse(p['N01_complete']);self.assertFalse(p['physical_pass'])

    def test_guide_is_non_retracing_but_not_radius_accepted(self):
        p=json.loads((OUT/'n01-joint-frame-corridor-guide.json').read_text())
        self.assertTrue(p['guides'])
        for g in p['guides']:
            q=[tuple(v) for v in g['all_grid_points_mm']]
            self.assertEqual(len(q),len(set(q)))
            self.assertTrue(g['not_a_selected_or_radius_qualified_cable'])


if __name__=='__main__':unittest.main()
