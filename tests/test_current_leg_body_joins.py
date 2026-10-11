import json
import hashlib
import math
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from plan_current_moving_looms import curve_length, metrics
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint'


class BodyJoins(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=json.loads((OUT/'leg-body-joins-plan.json').read_text())

    def test_math_receipt_accounts_for_all_families_without_partial_credit(self):
        present={q['loom'] for q in self.p['looms']}
        rejected={q['loom'] for q in self.p['rejected']}
        expected={leg+str(i) for leg in ('FL','FR','RL','RR') for i in (1,2,3)}
        self.assertFalse(present & rejected)
        self.assertEqual(present | rejected,expected)
        self.assertEqual(len(present),len(self.p['looms']))
        self.assertEqual(self.p['status'],'REJECTED_BODY_JOIN_MATH' if rejected else 'BODY_JOIN_FIXED_LENGTH_MATH_ONLY')
        for loom in self.p['looms']:
            for pose in loom['poses']:
                length=sum(curve_length(q) for q in pose['spans_mm'])
                length+=sum(q['length_mm'] for key in ('departure_parts_mm','transition_parts_mm','return_parts_mm') for q in pose.get(key,[]))
                self.assertAlmostEqual(length,loom['fixed_bundle_guide_mm'],places=4,msg=loom['loom'])

    def test_changed_boundaries_are_not_clamps_or_selected(self):
        self.assertFalse(self.p['selected']);self.assertFalse(self.p['W5_complete']);self.assertFalse(self.p['physical_pass'])
        self.assertTrue(self.p['native_open']);self.assertTrue(self.p['complete_factory_capacity_open'])
        for loom in self.p['looms']:
            if loom['loom'] in ('FL3','RL2','RL3','RR2'):
                self.assertLessEqual(abs(loom['body_dock_mm'][1]),100)
                self.assertLessEqual(loom['minimum_complete_blank_lower_bound_mm'],850)

    def test_changed_curves_radius_and_continuity(self):
        for loom in self.p['looms']:
            if loom['loom'] not in ('FL3','RL2','RL3','RR2'):continue
            for pose in loom['poses']:
                pieces=pose.get('departure_parts_mm',[])+pose.get('transition_parts_mm',[])
                for a,b in zip(pieces,pieces[1:]):self.assertLess(math.dist(a['end'],b['start']),1e-6)
                for q in pose['spans_mm']:
                    self.assertGreaterEqual(metrics(q,240)[1],31)
                    self.assertLess(math.dist(q[-1],loom['body_dock_mm']),1e-6)
                for q in pose.get('transition_parts_mm',[]):
                    if q['kind']=='arc':self.assertGreaterEqual(q['radius_mm'],31)
                if not pose['spans_mm']:
                    self.assertLess(math.dist(pieces[-1]['end'],loom['body_dock_mm']),1e-6)

    def test_source_pins(self):
        for name,digest in self.p['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)

    def test_incomplete_plan_cannot_borrow_previous_green_screens(self):
        if not self.p['rejected']:self.skipTest('Complete math must pass new current screens')
        for file in ('leg-body-joins-screen.json','leg-body-joins-motion-screen.json'):
            report=json.loads((OUT/file).read_text())
            self.assertEqual(report['status'],'BLOCKED_INCOMPLETE_BODY_JOIN_MATH')
            self.assertEqual(report['geometry_checks_run'],0)
            self.assertFalse(report['W5_complete'])
            for n,h in report['source_sha256'].items():
                self.assertEqual(hashlib.sha256((ROOT/n).read_bytes()).hexdigest(),h,n)

    def test_rejected_receiver_relayout_preserves_selection_and_exposes_invalidations(self):
        report=json.loads((OUT/'front-receiver-relayout-plan.json').read_text())
        self.assertFalse(report['selected']);self.assertFalse(report['W5_complete'])
        self.assertTrue(report['actual_material_open']);self.assertTrue(report['native_open'])
        self.assertEqual(report['status'],'REJECTED_FL_RECEIVER_RELAYOUT')
        self.assertIsNone(report['candidate_FL3'])
        self.assertEqual(len(report['changed_wire_ids']),9)
        self.assertGreater(len(report['invalidated']),0)
        for n,h in report['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/n).read_bytes()).hexdigest(),h,n)


if __name__=='__main__':unittest.main()
