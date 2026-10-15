import unittest
import FreeCAD as A
from plan_g1_rooted_carrier import geometry,PORTS

class G1CarrierTests(unittest.TestCase):
    def test_direct_upper_load_path_is_one_connected_body(self):
        body,bands,recipe=geometry(direct_upper=True)
        self.assertEqual(len(body.Solids),1)
        self.assertTrue(body.isValid())
        self.assertEqual(recipe['root_path_mm'][0],[-16,-30,76.72])
        self.assertTrue(recipe['direct_upper'])
        for band in bands.values():self.assertLess(body.common(band).Volume,1e-6)

    def test_one_rooted_design_five_independent_lands(self):
        body,bands,recipe=geometry()
        self.assertEqual(len(body.Solids),1)
        self.assertEqual(len(bands),5)
        for n,b in bands.items():
            self.assertLess(body.common(b).Volume,1e-6,n)
            for m,c in bands.items():
                if n!=m:self.assertLess(b.common(c).Volume,1e-6,(n,m))
        for row in recipe['lands']:
            self.assertEqual(row['land_mm'],3)
            self.assertEqual(row['centre_mm'][2],170.5)
        self.assertLess(body.BoundBox.XLength+10,256)
        self.assertLess(body.BoundBox.YLength+10,256)
        self.assertLess(body.BoundBox.ZLength+10,256)

    def test_mouth_lands_do_not_move_bought_ports(self):
        _,bands,_=geometry()
        for name,x,r in PORTS:
            # Exact nominal jacket cylinder over the actual first3mm UP.
            import Part
            wire=Part.makeCylinder(r,3,A.Vector(x,-54,169))
            self.assertLess(bands[name].common(wire).Volume,1e-6,name)

if __name__=='__main__':unittest.main()
