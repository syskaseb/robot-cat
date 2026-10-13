"""The actual FreeCAD batch-copy contract, before a large assembly copy."""
import unittest
import FreeCAD as A
from build_fixed_head_interface import add_box

class NativeDependencyCopy(unittest.TestCase):
    def test_parameter_and_body_share_one_copied_dependency(self):
        src=A.newDocument('BatchCopySource');dst=A.newDocument('BatchCopyDestination')
        try:
            par=src.addObject('App::VarSet','HeadInterfaceParameters')
            par.addProperty('App::PropertyLength','NorthRailThickness');par.NorthRailThickness=3
            body=src.addObject('PartDesign::Body','Support')
            add_box(src,body,'Rail',[0,0,0,2,2,3],expression='HeadInterfaceParameters.NorthRailThickness')
            cp,cb=dst.copyObject([par,body],True);dst.recompute()
            self.assertEqual(sum('NorthRailThickness' in o.PropertiesList for o in dst.Objects),1)
            self.assertAlmostEqual(cb.Shape.Volume,12)
            cp.NorthRailThickness=3.2;dst.recompute()
            self.assertAlmostEqual(cb.Shape.Volume,12.8)
            self.assertAlmostEqual(body.Shape.Volume,12)
        finally:
            A.closeDocument(dst.Name);A.closeDocument(src.Name)

if __name__=='__main__':unittest.main()
