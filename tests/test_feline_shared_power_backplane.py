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


if __name__=='__main__':unittest.main()
