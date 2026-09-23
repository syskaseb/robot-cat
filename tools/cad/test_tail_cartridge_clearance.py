import json
import math
import unittest
import pilot
from release_check import sha256, verify
from tail_cartridge_clearance import OUT, TARGET, PREVIOUS


class CartridgeClearanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads((OUT/'audit.json').read_text())
        cls.h = json.loads((OUT/'housing-installation.json').read_text())
        cls.b = json.loads((OUT/'bearing-preassembly.json').read_text())

    def test_provenance(self):
        for r, name in [(self.r, 'tail_cartridge_clearance.py'), (self.h, 'tail_housing_installation.py')]:
            self.assertEqual(r['study_sha256'], sha256(TARGET))
            self.assertEqual(r['tool_sha256'], sha256(pilot.ROOT/'tools/cad'/name))
            for p, h in r['unchanged_robot_files'].items(): self.assertEqual(h, sha256(pilot.ROOT/p))
        self.assertEqual(self.r['previous_sha256'], sha256(PREVIOUS))

    def test_geometry_and_history(self):
        self.assertEqual(set(self.r['geometry']), {'LowerRetainerPETG', 'SupportedRoot34'})
        self.assertTrue(all(g['strict_bop'] and g['solids'] == 1 for g in self.r['geometry'].values()))
        self.assertEqual(len(self.r['fully_constrained_sketches']), 22)
        self.assertTrue(self.r['independent_intent_comparison'])
        self.assertEqual(self.r['relocation'], {'documents_loaded': 1, 'external_links': 0})
        for g in self.r['geometry'].values(): self.assertLess(max(g['bbox_mm'])+20, 256)

    def test_coupled_parameters(self):
        self.assertTrue(all(v > 0 for v in self.r['parameter_removed_mm3'].values()))
        self.assertGreater(self.r['boss_parameter_delta_mm3']['LowerRetainerPETG'], 0)
        self.assertLess(self.r['boss_parameter_delta_mm3']['SupportedRoot34'], 0)

    def test_four_walls_and_nominal_head_seats(self):
        self.assertEqual(len(self.r['divider_probes']), 4)
        self.assertEqual(len(self.r['head_seat_probes']), 4)
        for row in self.r['divider_probes']: self.assertAlmostEqual(row['wall_mm'], 1.4)
        for row in self.r['head_seat_probes']: self.assertAlmostEqual(row['area_mm2'], math.pi*(2.1**2-1.2**2))

    def test_native_bench_not_servo_coupling(self):
        self.assertEqual(self.r['fixed_joints'], 9)
        self.assertEqual(len(self.r['physical_parts']), 10)
        self.assertEqual(len(self.r['solver_recovery']), 9)
        for row in self.r['solver_recovery']:
            self.assertLess(row['max_translation_mm'], 1e-5)
            self.assertLess(row['max_rotation_rad'], 1e-5)
        self.assertFalse(self.r['horn_jointed'])

    def test_cartridge_paths(self):
        self.assertEqual([r['angle_deg'] for r in self.r['motion_samples']], list(range(-30, 31, 5)))
        self.assertEqual([r['height_mm'] for r in self.r['installation_samples']], list(range(36, -1, -3)))
        self.assertEqual([r['dy_mm'] for r in self.r['nut_path']], [18-i*.25 for i in range(73)])
        for field in ('motion_samples', 'installation_samples', 'nut_path'):
            self.assertTrue(all(not r['intersections'] for r in self.r[field]))
        self.assertTrue(self.r['conditional_checks_passed'])
        self.assertFalse(self.r['internal_intersections'])

    def test_service_controls(self):
        self.assertAlmostEqual(self.r['nut_seat_mm2']['previous'], self.r['nut_seat_mm2']['current'])
        self.assertTrue(all(not r['intersections'] for r in self.r['shaft_tools'][:2]))
        self.assertTrue(self.r['shaft_tools'][2]['intersections'])
        self.assertGreater(max(r['short_channel_control_mm3'] for r in self.r['nut_path']), 1)
        self.assertGreater(max(r['retained_bolt_mm3'] for r in self.r['nut_path']), 1)

    def test_housing_sequence_accounting(self):
        rows = self.h['stages']
        self.assertEqual([r['name'] for r in rows], ['closed_bearing_block', 'housing_screws', 'spindle_cap', 'axial_screw'])
        used = set()
        for i, row in enumerate(rows):
            self.assertFalse(used.intersection(row['moving']))
            used.update(row['moving'])
            self.assertEqual([r['height_mm'] for r in row['samples']], list(range(32 if i in (0,3) else 20, -1, -2)))
            if i: self.assertEqual(row['fixed_count'], rows[i-1]['fixed_count']+len(rows[i-1]['moving']))
            self.assertEqual(row['clear'], not row['internal_intersections'] and all(not r['intersections'] for r in row['samples']))
        self.assertEqual(self.h['all_sampled_stages_clear'], all(r['clear'] for r in rows))

    def test_housing_scope_is_explicit(self):
        self.assertIn('MG92BOutput29', self.h['initially_present'])
        self.assertNotIn('MG92BOutput29', self.h['initially_absent'])
        self.assertIn('SpindleNut34', self.h['initially_present'])
        self.assertFalse(self.h['physical_assembly_proven'])
        self.assertFalse(self.h['final_tail_segments_installed'])
        self.assertTrue(self.h['not_checked'])

    def test_manifest_blocks_print_release(self):
        m = json.loads((pilot.ROOT/'hardware/releases/tail-cartridge-clearance.json').read_text())
        self.assertTrue(verify(pilot.ROOT, m)['integrity_ok'])
        self.assertFalse(verify(pilot.ROOT, m, True)['integrity_ok'])
        self.assertFalse(self.r['print_ready'])
        self.assertFalse(self.h['print_ready'])
        self.assertFalse(self.r['installed_in_robot'])

    def test_bearing_bench_provenance(self):
        self.assertEqual(self.b['tool_sha256'], sha256(pilot.ROOT/'tools/cad/tail_bearing_preassembly.py'))
        for p, h in (self.b['source_sha256'] | self.b['helper_sha256']).items():
            self.assertEqual(h, sha256(pilot.ROOT/p))
        self.assertFalse(self.b['robot_obstacles_included'])
        self.assertFalse(self.b['print_ready'])

    def test_bearing_bench_paths(self):
        self.assertEqual(len(self.b['stages']), 7)
        self.assertEqual([r['moving'] for r in self.b['stages']], [
            ['BearingLower34'], ['InnerSpacer34'], ['OuterSpacer34'], ['BearingUpper34'],
            ['BearingCap34'], ['BearingCapBolt34_0', 'BearingCapBolt34_1'], ['BearingCapNut34_0', 'BearingCapNut34_1']])
        for i, row in enumerate(self.b['stages']):
            self.assertEqual([r['height_mm'] for r in row['samples']], list(range(-24, 1, 2) if i == 6 else range(24, -1, -2)))
            self.assertEqual(row['clear'], all(not r['intersections'] for r in row['samples']))
        self.assertEqual(self.b['all_sampled_stages_clear'], all(r['clear'] for r in self.b['stages']))
        self.assertGreater(self.b['misaligned_bearing_control_mm3'], 1)

    def test_lid_geometry_and_tool_access(self):
        self.assertEqual(self.h['lid_sha256'], sha256(OUT/'TailBearingLidService.FCStd'))
        self.assertEqual(self.h['lid_sha256'], self.b['lid_sha256'])
        g = self.h['lid_geometry']
        self.assertTrue(g['strict_bop'])
        self.assertEqual(g['solids'], 1)
        self.assertEqual(len(g['sketches']), 3)
        self.assertEqual(g['relocated_documents'], 1)
        self.assertGreater(g['parameter_removed_mm3'], 0)
        self.assertTrue(g['independent_intent_comparison'])
        self.assertTrue(self.h['housing_driver_paths_clear'])
        self.assertTrue(all(not r['intersections'] and r['old_lid_control_mm3'] > 1 for r in self.h['housing_driver_paths']))
        self.assertTrue(self.b['counterhold_envelopes_clear'])
        self.assertTrue(all(not r['socket_tip_fit_proven'] for r in self.b['nut_counterhold_envelopes']))

    def test_superseded_sequence_is_preserved(self):
        old = OUT/'superseded-open-lid-sequence'
        r = json.loads((old/'housing-installation.json').read_text())
        self.assertEqual(r['tool_sha256'], sha256(old/'tail_housing_installation.py'))
        self.assertFalse(r['physical_assembly_proven'])


if __name__ == '__main__': unittest.main()
