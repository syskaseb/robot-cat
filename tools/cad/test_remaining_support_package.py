import copy,unittest
from package_remaining_supports import require_complete

class PackageTest(unittest.TestCase):
    def fixture(self):
        native=dict(status='REMAINING36LAND_SUPPORT_SET_NATIVE_PREPARED_W5_OPEN',
            native_documents=[{}]*3,exports=[dict(part=str(i),quantity=1,size_mm=[200,200,100]) for i in range(12)],
            relocated_reopen=True,parameter_restore_mm=[4,4.2,4],
            installed_new_hardware={'independent_T18I_bands':36,'provisional_case_bonds':4,'new_screws':0},
            physical_pass=False,W5_complete=False)
        material=dict(status='COMBINED_SUPPORT_MATERIAL_CLEAR_NATIVE_OPEN',groups=[{}]*12,contacts=[],errors=[])
        return native,material

    def test_complete_local_contract(self):require_complete(*self.fixture())

    def test_incomplete_export_and_parameter_rejected(self):
        n,m=self.fixture();n['exports'].pop()
        with self.assertRaises(AssertionError):require_complete(n,m)
        n,m=self.fixture();n['parameter_restore_mm']=[4,4.2]
        with self.assertRaises(AssertionError):require_complete(n,m)

    def test_contact_and_physical_claim_rejected(self):
        n,m=self.fixture();m['contacts']=[{'target':'real-part'}]
        with self.assertRaises(AssertionError):require_complete(n,m)
        n,m=self.fixture();n['physical_pass']=True
        with self.assertRaises(AssertionError):require_complete(n,m)

    def test_print_margin_rejected(self):
        n,m=self.fixture();n['exports'][0]['size_mm'][0]=248
        with self.assertRaises(AssertionError):require_complete(n,m)

if __name__=='__main__':unittest.main()
