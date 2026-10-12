import unittest
from unittest.mock import patch
import FreeCAD as A
import Part
import check_u1_current_service as S


class CurrentServiceTests(unittest.TestCase):
    def gate(self):
        return dict(pairs=372,errors=[],contacts=[dict(a='Bar',b='W003')],
                    reservation_resolutions=[dict(a='C1',b='W003')],source_sha256={})

    def test_no_other_old_contact_can_be_waived(self):
        g=self.gate();S.prior_gate(g)
        g['contacts'].append(dict(a='Bar',b='W002'))
        with self.assertRaises(AssertionError):S.prior_gate(g)

    def test_inherited_errors_and_changed_pins_fail(self):
        g=self.gate();g['errors']=['invalid BRep']
        with self.assertRaises(AssertionError):S.prior_gate(g)
        g=self.gate();g['source_sha256']={'dummy':'a'}
        with patch.object(S,'SHA',return_value='b'):
            with self.assertRaises(AssertionError):S.prior_gate(g)

    def test_continuous_prismatic_sweep_not_just_two_poses(self):
        s=Part.makeBox(2,3,1,A.Vector(10,20,30));sweep=S.sweep(s)
        self.assertAlmostEqual(sweep.Volume,2*3*13)
        self.assertEqual(len(sweep.Solids),1)
        self.assertAlmostEqual(sweep.BoundBox.ZMin,30)
        self.assertAlmostEqual(sweep.BoundBox.ZMax,43)


if __name__=='__main__':unittest.main()
