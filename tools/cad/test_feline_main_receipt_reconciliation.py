"""Reconcile stale status without awarding current harness service or routes."""
import unittest
from compose_feline_current_body_routes import current
from compose_feline_rr_two_tier_boundaries import current as before


class MainReceiptReconciliation(unittest.TestCase):
    def test_four_caps_keep_datums_and_open_assembly(self):
        _,old,_=before();_,rows,_=current();prior={r['id']:r for r in old}
        selected=[r for r in rows if r.get('static36_receipt')]
        self.assertEqual(len(selected),4)
        self.assertEqual([r['id'] for r in rows],[r['id'] for r in old])
        for row in selected:
            for field in ('point_mm','routing_exit_mm','routing_exit_axis','prefix_geometry_owner'):
                self.assertEqual(row[field],prior[row['id']][field])
            self.assertFalse(row['whole_service_sequence_received'])
            self.assertTrue(row['whole_current_scene_delta_and_harness_release_OPEN'])
            self.assertTrue(row['world_and_tools_assembly_NOT_received'])
            self.assertFalse(row['full_middle_route_accepted'])


if __name__=='__main__':unittest.main()
