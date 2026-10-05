"""Scope/count checks for the single pending print set, no whole CAD audit."""
import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

class PrintSet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'hardware/electronics/full-cat/w5-final-print-set-candidate-r1/manifest.json').read_text(encoding='utf-8'))
        cls.old=json.loads((ROOT/'hardware/manufacturing/one-batch-prototype-r53/selection.json').read_text(encoding='utf-8'))

    def test_one_job_per_identity(self):
        p=self.data['prints'];self.assertEqual(len(p),86)
        self.assertEqual(len({r['identity'] for r in p}),86)
        self.assertEqual(sum(r['quantity'] for r in p if r['purpose']=='installed_candidate'),134)

    def test_retained_parts_not_duplicated(self):
        old={r['identity']:r for r in self.old['prints']};new={r['identity']:r for r in self.data['prints']}
        changed={r['identity'] for r in self.data['source_parts']}
        self.assertEqual(len(changed.intersection(old)),5)
        for identity,row in old.items():
            self.assertIn(identity,new)
            if identity not in changed:self.assertEqual(new[identity],row)

    def test_received_fit_and_hobby_scope(self):
        for r in self.data['source_parts']:
            self.assertLessEqual(max(r['dimensions_mm'])+6,256)
            self.assertFalse(r['slicer_checked']);self.assertFalse(r['physical_fit_strength_creep_verified'])
        for key in ('selected','W1_complete','W5_complete','phase1_complete','physical_pass'):
            self.assertFalse(self.data[key])

if __name__=='__main__':unittest.main()
