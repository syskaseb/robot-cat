import json
from pathlib import Path
import unittest
from w5_leg_fanout_layout import changed_plan
from w5_rounded_path import corner_offsets

ROOT = Path(__file__).resolve().parents[2]


class CoupledLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = json.loads((ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r3/intent.json').read_text(encoding='utf-8'))['routes']
        cls.new = changed_plan(cls.old)

    def test_whole_conservation_and_unchanged_v(self):
        for before,after in zip(self.old,self.new):
            for key in ('wire','loom','servo_end','body_end','termination'):
                self.assertEqual(before[key],after[key])
            if before['role'] == 'V':self.assertEqual(before,after)

    def test_exact_r10_corner_consumption_for_all_changed_paths(self):
        for row in self.new:
            if row['role'] != 'V':corner_offsets(row['waypoints_mm'],10)

    def test_ground_blocks_are_not_on_top_of_data_blocks(self):
        for row in self.new:
            if row['role'] == 'G':
                self.assertEqual(abs(row['waypoints_mm'][0][1]),71.5)
                self.assertEqual(row['body_entry_tangent'][1],1 if row['loom'][1]=='L' else -1)
                self.assertGreater(row['waypoints_mm'][2][2],133.5)

    def test_rear_level_order_matches_physical_cages(self):
        for leg in ('RL','RR'):
            for role in ('D','G'):
                rows=sorted((r for r in self.new if r['loom'][:2]==leg and r['role']==role),key=lambda r:r['waypoints_mm'][0][0])
                levels=[r['waypoints_mm'][2][2] for r in rows]
                self.assertEqual(levels,sorted(levels,reverse=True))


if __name__ == '__main__':unittest.main()
