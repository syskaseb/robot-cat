import copy,json,unittest
from package_current_w5 import validate_counts,OUT


class W5PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.coverage=json.loads((OUT/'w5-current-end-coverage.json').read_text())
        cls.materials=json.loads((OUT/'w5-nominal-material-selection.json').read_text())
        cls.assembly=json.loads((OUT/'current-w5-assembly/neutral-manifest.json').read_text())
    def test_current_complete_scope(self):validate_counts(self.coverage,self.materials,self.assembly)
    def test_one_missing_end_is_rejected(self):
        q=copy.deepcopy(self.coverage);q['fixed_physical_guide_ends'].pop()
        with self.assertRaises(AssertionError):validate_counts(q,self.materials,self.assembly)
    def test_motion_duplicate_is_rejected(self):
        q=copy.deepcopy(self.assembly);q['reference_objects'].append(dict(name='Band_RL3/Splice/1/-15/0'))
        with self.assertRaises(AssertionError):validate_counts(self.coverage,self.materials,q)
    def test_actual_cut_not_invented(self):
        q=copy.deepcopy(self.materials);q['portions'][0]['actual_cut_mm']=123
        with self.assertRaises(AssertionError):validate_counts(self.coverage,q,self.assembly)


if __name__=='__main__':unittest.main()
