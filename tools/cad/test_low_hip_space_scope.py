"""Pose coupling and explicit partial-owner replacement must stay narrow."""
import unittest
import json
import math
from current_body_fanout_material import B
from check_low_hip_shared_space import same_leg_pose,load_candidate,P


class ScopeTest(unittest.TestCase):
    def test_independent_leg_and_static_material_remain(self):
        self.assertTrue(same_leg_pose(None,'FL',15))
        self.assertTrue(same_leg_pose(('RL',-15),'FL',15))
        self.assertTrue(same_leg_pose(('FL',15),'FL',15))
        self.assertFalse(same_leg_pose(('FL',-15),'FL',15))

    def test_prepared_subsets_and_eight_complete_ports(self):
        ports,mathplan,shapes,_=load_candidate()
        self.assertEqual(len(shapes),20)
        self.assertEqual(len(ports['retained']),4)
        self.assertEqual(len(ports['ports']),8)
        self.assertEqual(len(ports['removed_old_bands']),4)
        for row in ports['retained']:
            self.assertLess(row['outside_previous_mm3'],1e-5)
            self.assertGreater(shapes['Retained_'+row['owner']].Volume,1000)
        for row in ports['ports']:
            self.assertAlmostEqual(row['land']['length_mm'],9)
            self.assertEqual(row['recipe']['construction'],'single_post_axial_entry_below_band')
            self.assertEqual(row['recipe']['axial_entry_extension_mm'],2)
            self.assertLess(shapes[row['body']].common(shapes[row['band']]).Volume,1e-6)

    def test_all124_joins_preserve_actual_factory_endpoint(self):
        plan=json.loads((P.OUT/'body-low-hip-exit-plan.json').read_text())
        family=json.loads((P.OUT/'leg-source-near-member-plan.json').read_text())
        axes=json.loads((P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
        for row in plan['hips']:
            original=next(r for r in family['routes'] if r['loom']==row['loom'])
            for pose in row['poses']:
                factory=B.moved_parts(original['source_parts'],original['source'],pose['angle'],0,axes)
                self.assertLess(math.dist(pose['parts'][-1]['end'],factory[0]['start']),1e-6)

    def test_changed_length_not_hidden_as_extra_factory_stock(self):
        plan=json.loads((P.OUT/'body-low-hip-exit-plan.json').read_text())
        ledger=json.loads((P.OUT/'leg-extension-budget-plan.json').read_text())
        for row in plan['hips']:
            old=next(r for r in ledger['rows'] if r['loom']==row['loom'])
            added=row['guide_mm']-(row['previous_flex_length_mm']+18)
            self.assertAlmostEqual(added,148.4800842940392)
            self.assertGreater(old['remaining_after_guide_mm']-added,0)


if __name__=='__main__':unittest.main()
