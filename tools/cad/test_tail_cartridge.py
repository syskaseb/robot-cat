"""Saved CAD evidence, not physical approval; no FreeCAD import required."""
import json
import unittest
import pilot
from release_check import sha256, verify


class CartridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out=pilot.CAD/'studies/tail-cartridge'
        cls.audit=json.loads((cls.out/'cartridge-audit.json').read_text())
        cls.details=json.loads((cls.out/'cartridge-details.json').read_text())

    def test_hashes(self):
        for report,script in [(self.audit,'tail_cartridge_study.py'),(self.details,'tail_cartridge_details.py')]:
            self.assertEqual(report['study_sha256'],sha256(self.out/'TailHornCartridge.FCStd'))
            self.assertEqual(report['tool_sha256'],sha256(pilot.ROOT/'tools/cad'/script))
        self.assertEqual(len(self.audit['unchanged_robot_files']),9)
        for name,digest in self.audit['unchanged_robot_files'].items():
            self.assertEqual(digest,sha256(pilot.ROOT/name))

    def test_geometry_and_parameter(self):
        self.assertEqual(len(self.audit['fully_constrained_sketches']),17)
        self.assertEqual(len(self.audit['geometry']),3)
        for value in self.audit['geometry'].values():
            self.assertTrue(value['strict_bop_passed'])
            self.assertEqual(value['solids'],1)
            self.assertTrue(all(v<236 for v in value['bbox_mm']))
        self.assertTrue(all(v>0 for v in self.audit['parameter_change_removed_mm3'].values()))
        self.assertEqual(self.audit['relocation']['documents_loaded'],1)
        for values in self.details['expected_boolean_difference_mm3'].values():
            self.assertTrue(all(abs(v)<1e-5 for v in values))

    def test_motion_scope_and_rejection_control(self):
        self.assertTrue(self.audit['conditional_nominal_fit_passed'])
        self.assertFalse(self.audit['native_joints_tested'])
        self.assertEqual([r['angle_deg'] for r in self.audit['motion_samples']],list(range(-30,31,5)))
        self.assertTrue(all(not r['intersections'] for r in self.audit['motion_samples']))
        old=json.loads((self.out/'rejected-r0/cartridge-audit.json').read_text())
        self.assertFalse(old['conditional_nominal_fit_passed'])
        self.assertTrue(all(r['intersections'] for r in old['motion_samples']))
        self.assertEqual(old['study_sha256'],sha256(self.out/'rejected-r0/TailHornCartridge.FCStd'))
        self.assertEqual(old['tool_sha256'],sha256(self.out/'rejected-r0/tail_cartridge_study.py'))

    def test_no_false_service_or_print_approval(self):
        self.assertGreater(self.details['assembled_root_blocks_OD6_tool_mm3'],1)
        self.assertTrue(all(v<.001 for v in self.details['pre_root_OD6_tool_intersections_mm3'].values()))
        self.assertFalse(self.audit['installed_in_robot'])
        self.assertFalse(self.audit['print_ready'])
        self.assertFalse(self.audit['physical_fit_proven'])
        self.assertFalse(self.audit['cad_saved_by_audit'])
        self.assertFalse(self.details['cad_saved'])
        self.assertEqual(len(self.details['relative_horn_play_samples']),41)

    def test_manifest_is_concept_only(self):
        manifest=json.loads((pilot.ROOT/'hardware/releases/tail-cartridge-study.json').read_text())
        self.assertTrue(verify(pilot.ROOT,manifest)['integrity_ok'])
        self.assertFalse(verify(pilot.ROOT,manifest,True)['integrity_ok'])


if __name__=='__main__':unittest.main()
