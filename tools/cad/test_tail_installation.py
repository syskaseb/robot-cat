"""Regression contracts for installed R4 evidence, stdlib only."""
import json
import unittest
import pilot
import integrate_tail_cartridge as task
from release_check import verify, sha256
from package_pilot import bom_instances


class TailInstallationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = json.loads((task.OUT/'geometry.json').read_text())
        cls.n = json.loads((task.OUT/'relocation-native.json').read_text())
        cls.m = json.loads((task.OUT/'migration.json').read_text())
        cls.plan = json.loads((task.OUT/'assembly-plan.json').read_text())

    def test_hashes(self):
        self.assertEqual(self.m['assembly_sha256'], sha256(task.TARGET))
        self.assertEqual(self.m['module_sha256'], sha256(task.MODULE))
        for r in [self.g,self.n]:
            for p,h in r['file_sha256'].items(): self.assertEqual(h,sha256(pilot.ROOT/p))
            self.assertEqual(r['tool_sha256'],sha256(pilot.ROOT/'tools/cad/validate_tail_integration.py'))
        for p,h in (self.m['unchanged_predecessor_files'] | self.m['source_sha256']).items():
            self.assertEqual(h,sha256(pilot.ROOT/p))

    def test_component_and_joint_accounting(self):
        self.assertEqual(len(self.plan['components']),329)
        self.assertEqual(len({r['name'] for r in self.plan['components']}),329)
        self.assertEqual(len(self.plan['joints']),328)
        self.assertEqual(sum(r['type']=='Fixed' for r in self.plan['joints']),315)
        self.assertEqual(self.g['unchanged_components'],318)
        self.assertEqual(len(self.g['geometry_comparison']),329)
        self.assertEqual(self.g['inherited_joint_frames_unchanged'],319)

    def test_relocation_and_link_ownership(self):
        self.assertTrue(self.n['fresh_process'])
        self.assertFalse(self.n['outside_dependencies'])
        self.assertEqual(self.n['documents'],10)
        self.assertEqual(len(self.n['links']),54)
        owned = {r['component'] for r in self.n['links'] if r['owner']=='modules/tail/TailCartridge.FCStd'}
        self.assertEqual(owned,set(task.ADDED)|set(task.REPLACEMENTS))

    def test_parameters_reach_all_mating_parts(self):
        self.assertEqual(len(self.n['parameters']),3)
        for r in self.n['parameters']: self.assertTrue(r['restored'])
        delta = self.n['parameters'][0]['volume_delta_mm3']
        self.assertGreater(delta['TailLowerRetainer'],0)
        self.assertLess(delta['TailRoot29'],0)

    def test_editable_prints_and_geometry(self):
        self.assertEqual(len(self.g['constrained_sketches']),25)
        self.assertEqual(len(self.g['new_geometry']),11)
        self.assertTrue(self.g['misplacement_control_detected'])
        for name in ['TailRoot29','TailLowerRetainer','BearingCap34']:
            g=self.g['new_geometry'][name]
            self.assertTrue(g['strict_bop'])
            self.assertEqual(g['solids'],1)
            self.assertLess(max(g['bbox_mm'])+20,256)

    def test_native_retention_and_real_excursions(self):
        n=self.n['native']
        self.assertEqual((n['components'],n['fixed'],n['revolute'],n['temporary']),(329,315,13,29))
        self.assertEqual(len(n['frames']),22)
        self.assertEqual(len(n['peaks_deg']),13)
        self.assertAlmostEqual(n['peaks_deg']['Rev_TailYaw29'],30)
        for r in n['frames']:
            for key in ['gap_mm','fixed_error_rad','axis_error_rad','geometry_error_mm']: self.assertLess(r[key],1e-5)
        self.assertEqual(set(n['added_centroid_excursions_mm']),set(task.ADDED))
        self.assertTrue(all(v>.1 for v in n['added_centroid_excursions_mm'].values()))
        self.assertTrue(n['restored'])

    def test_incremental_collision_samples(self):
        self.assertFalse(self.g['static_intersections'])
        self.assertEqual([r['angle_deg'] for r in self.g['tail_collision_samples']],list(range(-30,31,5)))
        self.assertTrue(all(not r['intersections'] for r in self.g['tail_collision_samples']))
        self.assertTrue(set(task.ADDED).issubset(self.g['co_rotated_parts']))

    def test_delta_bom_no_double_count(self):
        b=json.loads((pilot.ROOT/'hardware/bom/tail-cartridge-installation.json').read_text())
        self.assertEqual(bom_instances(b),set(task.ADDED)|set(task.REPLACEMENTS))
        self.assertEqual(set(b['replaces_assembly_instances']),set(task.REPLACEMENTS))
        self.assertEqual(sum(p['quantity'] for p in b['parts'] if p['action']=='add'),9)

    def test_current_entry_and_readiness_fail_closed(self):
        # Historical checkpoint tests must not pin the mutable active selector.
        entry=json.loads((task.OUT/'checkpoint/current-assembly.json').read_text())
        self.assertEqual(pilot.ROOT/entry['entry'],task.TARGET)
        m=json.loads((pilot.ROOT/entry['manifest']).read_text())
        self.assertTrue(verify(pilot.ROOT,m)['integrity_ok'])
        self.assertFalse(verify(pilot.ROOT,m,True)['integrity_ok'])
        self.assertTrue(m['installed_in_robot'])
        self.assertFalse(self.n['servo_coupling_confirmed'])
        self.assertFalse(self.m['horn_included_as_physical_part'])
        self.assertFalse(self.g['legacy_shell_bop_passed'])
        self.assertFalse(self.n['cad_saved'])


if __name__ == '__main__': unittest.main()
