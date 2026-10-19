import subprocess
import sys
import unittest
from pathlib import Path
import FreeCAD
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from adopt_feline_zoned_addition import prove,HELPER
from feline_remaining_kits import candidates


class AdditiveZoneProof(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=subprocess.run(['git','show','c5f0bd35:'+HELPER],cwd=ROOT,check=True,capture_output=True).stdout
        cls.new=subprocess.run(['git','show','e6fb2794:'+HELPER],cwd=ROOT,check=True,capture_output=True).stdout.decode();cls.groups,_=candidates()

    def test_only_W029_added_all_prior_recipes_and_zone_results_identical(self):
        before,after=prove(self.old,self.new,self.groups)
        self.assertEqual(len(before),10);self.assertEqual(len(after),11)

    def test_changed_geometry_is_not_metadata_migration(self):
        with self.assertRaises(AssertionError):
            prove(self.old,self.new.replace('entry=3.;degrees=60.','entry=4.;degrees=60.'),self.groups)

    def test_changed_previous_zone_is_not_metadata_migration(self):
        with self.assertRaises(AssertionError):
            prove(self.old,self.new.replace("if group=='Bank:W020/body/end':return 'FORE_LEFT_SPLIT_BELOW_S0_KEY'", "if group=='Bank:W020/body/end':return 'CHANGED_OLD_ZONE'"),self.groups)


if __name__=='__main__':unittest.main()
