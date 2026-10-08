"""Small pure contract checks; no repeated CAD collision worker."""
import unittest
import open_prototype_local_boundaries as B


class LocalBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=B.build()

    def test_all_nine_local_wires_kept(self):
        self.assertEqual({r['wire'] for r in self.plan['rows']},
            {'XB12','XB13','XS13','XB22','XB23','XS23','XB32','XB33','XS33'})
        self.assertEqual(len(self.plan['rows']),9)

    def test_body_identity_and_corridor_preserved(self):
        old=B.read(B.SOURCES['endpoints'])['body_conductors']
        identity=lambda rows:{(r['id'],r['a'],r['b'],r['net']) for r in rows}
        self.assertEqual(identity(old),identity(self.plan['body_rows']))
        self.assertEqual(len(self.plan['body_rows']),80)
        self.assertTrue(all(r['corridor'] for r in self.plan['body_rows']))

    def test_hp_output_not_stale(self):
        hp=next(r for r in self.plan['rows'] if r['wire']=='XB22')
        self.assertEqual(hp['body_source_mm'],[68,-31.25,99.99])

    def test_shift_is_applied_once(self):
        yaw=next(r for r in self.plan['rows'] if r['wire']=='XB12')
        self.assertEqual(yaw['local_boundary_current_candidate_mm'],[-112,-56.8,85.2])
        tail=next(r for r in self.plan['rows'] if r['wire']=='XB32')
        self.assertEqual(tail['shift_mm'],[0,0,15])

    def test_missing_fixed_support_and_tail_replacement_not_waived(self):
        for r in self.plan['rows']:
            if r['wire'] in ('XB22','XB23','XS23','XB32','XB33','XS33'):
                self.assertFalse(r['known_current_attachment'])
            self.assertFalse(r['terminal_pin_invented'])
            self.assertFalse(r['route_qualified'])
            self.assertIsNone(r['actual_cut_mm'])

    def test_motor_return_not_pwm_ground(self):
        rows={r['wire']:r for r in self.plan['rows']}
        self.assertEqual(rows['XB13']['body_role'],'G_AUX.3')
        self.assertEqual(rows['XB23']['body_role'],'G_AUX.4')
        self.assertEqual(rows['XB33']['body_role'],'G_TAIL.2')
        self.assertTrue(all(rows[w]['material']=='HELU23301 black' for w in ('XB13','XB23','XB33')))

    def test_signal_role_matches_netlist_not_old_drawing_alias(self):
        rows={r['wire']:r for r in self.plan['rows']}
        for i,wire in enumerate(('XS13','XS23','XS33'),1):
            self.assertEqual(rows[wire]['body_role'],f'R{i}.2')
        self.assertTrue(all(not e['manufacturer_pin_known'] for r in self.plan['body_rows'] for e in r['ends']))

    def test_legacy_and_unknown_pads_stay_open(self):
        self.assertTrue(self.plan['legacy_source'])
        self.assertIsNone(self.plan['remaining_output_AUX']['target_pin_mm'])
        self.assertTrue(self.plan['remaining_output_AUX']['delivered_padmap_required'])
        self.assertFalse(self.plan['stage_completed'])
        self.assertFalse(self.plan['physical_pass'])
        self.assertEqual(self.plan['connectors_added'],0)


if __name__=='__main__':unittest.main()
