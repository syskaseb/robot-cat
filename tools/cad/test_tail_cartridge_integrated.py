import json
import unittest
import pilot
from release_check import sha256, verify
from tail_cartridge_integrated import OUT, TARGET, PREVIOUS


class IntegratedCartridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.r = json.loads((OUT/'audit.json').read_text())

    def test_provenance(self):
        self.assertEqual(self.r['study_sha256'], sha256(TARGET))
        self.assertEqual(self.r['previous_sha256'], sha256(PREVIOUS))
        self.assertEqual(self.r['tool_sha256'], sha256(pilot.ROOT/'tools/cad/tail_cartridge_integrated.py'))
        for p, h in self.r['unchanged_robot_files'].items(): self.assertEqual(h, sha256(pilot.ROOT/p))

    def test_two_prints_and_editable_history(self):
        self.assertEqual(set(self.r['geometry']), {'LowerRetainerPETG', 'SupportedRoot34'})
        self.assertTrue(all(g['strict_bop'] and g['solids'] == 1 for g in self.r['geometry'].values()))
        self.assertEqual(len(self.r['fully_constrained_sketches']), 22)
        self.assertTrue(self.r['independent_intent_comparison'])
        self.assertEqual(self.r['relocation'], {'documents_loaded': 1, 'external_links': 0})
        self.assertTrue(all(v > 0 for v in self.r['parameter_removed_mm3'].values()))

    def test_local_roof_not_global_wall_approval(self):
        for row, expected in zip(self.r['roof_probes'], [3.55, 5.65]):
            self.assertAlmostEqual(row['solid_length_mm'], expected)
        self.assertEqual(self.r['remaining_slot_divider_mm'], .9)
        self.assertFalse(self.r['print_ready'])
        self.assertEqual(self.r['fastener_stack_mm']['protrusion'], .4)

    def test_nine_native_fixed_and_no_fake_servo_joint(self):
        self.assertEqual(self.r['fixed_joints'], 9)
        self.assertEqual(len(self.r['physical_parts']), 10)
        self.assertEqual(len(self.r['solver_recovery']), 9)
        for row in self.r['solver_recovery']:
            self.assertLess(row['max_translation_mm'], 1e-5)
            self.assertLess(row['max_rotation_rad'], 1e-5)
        self.assertFalse(self.r['horn_jointed'])

    def test_sampled_paths(self):
        self.assertEqual([r['angle_deg'] for r in self.r['motion_samples']], list(range(-30, 31, 5)))
        self.assertEqual([r['height_mm'] for r in self.r['installation_samples']], list(range(36, -1, -3)))
        self.assertEqual([r['dy_mm'] for r in self.r['nut_path']], [18-i*.25 for i in range(73)])
        for field in ('motion_samples', 'installation_samples', 'nut_path'):
            self.assertTrue(all(not r['intersections'] for r in self.r[field]))
        self.assertNotIn('MG92BOutput29', self.r['installation_absent'])
        self.assertIn('UpperHousing34', self.r['installation_absent'])
        self.assertTrue(self.r['conditional_checks_passed'])

    def test_clearance_and_service_controls(self):
        self.assertFalse(self.r['internal_intersections'])
        self.assertTrue(all(v < .001 for v in self.r['horn_intersections_mm3'].values()))
        self.assertAlmostEqual(self.r['nut_seat_mm2']['r2'], self.r['nut_seat_mm2']['r3'])
        self.assertTrue(all(not r['intersections'] for r in self.r['shaft_tools'][:2]))
        self.assertTrue(self.r['shaft_tools'][2]['intersections'])
        self.assertGreater(max(r['retained_bolt_mm3'] for r in self.r['nut_path']), 1)
        self.assertGreater(max(r['short_channel_control_mm3'] for r in self.r['nut_path']), 1)
        self.assertEqual(self.r['rejected_study_sha256'], sha256(OUT/'rejected-short-channel/TailCartridgeIntegrated.FCStd'))

    def test_manifest_blocks_print_release(self):
        m = json.loads((pilot.ROOT/'hardware/releases/tail-cartridge-integrated.json').read_text())
        self.assertTrue(verify(pilot.ROOT, m)['integrity_ok'])
        self.assertFalse(verify(pilot.ROOT, m, True)['integrity_ok'])
        self.assertFalse(self.r['installed_in_robot'])

    def test_rejected_short_channel_is_preserved(self):
        rejected = OUT/'rejected-short-channel'
        r = json.loads((rejected/'audit.json').read_text())
        self.assertEqual(r['study_sha256'], sha256(rejected/'TailCartridgeIntegrated.FCStd'))
        self.assertEqual(r['tool_sha256'], sha256(rejected/'tail_cartridge_integrated.py'))
        self.assertFalse(r['conditional_checks_passed'])
        self.assertTrue(any(row['intersections'] for row in r['nut_path']))
        self.assertTrue(all(not row['intersections'] for row in r['motion_samples']))


if __name__ == '__main__': unittest.main()
