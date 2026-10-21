import unittest
import numpy as np
from plan_feline_u1_e2_zone import factory_rank,independent_case_rank,common_three_output_fan


class WholeZoneRank(unittest.TestCase):
    def test_common_fan_preserves_pad_axes_full_kits_and_stand_bore(self):
        import FreeCAD as A
        import Part
        from feline_source_saddles import segment
        pcb=Part.makeBox(43.18,50.8,1.6002,A.Vector(-10,-23.4,-25.03))
        stand=Part.makeCylinder(2.4,6.5,A.Vector(-6.19,2,-31.53)).cut(
            Part.makeCylinder(1.2,6.7,A.Vector(-6.19,2,-31.63)))
        fixed={'Ref_Material_PWM1608NominalPCB_0_0':pcb,'U1Relief:Stand0':stand}
        specs={}
        for w,x in zip(('XS13','XS23','XS33'),(1.43,3.97,6.51)):
            specs[w+'/extra/start']=dict(parts=[dict(start=[x,16.97,-28.25])],
                bare_parts=[dict(end=[x,15.97,-21.9298])],bare_radius_mm=.3989422804014327,
                selected_carrier_pad_identity=w+'.test',pad_world_mm=[x,15.97,-23.4298])
        actors,plan=common_three_output_fan(fixed,specs)
        self.assertEqual(len(actors),13)
        self.assertFalse(plan['N01_complete'])
        self.assertGreater(plan['Stand0_positive_joint_mm3'],0)
        self.assertGreater(plan['parallel_gallery_until_old_world_Y_mm'],pcb.BoundBox.YMax)
        for w,row in plan['routes'].items():
            self.assertEqual(row['named_pad'],w+'.test')
            self.assertAlmostEqual(np.linalg.norm(np.subtract(*row['full9_mm'])),9.)
            self.assertAlmostEqual(actors['U1Relief:'+w+':head'].Volume,5*4.3*5.3)
            self.assertTrue(all(r.get('radius_mm',12.6)>=12.6-1e-6 for r in row['parts']))
            a=segment(row['parts'][0]).valueAt(0)
            b=segment(row['bare_parts'][0]).valueAt(0)
            self.assertLess((a-b).Length,1e-6)
        root=actors['U1Relief:ForeRoot']
        self.assertEqual(len(root.fuse(stand).Solids),1)
        hole=Part.makeCylinder(1.2,30,A.Vector(-6.19,2,-45))
        self.assertLess(root.common(hole).Volume,1e-5)

    def test_independent_E2_choice_counts_all_four_necessary_budgets(self):
        cases=[dict(low_mm=[10,0,0],high_mm=[11,1,1],fixed_source_necessary_mm=210,
                    module_caps={w:[10,0,0] for w in ('XP02.module','XP03.module')}),
               dict(low_mm=[90,0,0],high_mm=[91,1,1],fixed_source_necessary_mm=150,
                    module_caps={w:[90,0,0] for w in ('XP02.module','XP03.module')})]
        score,chosen=independent_case_rank(np.eye(3),np.zeros((1,3)),
            [[0,0,0],[1,1,1]],{w:[0,0,0] for w in ('XP02.module','XP03.module')},
            cases,return_ids=True)
        self.assertEqual(chosen[0],1)
        self.assertAlmostEqual(score[0],150.)

    def test_two_fixed_sources_both_count_prefix_debit(self):
        ids = np.arange(41**3).reshape((41,41,41))
        costs = {'XP02.source':np.full(6*ids.size,10.),
                 'XP03.source':np.full(6*ids.size,20.)}
        caps = {w:[0.,0.,0.] for w in costs}
        score = factory_rank(np.eye(3),np.array([[20.,20.,20.]]),caps,
                             ids,np.zeros(3),costs,
                             {'XP02.source':30.,'XP03.source':40.})
        self.assertAlmostEqual(score[0],68.)

    def test_no_reachable_goal_does_not_become_zero_length(self):
        ids = np.full((41,41,41),-1)
        costs = {w:np.ones(6) for w in ('XP02.source','XP03.source')}
        score = factory_rank(np.eye(3),np.array([[20.,20.,20.]]),
                             {w:[0.,0.,0.] for w in costs},ids,np.zeros(3),
                             costs,{w:30. for w in costs})
        self.assertTrue(np.isinf(score[0]))


if __name__=='__main__':unittest.main()
