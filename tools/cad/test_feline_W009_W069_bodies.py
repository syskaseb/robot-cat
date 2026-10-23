import hashlib
import json
import unittest
import zipfile
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from compose_feline_current_body_routes import current, parent
from receive_feline_W009_W069_bodies import STATUS


class ReceivedBodies(unittest.TestCase):
    def test_reopen_current_caps_and_preserved_register(self):
        _, before, _ = parent(); _, after, _ = current()
        self.assertEqual([e['id'] for e in before], [e['id'] for e in after])
        self.assertEqual(len(after), 246)
        received = {e['portion_id'] for e in after if e.get('full_middle_route_accepted')}
        self.assertEqual(len(received),25)
        for wire, expected in [('W009',636.4129719628785),('W069',572.5710029278885)]:
            p=json.loads((OUT/('n01-current-'+wire+'-complete-body-plan.json')).read_text())
            self.assertEqual(p['status'],STATUS)
            self.assertEqual(sha(ROOT/p['bundle']),p['bundle_sha256'])
            for path,h in p['source_sha256'].items(): self.assertEqual(sha(ROOT/path),h,path)
            self.assertAlmostEqual(p['complete_body_length_mm'],expected)
            self.assertTrue(all(r['ok'] for r in p['checks'].values()))
            shapes={}
            with zipfile.ZipFile(ROOT/p['bundle']) as z:
                for r in p['geometry']:
                    raw=z.read(r['entry']);self.assertEqual(hashlib.sha256(raw).hexdigest(),r['sha256'])
                    s=Part.Shape();s.importBrepFromString(raw.decode())
                    self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1);shapes[r['name']]=s
            for owner, end in zip(p['source_prefix_owners'],p['current_boundaries']):
                faces=[f for f in shapes[owner].Faces if type(f.Surface).__name__=='Plane'
                       and (f.CenterOfMass-A.Vector(*end['point_mm'])).Length<1e-6]
                self.assertEqual(len(faces),1)
                row=next(e for e in after if e['id']==end['id'])
                self.assertTrue(row['whole_portion_received'])
                self.assertTrue(row['whole_factory900_and_moving_portion_NOT_received'])
            self.assertFalse(p['N01_complete']);self.assertFalse(p['physical_pass'])
            self.assertFalse(p['legacy_cache_hash_identity_recovered'])


if __name__=='__main__': unittest.main()
