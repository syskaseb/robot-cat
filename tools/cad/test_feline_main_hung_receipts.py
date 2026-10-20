"""Current constructive MAIN interfaces, not a whole-N01 acceptance test."""
import json,unittest
import FreeCAD
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import received
from compose_feline_cuff_boundaries import current as parent
from compose_feline_main_hung_boundaries import current
from feline_physical_wire_profiles import load


class MainReceipts(unittest.TestCase):
    def test_unchanged_identities_and_distinct_physical_datums(self):
        _,old,_=parent();_,rows,_=current()
        self.assertEqual(len(rows),246)
        for a,b in zip(old,rows):
            for k in ('id','wire','portion_id','endpoint','group'):self.assertEqual(a[k],b[k])
        changed=[r for r in rows if r['group']=='MAIN'];self.assertEqual(len(changed),4)
        for r in changed:
            self.assertNotEqual(r['actual_source_pad_mm'],r['point_mm'])
            self.assertNotEqual(r['point_mm'],r['routing_exit_mm'])
            self.assertEqual(r['source_full_individual_grip_after_RNF_mm'],9)
            self.assertEqual(r['source_RNF_raw_blank_mm'],16)
            self.assertFalse(r['full_middle_route_accepted'])

    def test_current_carrier_not_refined_or_cut(self):
        _,r=received();self.assertFalse(r['N01_complete']);self.assertFalse(r['physical_pass'])
        self.assertEqual(r['byte_identical_actor_count'],25)
        self.assertTrue(r['original_Pi_PWM_carrier_unchanged'])
        for actual,expected in zip(r['bay_centre_Y_interval_mm'],[-84.57,-79.705]):self.assertAlmostEqual(actual,expected,7)
        self.assertAlmostEqual(r['bay_chosen_mid_Y_mm'],-82.1375,5)

    def test_actual_nominal_not_larger_capacity_or_helu_shrink(self):
        r,_,_=load()
        for w in ('W060','W078','W079','W080'):
            p=r['portions'][w+'/retained0'];self.assertEqual(p['project_radius_mm'],1.05)
            self.assertEqual(p['legacy_capacity_radius_mm'],1.55)
            self.assertFalse(p['supplier_OD_guaranteed'])
        for w in ('W026','W037','W045','W053'):
            p=r['portions'][w+'/custom'];self.assertGreaterEqual(p['project_radius_mm'],2.1)
            self.assertGreaterEqual(p['minimum_project_R_mm'],25.2)


if __name__=='__main__':unittest.main()
