import hashlib,json,unittest
from unittest.mock import MagicMock,patch
from current_body36_candidates import resolve

class ReceiptRecoveryTests(unittest.TestCase):
    def fixture(self):
        root=MagicMock();base={'routes':{str(i):{'revision':'base'} for i in range(36)}}
        (root/'base.json').read_text.return_value=json.dumps(base)
        old={'proposed_routes':{str(i):{'revision':'ancestor'} for i in range(27,36)}}
        raw=json.dumps(old).encode()
        now={'inherited_receipt':'base.json','retained_route_ids':[str(i) for i in range(27)],
             'proposed_routes':{'30':{'revision':'current'}},
             'qualified_changed_routes':{'31':{'revision':'qualified'}},
             'inherited_qualified_receipt':{'git_commit':'frozen','receipt':'receipt.json','sha256':hashlib.sha256(raw).hexdigest()}}
        return root,now,raw

    def test_material_only_receipt_preserves_missing_proposals(self):
        root,now,raw=self.fixture()
        with patch('current_body36_candidates.subprocess.check_output',return_value=raw):
            routes,chain=resolve(now,root)
        self.assertEqual(len(routes),36)
        self.assertEqual(routes['29']['revision'],'ancestor')
        self.assertEqual(routes['30']['revision'],'current')
        self.assertEqual(routes['31']['revision'],'qualified')
        self.assertEqual(len(chain),1)

    def test_altered_ancestor_is_rejected(self):
        root,now,raw=self.fixture()
        with patch('current_body36_candidates.subprocess.check_output',return_value=raw+b' '):
            with self.assertRaisesRegex(AssertionError,'Changed inherited'):resolve(now,root)

if __name__=='__main__':unittest.main()
