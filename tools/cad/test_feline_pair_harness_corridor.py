import json,unittest,zipfile,hashlib
import numpy as np
from plan_feline_pair_harness_corridor import add_jacket
from plan_feline_layout import OUT
import feline_tangent_routes as ft
from check_main_p0_placement import ROOT,sha


class HarnessCorridorTests(unittest.TestCase):
    def test_rejected_portals_replay_real_intersections(self):
        import FreeCAD
        import Part
        from receive_feline_W024_shared_body import solid
        folder=OUT/'W009-W069-harness-corridor'
        context=json.loads((folder/'recovered-context.json').read_text())
        records={r['name']:r for r in context['geometry']}
        recipes=json.loads((folder/'W009-saved-portals.json').read_text())['proposals']
        with zipfile.ZipFile(ROOT/context['bundle']) as z:
            for heading,target in [(4,'CurrentMiddle:W024'),(2,'Station:Bank:W047/body/end:wire:W047/body/end')]:
                row=records[target];raw=z.read(row['entry'])
                self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
                obstacle=Part.Shape();obstacle.importBrepFromString(raw.decode())
                recipe=next(r for r in recipes if r['end_heading']==heading)
                actor=solid(recipe['parts'],recipe['radius_mm'])
                self.assertGreater(actor.common(obstacle).Volume,1e-5)
            proof=json.loads((folder/'W009-overpass-rejection.json').read_text())
            row=records[proof['target']];raw=z.read(row['entry'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
            obstacle=Part.Shape();obstacle.importBrepFromString(raw.decode())
            actor=solid(proof['parts'],proof['radius_mm'])
            self.assertAlmostEqual(actor.common(obstacle).Volume,proof['common_mm3'],places=5)

    def test_saved_pair_reopens_as_two_valid_solids_without_claiming_N01(self):
        import FreeCAD
        import Part
        packet=json.loads((OUT/'W009-W069-harness-corridor/pair-outline.json').read_text())
        self.assertFalse(packet['N01_complete']);self.assertFalse(packet['physical_pass'])
        self.assertEqual(sha(ROOT/packet['bundle']),packet['bundle_sha256'])
        for path,digest in packet['source_sha256'].items():self.assertEqual(sha(ROOT/path),digest)
        with zipfile.ZipFile(ROOT/packet['bundle']) as z:
            for row in packet['geometry']:
                raw=z.read(row['entry']);self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
                s=Part.Shape();s.importBrepFromString(raw.decode())
                self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1)
                self.assertGreater(s.Volume,0)

    def test_later_jacket_blocks_and_never_increases_room(self):
        room=np.full((31,31,31),20.);origin=np.array([-15.,-15.,-15.])
        add_jacket(room,origin,dict(parts=[ft.line([-5,0,0],[5,0,0])],radius_mm=1.))
        self.assertLess(room[15,15,15],0)
        self.assertLess(room[15,18,15],1.55)
        self.assertTrue((room<=20).all())
        self.assertEqual(room[0,0,0],20)

    def test_saved_proposals_keep_tangency_and_minimum_radius(self):
        folder=OUT/'W009-W069-harness-corridor'
        recipes=json.loads((folder/'W009-saved-portals.json').read_text())['proposals']
        recipes=recipes+[json.loads((folder/'pair-preflight.json').read_text())['paths']['W069/body']]
        for recipe in recipes:
            parts=recipe['parts'];self.assertGreaterEqual(ft.min_radius(parts),12.4-1e-6)
            self.assertAlmostEqual(ft.length(parts),recipe['length_mm'],places=5)
            for a,b in zip(parts,parts[1:]):
                self.assertLess(ft.norm(ft.sub(a['end'],b['start'])),1e-6)
                ta=a['end_tangent'] if a['kind']=='arc' else ft.unit(ft.sub(a['end'],a['start']))
                tb=b['tangent'] if b['kind']=='arc' else ft.unit(ft.sub(b['end'],b['start']))
                self.assertLess(ft.norm(ft.sub(ta,tb)),1e-6)


if __name__=='__main__':unittest.main()
