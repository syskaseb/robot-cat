import hashlib
import json
import unittest
import zipfile

import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from receive_feline_W020_complete_body import DEST,STATUS,OWNERS
from receive_feline_W024_shared_body import solid
from compose_feline_current_body_routes import current


class WholeBody(unittest.TestCase):
    def test_saved_geometry_and_current_caps(self):
        p=json.loads(DEST.read_text())
        self.assertEqual(p['status'],STATUS)
        self.assertEqual(sha(ROOT/p['bundle']),p['bundle_sha256'])
        for name,h in p['source_sha256'].items():
            self.assertEqual(sha(ROOT/name),h,name)
        saved={}
        with zipfile.ZipFile(ROOT/p['bundle']) as z:
            for r in p['geometry']:
                raw=z.read(r['entry'])
                self.assertEqual(hashlib.sha256(raw).hexdigest(),r['sha256'])
                s=Part.Shape();s.importBrepFromString(raw.decode())
                self.assertTrue(s.isValid());self.assertEqual(len(s.Solids),1)
                saved[r['name']]=s
        fresh=solid(p['middle_recipe']['parts'],p['middle_recipe']['radius_mm'])
        middle=saved['CurrentMiddle:W020']
        self.assertAlmostEqual(fresh.Volume,middle.Volume,places=5)
        self.assertAlmostEqual(fresh.common(middle).Volume,middle.Volume,places=4)
        for owner,b in zip(OWNERS,p['current_boundaries']):
            cap=[f for f in saved[owner].Faces if type(f.Surface).__name__=='Plane'
                 and (f.CenterOfMass-A.Vector(*b['point_mm'])).Length<1e-6]
            self.assertEqual(len(cap),1)
            self.assertLess(middle.distToShape(saved[owner])[0],1e-6)
        self.assertAlmostEqual(p['complete_body_length_mm'],419.8071159815733,places=6)
        self.assertEqual(len(p['checks']),118)
        self.assertTrue(all(r['ok'] for r in p['checks'].values()))
        self.assertGreaterEqual(p['outer']['gap_mm'],3.25)
        self.assertAlmostEqual(middle.BoundBox.ZMin-p['motion_maximum_z_mm'],p['motion_vertical_lower_bound_mm'])
        self.assertGreaterEqual(p['motion_vertical_lower_bound_mm'],1.25)
        self.assertEqual((p['motion_actors_covered'],p['sampled_poses']),(3888,36))
        self.assertFalse(p['N01_complete']);self.assertFalse(p['physical_pass'])
        self.assertEqual(len(p['preserved_other_candidate_failures']),3)
        _,rows,_=current()
        ends=[e for e in rows if e['portion_id']=='W020/body']
        self.assertEqual(len(ends),2)
        self.assertTrue(all(e['whole_portion_received'] for e in ends))
        self.assertTrue(all(e['whole_factory900_and_moving_portion_NOT_received'] for e in ends))
        # Earlier factory/retained receipts use full_middle_route_accepted;
        # whole_portion_received was introduced later and covers only13.
        self.assertEqual(len({e['portion_id'] for e in rows if e.get('full_middle_route_accepted')}),25)
        for e,b in zip(ends,p['current_boundaries']):
            np.testing.assert_allclose(e['routing_exit_mm'],b['point_mm'],atol=1e-7,rtol=0)


if __name__=='__main__':unittest.main()
