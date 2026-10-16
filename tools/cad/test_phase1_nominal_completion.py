import copy, json, unittest
from finalize_phase1_prototype import OUT, validate_basis


class NominalCompletion(unittest.TestCase):
    def setUp(self):
        self.criteria=json.loads((OUT/'criteria.json').read_text())
        self.result=json.loads((OUT/'assessment.json').read_text())

    def test_complete_documentation(self):
        self.assertTrue(validate_basis(self.criteria,self.result))

    def test_rejects_physical_or_power_claim(self):
        for flag in ('physical_pass','power_authorized','electrical_qualification_complete'):
            r=copy.deepcopy(self.result);r[flag]=True
            with self.assertRaises(AssertionError):validate_basis(self.criteria,r)

    def test_fixed_denominator(self):
        self.result['fixed_total']=19
        with self.assertRaises(AssertionError):validate_basis(self.criteria,self.result)

    def test_missing_fuse(self):
        self.result['fuse_roles'].pop()
        with self.assertRaises(AssertionError):validate_basis(self.criteria,self.result)

    def test_no_waived_LiPo_hold(self):
        self.result['phase2_holds'][0]['blocks_LiPo_trials']=False
        with self.assertRaises(AssertionError):validate_basis(self.criteria,self.result)

    def test_no_fake_Waveshare_wire_spec(self):
        self.result['assumptions']['cable_26AWG']['delivered_Waveshare_confirmed']=True
        with self.assertRaises(AssertionError):validate_basis(self.criteria,self.result)

    def test_overload_not_permitted(self):
        self.result['scenarios']['all_stall_permitted']=True
        with self.assertRaises(AssertionError):validate_basis(self.criteria,self.result)


if __name__=='__main__':unittest.main()
