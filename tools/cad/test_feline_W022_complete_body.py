import hashlib,json,math,unittest,zipfile
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_joint_usb_route import wire
from compose_feline_current_body_routes import current


class WholeCurrentBody(unittest.TestCase):
    def test_fresh_whole_curve_and_two_retained_prefixes(self):
        p=json.loads((OUT/'n01-current-W022-complete-body-plan.json').read_text())
        self.assertEqual(sha(ROOT/p['bundle']),p['bundle_sha256'])
        shapes={}
        with zipfile.ZipFile(ROOT/p['bundle']) as z:
            for r in p['geometry']:
                raw=z.read(r['entry']);self.assertEqual(hashlib.sha256(raw).hexdigest(),r['sha256'])
                s=Part.Shape();s.importBrepFromString(raw.decode());self.assertTrue(s.isValid());shapes[r['name']]=s
        r=p['middle_recipe'];w=wire(r['parts']);first=w.Edges[0]
        fresh=w.makePipeShell([Part.Wire([Part.makeCircle(r['radius_mm'],first.valueAt(first.FirstParameter),first.tangentAt(first.FirstParameter))])],True,False)
        self.assertTrue(fresh.isValid());self.assertEqual(len(fresh.Solids),1)
        saved=shapes['CurrentMiddle:W022'];self.assertAlmostEqual(saved.Volume,fresh.Volume,places=5)
        common=fresh.common(saved).Volume;self.assertAlmostEqual(common,saved.Volume,places=4)
        for owner,boundary in zip(p['source_prefix_owners'],p['current_boundaries']):
            s=shapes[owner];self.assertAlmostEqual(s.Volume/math.pi,boundary['retained_prefix_length_mm'],places=4)
        self.assertAlmostEqual(p['complete_body_length_mm'],382.6575403414284,places=6)
        _,rows,_=current();ends=[e for e in rows if e['portion_id']=='W022/body']
        self.assertEqual(len(ends),2);self.assertTrue(all(e['full_middle_route_accepted'] for e in ends))
        self.assertTrue(all(e['whole_factory900_and_moving_portion_NOT_received'] for e in ends))
        self.assertFalse(p['N01_complete']);self.assertFalse(p['physical_pass'])


if __name__=='__main__':unittest.main()
