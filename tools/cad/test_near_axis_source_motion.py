import json,math,unittest
import FreeCAD as A
import numpy as np
from open_prototype_path_preflight import samples
from plan_near_axis_hip_sources import OUT,ROOT,endpoints,build
import current_body_fanout_material as M


class NearAxisSourceTests(unittest.TestCase):
    def test_both_complete_candidate_families_tangent_factory_and_margin(self):
        axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
        for filename in ('body-near-axis-hip-plan.json','body-same-side-near-axis-plan.json','body-underframe-near-axis-plan.json'):
            plan=json.loads((OUT/filename).read_text());count=0
            self.assertFalse(plan['rejected'])
            for row in plan['hips']:
                datum=row['source']['connector_reservation_world_mm'][row['source']['project_connector_choice']]
                axis=row['source']['cable_exit_world_axis']
                self.assertLess(math.dist(row['source_parts'][-1]['end'],[a+14*b for a,b in zip(datum,axis)]),1e-6)
                for pose in row['poses']:
                    factory=M.B.moved_parts(row['source_parts'],row['source'],pose['angle'],0,axes)
                    whole=pose['parts']+factory;edges=[M.P.wire([p]).Edges[0] for p in whole]
                    for a,b in zip(edges,edges[1:]):
                        self.assertLess(a.Vertexes[-1].Point.distanceToPoint(b.Vertexes[0].Point),1e-6)
                        self.assertGreater(a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter)),1-1e-6)
                    a,b,v,_=endpoints(row,pose['angle'])
                    if row.get('free_entry_parts'):a=row['free_entry_parts'][-1]['end']
                    length=row.get('spatial_length_mm',row['flex_length_mm'])
                    for delta in (-5,5):self.assertIsNotNone(build(a,b,v,length+delta,beta_degrees=row.get('bridge_beta_degrees',0)))
                    self.assertAlmostEqual(sum(p['length_mm'] for p in pose['parts']),row['guide_mm'],places=5)
                    count+=1
            self.assertEqual(count,124)

    def test_same_side_roots_inside_approved_torso_and_own_leg_side(self):
        plan=json.loads((OUT/'body-same-side-near-axis-plan.json').read_text())
        for row in plan['hips']:
            x,y,z=row['fixed_anchor_world_mm']
            self.assertTrue(-120<x<205 and abs(y)+4.4+5<=100 and -2<z<158)
            self.assertGreater(y*row['moving_anchor_rest_world_mm'][1],0)

    def test_underframe_uses_retained_body_layer_not_knee_corner(self):
        plan=json.loads((OUT/'body-underframe-near-axis-plan.json').read_text())
        family=json.loads((OUT/'leg-source-near-member-plan.json').read_text())
        for row in plan['hips']:
            original=next(r for r in family['hips'] if r['loom']==row['loom'])
            self.assertEqual(row['fixed_anchor_world_mm'][1:],original['fixed_anchor_world_mm'][1:])
            self.assertLessEqual(row['flex_length_mm'],165)

    def test_inboard_s_joint_rejection_is_preserved(self):
        plan=json.loads((OUT/'body-inboard-s-hip-plan.json').read_text())
        self.assertTrue(plan['status'].startswith('REJECTED'))
        self.assertTrue(plan['rejected'])
        self.assertFalse(plan['selected'] or plan['W5_complete'] or plan['physical_pass'])


if __name__=='__main__':unittest.main()
