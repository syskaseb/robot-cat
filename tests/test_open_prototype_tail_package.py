"""M3 is a complete current nominal mechanical selection, never wiring/PASS."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT=BASE/'tail-mount-checkpoint'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class TailPackage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=read(OUT/'selection.json');cls.m=read(OUT/'manifest.json')
        cls.motion=read(OUT/'tail-assembly-checks.json')

    def test_complete_current_mechanics_only(self):
        self.assertTrue(self.p['selected'] and self.p['mechanical_M3_complete'])
        for k in ('physical_pass','wiring_complete','print_ready','full_phase1_complete'):
            self.assertFalse(self.p[k])
        self.assertGreaterEqual(len(self.p['phase2_gates']),5)

    def test_current_nominal_motion_and_native_reopen(self):
        self.assertEqual(self.motion['contacts'],[]);self.assertEqual(self.motion['errors'],[])
        self.assertEqual([r['angle_deg'] for r in self.motion['motion_samples']],list(range(-30,31,5)))
        self.assertTrue(all(r['new_contacts']==0 for r in self.motion['motion_samples']))
        self.assertEqual(len(set(self.motion['tail_identities'])),61)
        self.assertTrue(self.motion['whole_tail_parameter_restore'])
        reopen=read(OUT/'tail-reopen-checks.json')
        self.assertEqual(reopen['external_link_count'],0)
        self.assertTrue(reopen['all_61_rise_restored'])
        self.assertEqual(reopen['localized_moving_parts_checked'],33)

    def test_one_fixed_score_not_partial_wiring(self):
        score=read(BASE/'current-phase1-score.json')
        self.assertEqual(score['fixed_total'],20);self.assertEqual(score['result_count'],4)
        self.assertEqual(score['result_percent'],20)
        self.assertEqual(set(score['confirmed_result_ids']),{'M1','M3','E4','A1'})
        self.assertEqual(score['evidence_sha256'],digest(OUT/'manifest.json'))

    def test_no_duplicate_frame_hardware_or_horns(self):
        hw=self.p['shared_rear_frame_hardware']
        self.assertEqual((hw['M2x30'],hw['M2_nut_reused'],hw['M2_washer_reused']),(4,4,8))
        self.assertEqual(hw['procurement_contribution_only']['purchased'],0)
        self.assertEqual(self.p['tail_internal_hardware']['unique_parts'],44)
        horns=[r for r in self.p['prints'] if r['identity']=='drive:MG92BPrintedHorn20T-R2']
        self.assertEqual(len(horns),1);self.assertEqual(horns[0]['quantity'],1)
        self.assertEqual(sum(r['quantity'] for r in self.p['prints']),21)

    def test_print_margin_and_retained_monitor_ties(self):
        self.assertTrue(all(max(r['print_size_mm'])+10<256 for r in self.p['prints']))
        self.assertEqual(self.p['monitor']['nominal_length_mm'],145)
        self.assertEqual(self.p['monitor']['band_channel_minimum_floor_mm'],1.6)
        self.assertTrue(self.p['monitor']['ties_retained_not_extra'])

    def test_hash_integrity_and_print_gate_stays_closed(self):
        spec=importlib.util.spec_from_file_location('tail_release_check',ROOT/'tools/cad/release_check.py')
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        self.assertTrue(mod.verify(ROOT,self.m)['integrity_ok'])
        self.assertFalse(mod.verify(ROOT,self.m,True)['integrity_ok'])
        corrupted=dict(self.m,files=[dict(self.m['files'][0],sha256='0'*64)]+self.m['files'][1:])
        self.assertFalse(mod.verify(ROOT,corrupted)['integrity_ok'])

if __name__=='__main__':unittest.main()
