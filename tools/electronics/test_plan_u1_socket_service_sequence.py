import unittest
import plan_u1_socket_service_sequence as S


class ServiceSequenceTests(unittest.TestCase):
    def receipt(self):return dict(errors=[],contacts=[dict(a='Bar',b='W003')],
        reservation_resolutions=[dict(a='Cap',b='W003')],service_lift_mm=12,pairs=372)

    def test_conditional_not_free_cable_removal(self):
        p=S.derive(self.receipt())
        self.assertFalse(p['E1_complete']);self.assertFalse(p['selected'])
        self.assertFalse(p['no_external_wire_disconnects_required_for_adapter'])
        self.assertEqual(p['loose_cable_interfaces'],3)
        self.assertEqual(p['new_geometry_pairs'],0)
        self.assertTrue(p['unresolved_prerequisites'])

    def test_changed_obstacle_cannot_be_waived(self):
        r=self.receipt();r['contacts'].append(dict(a='Bar',b='UpperCarrier001'))
        with self.assertRaises(AssertionError):S.derive(r)

    def test_failed_geometry_cannot_be_reused(self):
        r=self.receipt();r['errors'].append('Invalid BRep')
        with self.assertRaises(AssertionError):S.derive(r)


if __name__=='__main__':unittest.main()
