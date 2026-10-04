from pathlib import Path
import json
import unittest
from w5_leg_lower_fanouts_r1 import plan
from w5_leg_escape_fanouts_r1 import plan as escape_plan

ROOT=Path(__file__).resolve().parents[2]


class SourceAssemblyScope(unittest.TestCase):
    def test_failed_installed_access_not_promoted(self):
        receipt=json.loads((ROOT/'hardware/electronics/full-cat/w5-source-cage-assembly-receive-r1/assembly.json').read_text(encoding='utf-8'))
        self.assertFalse(receipt['installed_service_clear'])
        self.assertFalse(receipt['whole_source_assembly_complete'])
        self.assertFalse(receipt['selected'])
        self.assertFalse(receipt['W5_complete'])
        self.assertEqual(receipt['inherited_installed_contacts'],30)
        self.assertTrue(receipt['closed_STLs'])
        self.assertTrue(receipt['relocated_reopen'])

    def test_contact_count_keeps_original_receipt(self):
        receipt=json.loads((ROOT/'hardware/electronics/full-cat/w5-source-cage-access-native-r1/checks.json').read_text(encoding='utf-8'))
        self.assertEqual(receipt['status'],'SOURCE_CAGE_ACCESS_REJECTED')
        self.assertEqual(len(receipt['hits']),30)
        self.assertEqual(receipt['errors'],[])

    def test_lower_family_preserves_ports_V_and_input(self):
        old=json.loads((ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r5/intent.json').read_text(encoding='utf-8'))['routes']
        before=json.dumps(old,sort_keys=True)
        rows=plan(old)
        self.assertEqual(json.dumps(old,sort_keys=True),before)
        self.assertEqual(len(rows),36)
        self.assertEqual(len({r['wire'] for r in rows}),36)
        for prior,row in zip(old,rows):
            self.assertEqual(row['body_end'],prior['body_end'])
            self.assertEqual(row['waypoints_mm'][-1],prior['waypoints_mm'][-1])
            if row['role']=='V': self.assertEqual(row,prior)
            else:
                self.assertFalse(row['ground_orientation_180_same_footprint'])
                self.assertEqual(abs(row['waypoints_mm'][0][1]),30.5)
                self.assertLessEqual(row['waypoints_mm'][2][2],93)

    def test_escape_has_two_full_R10_rise_bends(self):
        old=json.loads((ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r5/intent.json').read_text(encoding='utf-8'))['routes']
        rows=escape_plan(old)
        for prior,row in zip(old,rows):
            self.assertEqual(row['body_end'],prior['body_end'])
            self.assertEqual(row['waypoints_mm'][-1],prior['waypoints_mm'][-1])
            if row['role']=='V': self.assertEqual(row,prior); continue
            p=row['waypoints_mm']
            self.assertGreaterEqual(p[3][2]-p[2][2],20)
            self.assertAlmostEqual(abs(p[4][0]-p[3][0]),25)
            self.assertGreaterEqual(abs(p[0][1]-p[1][1]),16)


if __name__=='__main__': unittest.main()
