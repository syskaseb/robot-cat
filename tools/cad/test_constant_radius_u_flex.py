"""Exact lengths/joins/radii, including every currently planned Hip1 pose."""
import json
import math
import unittest
import FreeCAD as A
import Part
from constant_radius_u_flex import build,minimum
from plan_body_fanout_layout import OUT
from current_body_fanout_material import P


def end_tangent(part,at_end):
    edge=P.wire([part]).Edges[0]
    forward=(edge.valueAt(edge.FirstParameter)-A.Vector(*part['start'])).Length<1e-7
    parameter=edge.LastParameter if at_end==forward else edge.FirstParameter
    v=edge.tangentAt(parameter)
    return v if forward else -v


class RoundFlexTest(unittest.TestCase):
    def test_too_short_is_not_faked(self):
        start=[0,0,0];end=[100,0,-10];axis=[0,0,1]
        low=minimum(start,end,axis)
        self.assertIsNone(build(start,end,axis,low['length_mm']-1))

    def test_all124_received_poses_are_continuous_exact_lengths(self):
        plan=json.loads((OUT/'body-low-hip-exit-plan.json').read_text())
        self.assertFalse(plan['errors'])
        count=0;low=float('inf');high=-float('inf')
        for row in plan['hips']:
            self.assertEqual(row['fixed_anchor_world_mm'][::2],row['previous_fixed_anchor_world_mm'][::2])
            self.assertAlmostEqual(abs(row['fixed_anchor_world_mm'][1]),45.5)
            self.assertEqual(len(row['fixed_lands']),2)
            self.assertEqual(len(row['poses']),31)
            for pose in row['poses']:
                count+=1;parts=pose['parts'];wire=P.wire(parts)
                self.assertTrue(wire.isValid())
                self.assertAlmostEqual(wire.Length,row['guide_mm'],places=6)
                low=min(low,wire.BoundBox.ZMin);high=max(high,wire.BoundBox.ZMax)
                for part in parts:
                    if part['kind']=='arc':
                        self.assertAlmostEqual(P.wire([part]).Edges[0].Curve.Radius,31.5,places=6)
                for a,b in zip(parts,parts[1:]):
                    self.assertLess(math.dist(a['end'],b['start']),1e-7)
                    self.assertGreater(end_tangent(a,True).dot(end_tangent(b,False)),1-1e-7)
        self.assertEqual(count,124)
        print('received exact U math',count,'common guide',plan['hips'][0]['guide_mm'],'Zbounds',low,high)


if __name__=='__main__':unittest.main()
