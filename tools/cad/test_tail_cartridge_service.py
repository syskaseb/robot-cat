import json
import unittest
import pilot
from release_check import sha256,verify


class CartridgeServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out=pilot.CAD/'studies/tail-cartridge-service'
        cls.service=json.loads((cls.out/'service-audit.json').read_text())
        cls.joints=json.loads((cls.out/'joint-audit.json').read_text())
        cls.install=json.loads((cls.out/'installation-audit.json').read_text())

    def test_provenance(self):
        for r,script in [(self.service,'tail_cartridge_service.py'),(self.joints,'tail_cartridge_joints.py'),(self.install,'tail_cartridge_installation.py')]:
            self.assertEqual(r['study_sha256'],sha256(self.out/'TailCartridgeService.FCStd'))
            self.assertEqual(r['tool_sha256'],sha256(pilot.ROOT/'tools/cad'/script))
        for p,h in self.service['unchanged_robot_files'].items():self.assertEqual(h,sha256(pilot.ROOT/p))

    def test_geometry(self):
        self.assertTrue(self.service['strict_bop'])
        self.assertEqual(len(self.service['fully_constrained_sketches']),21)
        self.assertTrue(all(abs(v)<1e-5 for v in self.service['expected_difference_mm3']))
        self.assertEqual(self.service['relocation']['documents_loaded'],1)
        self.assertTrue(all(v>0 for v in self.service['parameter_removed_mm3'].values()))
        self.assertAlmostEqual(self.service['nut_seat_mm2']['prior'],self.service['nut_seat_mm2']['service'])

    def test_nut_path_controls(self):
        rows=self.service['nut_path']
        self.assertEqual([r['dy_mm'] for r in rows],[18-i*.25 for i in range(73)])
        self.assertTrue(self.service['conditional_nut_path_clear'])
        self.assertTrue(all(not r['intersections'] for r in rows))
        self.assertGreater(max(r['prior_root_mm3'] for r in rows),1)
        self.assertGreater(max(r['retained_bolt_mm3'] for r in rows),1)

    def test_tool_scope_and_blocked_counterhold(self):
        rows=self.service['shaft_tool_paths']
        self.assertEqual([r['diameter_mm'] for r in rows],[2.5,3,6])
        self.assertTrue(all(not r['intersections'] for r in rows[:2]))
        self.assertTrue(rows[2]['intersections'])
        self.assertTrue(all(r['intersections'] for r in self.service['m2_counterhold_paths']))

    def test_native_fixed_stack_only(self):
        self.assertEqual(self.joints['fixed_joints'],10)
        self.assertEqual(len(self.joints['parts']),11)
        self.assertEqual(len(self.joints['perturbation_recovery']),10)
        self.assertTrue(all(r['gap_mm']<1e-5 for r in self.joints['joint_gaps']))
        self.assertFalse(self.joints['horn_jointed'])
        self.assertFalse(self.joints['servo_motion_tested'])

    def test_installation_scope(self):
        self.assertEqual([r['height_above_rest_mm'] for r in self.install['samples']],list(range(36,-1,-3)))
        self.assertNotIn('MG92BOutput29',self.install['absent_components'])
        self.assertIn('UpperHousing34',self.install['absent_components'])
        self.assertTrue(self.install['conditional_path_clear'])
        self.assertFalse(self.install['print_ready'])
        self.assertTrue(all(v>1 for v in self.install['before_flat_positive_controls_mm3'].values()))

    def test_manifest(self):
        m=json.loads((pilot.ROOT/'hardware/releases/tail-cartridge-service.json').read_text())
        self.assertTrue(verify(pilot.ROOT,m)['integrity_ok'])
        self.assertFalse(verify(pilot.ROOT,m,True)['integrity_ok'])


if __name__=='__main__':unittest.main()
