"""Prevent repeating locally clear but physically too-short JPWM hypotheses."""
import copy,json,unittest
from plan_feline_layout import OUT
from plan_feline_jpwm_pair_exit import factory_gate,construct


def fixture():
    p=json.loads((OUT/'n01-JPWM-four-factory-length-necessity.json').read_text())
    ends=[]
    for r in p['pieces']:
        ends.extend([dict(id=r['jpwm_end_id'],portion_id=r['wire']+'/extra',wire=r['wire'],
                         group='JPWM',routing_exit_mm=r['jpwm_routing_boundary_mm'],point_mm=None),
                     dict(id=r['other_end_id'],portion_id=r['wire']+'/extra',wire=r['wire'],
                         group='receiver',routing_exit_mm=r['other_routing_boundary_mm'],point_mm=None)])
    return ends


class WholeFactoryGate(unittest.TestCase):
    def test_reject_current_pose_before_any_grip_geometry(self):
        ends=fixture();before=copy.deepcopy(ends);gate=factory_gate(ends)
        self.assertEqual([r['wire'] for r in gate['hard_holds']],['XP02.source'])
        self.assertGreater(gate['hard_holds'][0]['straight_boundary_lower_bound_mm'],266.)
        with self.assertRaisesRegex(ValueError,'Relocate whole JPWM'):construct(ends)
        self.assertEqual(ends,before)

    def test_require_both_physical_ends(self):
        with self.assertRaisesRegex(AssertionError,'BOTH ends'):factory_gate(fixture()[:-1])

    def test_positive_bound_is_not_route_or_N01(self):
        ends=fixture()
        for r in ends:
            if r['group']=='JPWM':r['routing_exit_mm']=[x+d for x,d in zip(r['routing_exit_mm'],[140,98.8,-23.4390475583])]
        gate=factory_gate(ends)
        self.assertFalse(gate['hard_holds']);self.assertFalse(gate['N01_complete'])
        self.assertTrue(gate['necessary_bound_only_NOT_route_approval'])


if __name__=='__main__':unittest.main()
