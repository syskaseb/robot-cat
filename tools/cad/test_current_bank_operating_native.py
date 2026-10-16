import json,unittest
import FreeCAD as A
import Part
from current_native_receiver_primitives import Construction
from current_bank_operating_native import rail_parts,bank_seat,equal,case_backer
from plan_current_harness_interfaces import OUT
from plan_individual_bank_seats import seats


class OperatingNativeTests(unittest.TestCase):
    def test_rail_has_editable_drilled_bosses_and_true_source_grips(self):
        d=A.newDocument('OperatingRailPrimitiveTest')
        try:
            ops=Construction(d);plan=json.loads((OUT/'bank-prototype-service-plan.json').read_text())
            rail,bosses,q=rail_parts(ops,plan)
            for obj in [rail,*bosses.values()]:
                self.assertTrue(obj.Shape.isValid());self.assertEqual(len(obj.Shape.Solids),1);self.assertFalse(obj.Shape.check(True))
            self.assertGreater(ops.sketches,20)
        finally:A.closeDocument(d.Name)

    def test_native_relief_seat_preserves_catalog_hole(self):
        d=A.newDocument('OperatingBankSeatTest')
        try:
            q=seats([dict(id='F_R6_CP2',centre_xy_mm=[107,-62],flange_top_z_mm=126)],True)['F_R6_CP2']
            obj=bank_seat(Construction(d),q['recipe'],'BankR6');equal(obj.Shape,q['body'],'R6 seat native')
        finally:A.closeDocument(d.Name)


if __name__=='__main__':unittest.main()
