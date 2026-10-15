import math,unittest
import FreeCAD as A
from antiparallel_axial_flex import build
from plan_current_main_sources import OUT,ROOT
from plan_continuous_joint_family import self_screen
from plan_axial_hip_sources import ends
from plan_current_mta_interfaces import line
from plan_current_rigid_factory_joins import moved_parts
import json,copy


class AxialReturnTests(unittest.TestCase):
    def test_independent_semicircle_fixture(self):
        radius=31.5
        parts=build([0,0,0],[0,63,0],[1,0,0],math.pi*radius,0,radius)
        self.assertEqual(len(parts),2)
        for point,wanted in zip(parts[0]['end'],[31.5,31.5,0]):self.assertAlmostEqual(point,wanted)
        for point,wanted in zip(parts[-1]['end'],[0,63,0]):self.assertAlmostEqual(point,wanted)
        self.assertIsNone(build([0,0,0],[0,62,0],[1,0,0],200))

    def test_real_rear_sources31poses_length_margin_and_self_clear(self):
        seed=json.loads((OUT/'body-axial-hip-plan.json').read_text())
        axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
        for original in seed['hips']:
            if not original['physical_leg'].startswith('Rear'):continue
            row=copy.deepcopy(original);row['fixed_anchor_world_mm']=[145,0,105]
            passed=None
            for length in range(150,251,5):
                good=True
                for h in range(-15,16):
                    _,end,exit,moving=ends(row,h)
                    start=[154,0,105]
                    for allowance in (-5,0,5):
                        q=build(start,end,[1,0,0],length+allowance)
                        if q is None:good=False;break
                        full=[line(row['fixed_anchor_world_mm'],start),*q,line(end,moving),
                              *moved_parts(row['source_parts'],row['source'],h,0,axes)]
                        if self_screen(full):good=False;break
                    if not good:break
                if good:passed=length;break
            self.assertIsNotNone(passed,original['loom'])


if __name__=='__main__':unittest.main()
