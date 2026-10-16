import unittest
from compose_phase1_print_set import identity,put,HORN


class PrintIdentityTests(unittest.TestCase):
    def test_physical_plate_aliases(self):
        self.assertEqual(identity(dict(identity='CP2:LowerCarrier')),'LowerCarrier001')
        self.assertEqual(identity(dict(part='FoundationStationSupports')),'Foundation')
        self.assertEqual(identity(dict(path='module/Foundation_current_x1.stl')),'Foundation')
        self.assertEqual(identity(dict(part='UpperCarrier001',identity='CP2:UpperCarrier')),'UpperCarrier001')
    def test_horn_allocations_sum_but_plates_replace(self):
        p={};old=[];r=dict(identity=HORN,path='horn.stl',sha256='same',quantity=2)
        put(p,r,'head',old);put(p,dict(r,quantity=1),'tail',old);self.assertEqual(p[HORN]['quantity'],3)
        put(p,dict(part='UpperCarrier',path='old.stl',sha256='old',quantity=1),'M5',old)
        put(p,dict(part='UpperCarrier001',path='new.stl',sha256='new',quantity=1),'W5',old)
        self.assertEqual(p['UpperCarrier001']['quantity'],1);self.assertEqual(len(old),1)
    def test_ambiguous_identity_is_rejected(self):
        with self.assertRaises(AssertionError):identity(dict(path='unknown_current_x4.stl'))


if __name__=='__main__':unittest.main()
