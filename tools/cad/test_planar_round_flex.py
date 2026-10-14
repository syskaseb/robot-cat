import json
import math
import unittest
from plan_body_fanout_layout import OUT
from plan_continuous_joint_family import self_screen
from plan_low_hip_rail_exit import ends
from plan_current_moving_looms import norm,sub


class RailFlexTests(unittest.TestCase):
    def test_all_124_nominal_poses_and_endpoints(self):
        plan=json.loads((OUT/'body-low-hip-rail-exit-plan.json').read_text())
        self.assertEqual(len(plan['hips']),4)
        self.assertEqual(plan['chosen_common_flex_mm'],155)
        self.assertEqual(plan['additional_fixed_bands'],0)
        count=0
        for row in plan['hips']:
            self.assertEqual(row['fixed_anchor_world_mm'][2],-20)
            self.assertEqual(row['guide_mm'],173)
            for pose in row['poses']:
                parts=pose['parts'];a,b,v,moving=ends(row,pose['angle'])
                self.assertLess(norm(sub(parts[0]['start'],row['fixed_anchor_world_mm'])),1e-7)
                self.assertLess(norm(sub(parts[-1]['end'],moving)),1e-7)
                self.assertAlmostEqual(sum(p['length_mm'] for p in parts),173,places=6)
                for left,right in zip(parts,parts[1:]):
                    self.assertLess(norm(sub(left['end'],right['start'])),1e-6)
                self.assertIsNone(self_screen(parts),(row['loom'],pose['angle']))
                count+=1
        self.assertEqual(count,124)


if __name__=='__main__':unittest.main()
