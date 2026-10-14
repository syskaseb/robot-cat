import json
import unittest
import FreeCAD as A
from check_rail_support_correction import coexist,P
from plan_rail_support_correction import orthogonal


class CorrectionScopeTests(unittest.TestCase):
    def test_upstream_joint_coupling(self):
        self.assertTrue(coexist(None,('FR','Knee',15,15)))
        self.assertTrue(coexist(('FL','Knee',-15,-15),('FR','Knee',15,15)))
        self.assertTrue(coexist(('FR','Hip',15,0),('FR','Knee',15,-15)))
        self.assertFalse(coexist(('FR','Hip',0,0),('FR','Knee',15,0)))
        self.assertFalse(coexist(('FR','Knee',15,0),('FR','Knee',15,15)))
        self.assertTrue(coexist(('FR','Knee',15,15),('FR','Ankle',15,15)))

    def test_new_plan_keeps_fixed_count_and_orthogonal_full_paths(self):
        plan=json.loads((P.OUT/'body-rail-support-correction-plan.json').read_text())
        self.assertFalse(plan['contacts']);self.assertEqual(plan['checks'],90)
        self.assertEqual(len(plan['changed_support_owners']),5)
        self.assertGreater(plan['joint_knee_allocation']['joint_choices'],0)
        for row in plan['changed_ports']:
            points=row['points']
            self.assertLess(A.Vector(*points[-1]).distanceToPoint(A.Vector(*row['arrival'])),1e-6)
            for a,b in zip(points,points[1:]):self.assertLessEqual(sum(abs(x-y)>1e-7 for x,y in zip(a,b)),1)
        for row in plan['joint_knee_allocation']['selected']:self.assertGreaterEqual(row['minimum_RR_gap_mm'],3.25)

    def test_orthogonal_helper_never_makes_diagonal_arm_box(self):
        for order in ((0,1,2),(2,1,0),(1,0,2)):
            points=orthogonal([1,2,3],[9,-8,7],order)
            self.assertEqual(points[-1],[9,-8,7])
            self.assertEqual(len(points),4)


if __name__=='__main__':unittest.main()
