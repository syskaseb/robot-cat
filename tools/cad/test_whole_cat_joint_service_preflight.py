import json
import math
import unittest
from whole_cat_joint_service_preflight import BASE, classify_contact, reconcile, transform_endpoint


class DependencyPreflight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gate = json.loads((BASE/'joint-service-layout.json').read_text(encoding='utf-8'))
        cls.graph = json.loads((BASE/'whole-harness-board-plan.json').read_text(encoding='utf-8'))
        data = json.loads((BASE/'service-zone-inventory.json').read_text(encoding='utf-8'))
        cls.inventory = {r['name']: r for r in data['components']}
        cls.result = reconcile(cls.gate, cls.graph, cls.inventory)

    def test_all_eight_mta_mates_invalidated_and_inputs_not_duplicated(self):
        self.assertEqual(len(self.result['invalidated_native_joints']), 8)
        self.assertEqual({r['id'] for r in self.result['MTA_input_topology']},
                         {'W041', 'W042', 'W044', 'W052'})
        self.assertFalse(self.result['selected'])
        self.assertFalse(self.result['W5_complete'])

    def test_rigid_aux_cell_preserves_short_input(self):
        row = next(r for r in self.graph['branch_input_length_gate'] if r['holder']=='F_AUX')
        ends = [dict(role='test', native=n, point_mm=p, departure=[1,0,0])
                for n,p in [('F_AUX_CP2',row['factory_exit_mm']),
                            ('P_REAR_CP2',row['target_mm'])]]
        moved = [transform_endpoint(e,self.gate['recipe'],self.inventory) for e in ends]
        self.assertAlmostEqual(math.dist(*[r['proposed_point_mm'] for r in moved]),15)
        self.assertEqual(row['actual_current_nominal_input_blank_mm'],29)
        self.assertIsNone(transform_endpoint(dict(role='F_PI.in',native='F_PI_CP2',
            point_mm=[-24,41.25,104]),self.gate['recipe'],self.inventory))

    def test_rotation_propagates_direction_not_only_position(self):
        row = transform_endpoint(dict(role='F_TY.in',native='F_TY_CP2',
            point_mm=[-2.5,-87,90],departure=[-1,0,0]),self.gate['recipe'],self.inventory)
        self.assertAlmostEqual(row['proposed_point_mm'][0],-74.5)
        self.assertAlmostEqual(row['proposed_departure'][0],1)

    def test_contact_classes_do_not_turn_negative_layout_into_clearance(self):
        stale = self.result['invalidated_native_joints']
        self.assertEqual(classify_contact(['P_REAR_CP2','XA01_SHORT_STRIP_CP2'],stale),
                         'DESIGNED_INSERTION_NOT_OBSTRUCTION')
        self.assertTrue(classify_contact(['MTA_FL_CP2','Joint_RL_SOURCE'],stale).startswith('STALE'))
        self.assertEqual(len(self.result['outside']),2)
        self.assertFalse(self.result['physical_pass'])


if __name__=='__main__':
    unittest.main()
