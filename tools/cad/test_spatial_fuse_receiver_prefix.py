import json,unittest
from spatial_fuse_receiver_prefix import build
from current_body_fanout_material import B,P
from open_prototype_head_preflight import MOUNT
from plan_continuous_joint_family import self_screen


class SpatialFusePrefixTest(unittest.TestCase):
    def test_real_spacer_and_retained_complete_wire_are_clear(self):
        contract=json.loads((P.OUT/'body36-current-contract.json').read_text())
        original=next(r for r in contract['rows'] if r['wire']=='W022');q=build(original)
        reader=B.H.P.SavedShapes();spacer=reader.shape(MOUNT,'Spacer2')
        path=P.wire(q['receiving_parts']);other=P.wire(contract['inherited_routes']['W024']['parts'])
        power=json.loads((P.OUT/'u1-power-grips-native.json').read_text());model=P.ROOT/power['native']
        assert P.SHA(model)==power['native_sha256']
        for name in ('LowerCarrier001','MAINGrip'):
            self.assertGreaterEqual(path.distToShape(reader.shape(model,name))[0],1.25,name)
        self.assertGreaterEqual(path.distToShape(spacer)[0],1.25)
        self.assertGreaterEqual(path.distToShape(other)[0],2.25)
        self.assertEqual(q['receiving_land']['start'],[-23.0,36.0,56.402])
        self.assertEqual(q['receiving_land']['end'],[-23.0,45.0,56.402])
        self.assertIsNone(self_screen(q['receiving_parts']))
        self.assertTrue(all(p.get('radius_mm',10)>=10 for p in q['receiving_parts']))


if __name__=='__main__':unittest.main()
