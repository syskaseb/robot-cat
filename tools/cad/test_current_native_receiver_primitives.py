import json,unittest
import FreeCAD as A
from plan_body36_receiver_space import P
from current_native_receiver_primitives import Construction


class CurrentReceiverPrimitivesTest(unittest.TestCase):
    def test_triple_and_bolted_halves_match_and_bore_parameter_restores(self):
        selection=json.loads((P.OUT/'receiver-joint-selection.json').read_text())
        domains=json.loads((P.ROOT/selection['domain_receipt']).read_text())['qualified_options']
        doc=A.newDocument('CurrentReceiverPrimitiveFixture');parts=[]
        try:
            par=doc.addObject('App::VarSet','ReceiverParameters')
            par.addProperty('App::PropertyLength','ArmThickness');par.ArmThickness=4
            par.addProperty('App::PropertyLength','CoreBoreRadius');par.CoreBoreRadius=1.3
            ops=Construction(doc)
            for name in ('D_RL','RR_G'):
                record=domains[name][selection['selected_options'][name]]
                for cap in (False,True):
                    obj,expected=ops.triple(record,name+('Cap' if cap else 'Body'),cap)
                    s=obj.Shape;self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1)
                    self.assertFalse(s.check(True))
                    self.assertLess(max(s.cut(expected).Volume,expected.cut(s).Volume),1e-4)
                    parts.append((obj,s.Volume))
            par.CoreBoreRadius=1.4;doc.recompute()
            for obj,v in parts:self.assertLess(obj.Shape.Volume,v)
            par.CoreBoreRadius=1.3;doc.recompute()
            for obj,v in parts:self.assertAlmostEqual(obj.Shape.Volume,v,places=4)
            self.assertTrue(all(o.FullyConstrained for o in doc.Objects if o.TypeId=='Sketcher::SketchObject'))
        finally:A.closeDocument(doc.Name)


if __name__=='__main__':unittest.main()
