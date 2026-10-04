import unittest
from w5_source_material_contribution_r1 import contribution


class SourceContributionTests(unittest.TestCase):
    def inputs(self):
        return (dict(route_wires=['W064','W065','W067','W068','XA01'],S1_trial_total_mm=2390,legacy_S1_mm=920,
                     route_trial_mm=dict(W064=620,W065=480,W067=700,W068=590,XA01=40)),
                dict(HELU23802=dict(unique_roles=[dict(id='W066',blank_mm=330),dict(id='bank_extensions',blank_mm=1190)])),
                dict(status='FOUR_SOURCE_INSULATION_GRIPS_LOCAL_COMPLETE_UNSELECTED',hits=[],errors=[]))

    def test_replace_reserve_not_add(self):
        r=contribution(*self.inputs()); self.assertEqual(r['HELU23802']['nominal_total_mm'],3910)
        self.assertEqual(r['HELU23802']['candidate_stock_m'],5)
        self.assertEqual(r['T18I145']['contribution'],8)
        self.assertFalse(r['W5_complete']); self.assertFalse(r['selection_changed'])

    def test_duplicate_source_role_rejected(self):
        source,bank,grips=self.inputs(); bank['HELU23802']['unique_roles'][1]['id']='W064'
        with self.assertRaises(AssertionError): contribution(source,bank,grips)

    def test_rejected_grip_not_material_choice(self):
        source,bank,grips=self.inputs(); grips['hits']=[dict(owner='Cover')]
        with self.assertRaises(AssertionError): contribution(source,bank,grips)

    def test_no_fake_prefuse_or_whole_stock_completion(self):
        r=contribution(*self.inputs())
        self.assertTrue(r['HELU23502_XA01']['prefuse_internal_holder_length_unknown'])
        self.assertFalse(r['K3_complete']); self.assertFalse(r['physical_pass'])

    def test_source_lengths_do_not_inherit_short_source_E3(self):
        r=contribution(*self.inputs()); e=r['E3_changed_length_inputs']
        self.assertEqual(e['FRONT_nominal_mm']+e['REAR_nominal_mm'],2390)
        self.assertEqual(e['FRONT_delta_mm']+e['REAR_delta_mm'],1470)
        self.assertFalse(r['E3_complete'])


if __name__=='__main__': unittest.main()
