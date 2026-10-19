"""Routing boundary changes are not changed electrical terminals/SKUs."""
import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from feline_fore_receiver_integration import inputs,proposal


class ForeReceivers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.world=inputs();cls.parts,cls.groups,cls.kinds,cls.plan=proposal(cls.world)

    def test_nine_full_OD3p1_jackets_and_continuity_points_preserved(self):
        rows=self.plan['FR_accounting_boundary_changes']
        self.assertEqual(len(rows),9)
        self.assertEqual(len({r['id'] for r in rows}),9)
        for r in rows:
            self.assertEqual(r['delta_mm'],[0,20,0])
            self.assertFalse(r['new_connector_or_splice'])
            self.assertAlmostEqual(self.parts['End:'+r['id']].Volume,math.pi*1.55**2*9)
        self.assertTrue(self.plan['source_factory_4MTA_parts_and_both_sides_unchanged'])

    def test_all_nine_lands_clear_the_new_cuff(self):
        cuff=self.parts['BundleCuff:FR']
        self.assertTrue(cuff.isValid());self.assertEqual(len(cuff.Solids),1)
        for r in self.plan['FR_accounting_boundary_changes']:
            common=cuff.common(self.parts['End:'+r['id']])
            self.assertLess(common.Volume,1e-5)

    def test_upper_deck_is_a_whole_subset_with_first_housing_supported(self):
        old=self.world.parts['StructureReserve:BankBed-1'];new=self.parts['StructureReserve:BankBed-1']
        self.assertLess(new.cut(old).Volume,1e-5)
        self.assertAlmostEqual(new.BoundBox.XMin,-43.75)
        self.assertAlmostEqual(new.BoundBox.ZLength,3)
        self.assertFalse(self.plan['N01_complete']);self.assertFalse(self.plan['physical_pass'])

    def test_supported_receiver_has_full_side_bond_and_all_nine_clear_lands(self):
        parts,groups,kinds,plan=proposal(self.world,True)
        self.assertEqual(plan['FR_routing_Z_from_full_mount_and_tie'],73)
        cuff=parts['BundleCuff:FR']
        self.assertTrue(cuff.isValid());self.assertEqual(len(cuff.Solids),1)
        self.assertAlmostEqual(cuff.common(self.world.parts['StructureReserve:Post-69_-1']).Volume,83.7)
        self.assertEqual(plan['FR_full_side_bond']['side_face_area_mm2'],54)
        for row in plan['FR_accounting_boundary_changes']:
            self.assertEqual(row['delta_mm'],[0,20,3])
            self.assertLess(cuff.common(parts['End:'+row['id']]).Volume,1e-5)
        head=parts['BundleTie:FLHead'];tie=self.world.parts['BundleTie:FL']
        self.assertAlmostEqual(head.Volume,100)
        self.assertGreater(head.common(tie).Volume,0)
        self.assertTrue(plan['source_factory_4MTA_parts_and_both_sides_unchanged'])


if __name__=='__main__':unittest.main()
