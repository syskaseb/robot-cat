"""Whole source allocations are proposals, never native/N01 acceptance."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from feline_fore_core_and_source_fans import allocation,named_parent,shared_root


class SharedSourceSpace(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src,cls.doc,cls.parts,cls.rows,cls.mouths,cls.choices,cls.facts=allocation()

    def test_six_actual_mouths_keep_bought_parts_and_curvature(self):
        self.assertEqual(len(self.mouths),6)
        self.assertTrue(all(self.choices.values()))
        self.assertEqual(self.facts['coupled_S0_translation_mm'],[0,0,0])
        self.assertEqual(sum(r['group']=='S1' for r in self.rows.values()),10)
        for choices in self.choices.values():
            for row in choices:
                self.assertEqual(row['R_mm'],25.2);self.assertEqual(row['full_grip_mm'],9)
                self.assertEqual(row['jacket_radius_mm'],2.1)

    def test_root_uses_actual_rim_and_full_two_mm_parent_face(self):
        parent,pin=named_parent();old=self.parts['BundleCuff:FR'];volume=old.Volume
        new,relation=shared_root(old,parent,self.parts['BundleTie:FR'])
        self.assertTrue(new.isValid());self.assertEqual(len(new.Solids),1)
        self.assertAlmostEqual(new.common(parent).Volume,33)
        self.assertAlmostEqual(relation['actual_rim_face_area_mm2'],18)
        self.assertGreater(relation['full_strap_clearance']['previous_positive_common_mm3'],0)
        self.assertLess(relation['full_strap_clearance']['current_positive_common_mm3'],1e-5)
        self.assertAlmostEqual(old.Volume,volume)
        self.assertFalse(relation['physical_pass'])

    def test_new_frame_addition_preserves_all_nine_jackets_and_strap_slot(self):
        parent,_=named_parent();old=self.parts['BundleCuff:FR'];new,_=shared_root(old,parent,self.parts['BundleTie:FR'])
        delta=new.cut(old)
        for name,shape in self.parts.items():
            if self.rows[name]['group']!='FRBodyReceiver' or name=='BundleCuff:FR':continue
            self.assertLess(new.common(shape).Volume,1e-5,name)
            self.assertGreater(delta.distToShape(shape)[0],.25,name)


if __name__=='__main__':unittest.main()
