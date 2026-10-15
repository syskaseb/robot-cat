import unittest
import FreeCAD as A
from plan_g1_rooted_carrier import geometry,PORTS

class G1CarrierTests(unittest.TestCase):
    def test_whole_open_web_preserves_real_xa06_clearance(self):
        import zipfile
        import Part
        from plan_body36_receiver_space import P
        body,bands,recipe=geometry(direct_upper=True,upper_portal=True,open_web=True)
        with zipfile.ZipFile(P.OUT.parent/'current-view-60-20261012.zip') as z:
            wire=Part.Shape();wire.importBrepFromString(z.read('wire0007.brep').decode())
        self.assertGreaterEqual(min(body.distToShape(e)[0] for e in wire.Edges),1.5-1e-6)
        self.assertTrue(recipe['open_web'])
        self.assertTrue(all(r['bridge_mm'][2]==173 for r in recipe['lands']))
        for band in bands.values():self.assertLess(body.common(band).Volume,1e-6)

    def test_portal_foot_in_actual_saved_native_material(self):
        from check_main_p0_placement import SavedShapes
        from plan_body36_receiver_space import P
        from loom_land_port import box
        path=P.OUT/'U1InterfaceCarriersCurrent.FCStd'
        self.assertEqual(P.SHA(path),'fd09de30744aa0ea26bad789779980172ee078b650ae80070729254ee259e9c1')
        parent=SavedShapes().shape(path,'UpperCarrier001')
        self.assertLess(box([-58,-24,76.72,-54,-20,77.72]).cut(parent).Volume,1e-6)

    def test_upper_portal_avoids_known_tail_fuse_and_aux_wire_corridors(self):
        from loom_land_port import box
        import Part
        body,bands,recipe=geometry(direct_upper=True,upper_portal=True)
        self.assertEqual(recipe['root_path_mm'][0],[-56,-22,76.72])
        self.assertEqual(recipe['pads'][1]['bounds_mm'][1:2],[-38.5])
        case=box([-61,-52,89.99,-10,-31.75,111.99])
        self.assertLess(body.common(case).Volume,1e-6)
        # Known fixed head supply run below the portal, not a clearance
        # claim for the whole moving head or the rest of the scene.
        xs23=Part.makeCylinder(1.05,180,A.Vector(-116.6,-27.6,79.2),A.Vector(1,0,0))
        self.assertLess(body.common(xs23).Volume,1e-6)
        self.assertEqual(len(body.Solids),1)

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
