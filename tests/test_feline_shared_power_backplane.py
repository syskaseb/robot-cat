"""Shared architecture constructor and explicit supplier/physical distinction."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from feline_shared_power_backplane import fast_inputs,proposal,intrinsic_failures


class SharedBackplane(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parts,cls.groups,cls.kinds,cls.facts=proposal(fast_inputs())

    def test_complete_occupied_pi_kit_moves_rigidly(self):
        self.assertEqual(self.facts['Pi_selected_complete_kit_parts'],44)
        self.assertEqual(sum(g=='PiSide' for g in self.groups.values()),44)
        centre=self.facts['Pi_actual_PCB_centre_mm']
        self.assertAlmostEqual(centre[0],0)
        self.assertAlmostEqual(centre[2],32)
        self.assertLess(max(s.BoundBox.YMax for n,s in self.parts.items() if self.groups[n]=='PiSide'),96.00001)

    def test_actual_source_metal_gaps_and_nominal_supplier_holds_separate(self):
        receipts=self.facts['S0_intrinsic_ring_receipts']
        holds=[r for r in receipts if r.get('classification')=='SUPPLIER_INTERFACE_HOLD']
        self.assertEqual(len(holds),2)
        self.assertTrue(all(not r['physical_clearance_claimed'] for r in holds))
        self.assertEqual(intrinsic_failures(receipts),[])
        self.assertEqual(len(receipts)-len(holds),8)

    def test_real_metal_failure_is_never_a_supplier_waiver(self):
        self.assertEqual(len(intrinsic_failures([dict(gap_mm=0,required_mm=1.25,positive_common_mm3=2)])),1)
        self.assertFalse(self.facts['whole_power_core_gate_complete'])
        self.assertFalse(self.facts['N01_complete'])
        self.assertFalse(self.facts['physical_pass'])

    def test_revised_functional_zones_preserve_board_and_source_parts(self):
        parts,groups,_,f=proposal(fast_inputs(),True)
        self.assertEqual(sum(g=='PiUpper' for g in groups.values()),44)
        self.assertEqual(sum(g=='S0' for g in groups.values()),11)
        self.assertEqual(sum(g=='S1' for g in groups.values()),10)
        self.assertEqual(f['MAIN_whole_changed_unit']['relative_translation_mm'][1],45)
        self.assertTrue(f['MAIN_whole_changed_unit']['complete_two_fastener_stacks_reversed'])
        for s in parts.values():
            b=s.BoundBox
            self.assertGreaterEqual(b.XMin,-138.25-1e-5)
            self.assertLessEqual(b.ZMax,108.75+1e-5)
        self.assertGreater(parts['Ref_Material_S0_key_CP2_0_0'].BoundBox.Center.x,
                           parts['Ref_Material_S0_body_CP2_0_0'].BoundBox.Center.x)

    def test_shared_fore_plan_includes_both_full_factory_blanks_and_real_usb_curve(self):
        parts,groups,_,f=proposal(fast_inputs(),True,True)
        self.assertFalse(f['reuse_original_S1_pose'])
        self.assertEqual(sum(g=='PiUpper' for g in groups.values()),44)
        for r in f['shared_fore_units']['F_HY_full_factory_ports']:
            self.assertAlmostEqual(r['external_factory_mm']+r['internal_assumed_mm'],100)
            self.assertAlmostEqual(sum((a-b)**2 for a,b in zip(*r['first_full9_mm']))**.5,9)
        usb=f['shared_fore_units']['PiUSB_changed_profile']
        self.assertEqual(usb['R_mm'],30)
        self.assertEqual(usb['first_project_mm'],3)
        self.assertEqual(usb['status'],'OWNED_BAYS_PROFILE_CLEAR_EXTERNAL_WORLD_STILL_OPEN')
        self.assertLess(f['Pi_whole_bay_translation_interval_mm'][0],f['Pi_relative_pose']['translation_mm'][0])
        for s in parts.values():
            b=s.optimalBoundingBox()
            self.assertGreaterEqual(b.XMin,-138.25-1e-5)
            self.assertGreaterEqual(b.YMin,-96.75-1e-5)
            self.assertLessEqual(b.YMax,96.75+1e-5)
            self.assertLessEqual(b.ZMax,108.75+1e-5)

    def test_full_s1_not_just_case_sets_lower_plane_and_carrier_avoids_control(self):
        parts,groups,_,f=proposal(fast_inputs(),True,True,True)
        s1=[s for n,s in parts.items() if groups[n]=='S1']
        self.assertAlmostEqual(min(s.optimalBoundingBox().ZMin for s in s1),39.77)
        self.assertFalse(f['reuse_original_S1_pose'])
        root=f['shared_fore_units']['PWM_changed_root']
        self.assertEqual(root['own_failures'],[])
        self.assertAlmostEqual(root['named_R1_R2_full_case_gap_mm'][1]-root['named_R1_R2_full_case_gap_mm'][0],9)
        self.assertEqual(len(parts['ShelfPWM:carrier'].Solids),1)
        self.assertTrue(parts['ShelfPWM:carrier'].isValid())
        self.assertEqual(f['shared_fore_units']['PiUSB_changed_profile']['status'],
                         'OWNED_BAYS_PROFILE_CLEAR_EXTERNAL_WORLD_STILL_OPEN')


if __name__=='__main__':unittest.main()
