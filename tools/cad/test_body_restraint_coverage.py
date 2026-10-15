import copy,json,subprocess,unittest
from compose_current_body_restraint_coverage import unchanged_routes,ROOT,OUT


class CoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current=json.loads((OUT/'body36-shared-macro-layout.json').read_text())
        path=(OUT/'body36-shared-macro-layout.json').relative_to(ROOT).as_posix()
        commit=cls.current['inherited_qualified_receipt']['git_commit']
        cls.old=json.loads(subprocess.check_output(['git','show',commit+':'+path],cwd=ROOT))
        cls.base=json.loads((ROOT/cls.current['inherited_receipt']).read_text())
    def test_actual_old33_new3_composition(self):
        old,new=unchanged_routes(self.old,self.current,self.base)
        self.assertEqual(len(old),33);self.assertEqual(new,['W004','W022','W069'])
    def test_changed_inherited_curve_is_not_waived(self):
        q=copy.deepcopy(self.current);q['qualified_changed_routes']['W019']['parts'][0]['start'][0]+=.1
        with self.assertRaises(AssertionError):unchanged_routes(self.old,q,self.base)
    def test_partial_or_failed_new_gate_is_not_complete(self):
        q=copy.deepcopy(self.current);q['qualified_changed_routes'].pop('W004')
        with self.assertRaises(AssertionError):unchanged_routes(self.old,q,self.base)
        q=copy.deepcopy(self.current);q['attempts'][0]['errors']=['failure']
        with self.assertRaises(AssertionError):unchanged_routes(self.old,q,self.base)


if __name__=='__main__':unittest.main()
