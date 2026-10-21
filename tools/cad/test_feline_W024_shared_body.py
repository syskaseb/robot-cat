import hashlib,json,unittest,zipfile
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_joint_usb_route import wire
from plan_feline_FL_three_core_shared_trunk import construct,transport
from receive_feline_W024_shared_body import solid
from compose_feline_current_body_routes import current


class SharedBody(unittest.TestCase):
    def test_fresh_circles_whole_body_and_delta_motion_scope(self):
        p=json.loads((OUT/'n01-current-W024-shared-complete-body-plan.json').read_text())
        base=json.loads((OUT/'n01-current-W022-complete-body-plan.json').read_text())
        self.assertEqual(sha(ROOT/p['bundle']),p['bundle_sha256'])
        trunk,offset=transport(base['middle_recipe']['parts'][:13],[0,0,2.2])
        self.assertAlmostEqual(np.linalg.norm(offset),2.2)
        for a,b in zip(base['middle_recipe']['parts'][:13],trunk):
            self.assertAlmostEqual(np.linalg.norm(np.asarray(a['start'])-b['start']),2.2)
            self.assertAlmostEqual(np.linalg.norm(np.asarray(a['end'])-b['end']),2.2)
        fresh=solid(p['middle_recipe']['parts'],1.)
        with zipfile.ZipFile(ROOT/p['bundle']) as z:
            r=next(g for g in p['geometry'] if g['name']=='CurrentMiddle:W024');raw=z.read(r['entry'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(),r['sha256']);saved=Part.Shape();saved.importBrepFromString(raw.decode())
        self.assertAlmostEqual(fresh.Volume,saved.Volume,places=5)
        self.assertAlmostEqual(fresh.common(saved).Volume,saved.Volume,places=4)
        counts=p['motion_counts'];self.assertEqual(sum(counts[k] for k in ('trunk_prior_exact_bound','trunk_bbox_bound','trunk_new_exact')),3888)
        self.assertEqual(counts['branch_bbox_bound']+counts['branch_new_exact'],3888)
        self.assertEqual(counts['trunk_new_exact'],3);self.assertEqual(counts['trunk_prior_exact_bound'],144)
        self.assertTrue(all(r['ok'] for r in p['motion_new_exact'].values()))
        self.assertGreaterEqual(min(p['motion_trunk_minimum_bound_mm'],p['motion_branch_minimum_bound_mm']),1.25-1e-6)
        self.assertFalse(p['N01_complete']);self.assertEqual(len(p['preserved_W020_rejections']),2)
        _,rows,_=current()
        self.assertTrue(all(e['full_middle_route_accepted'] for e in rows if e['portion_id']=='W024/body'))
        self.assertTrue(all(e.get('full_middle_route_accepted') for e in rows if e['portion_id']=='W020/body'))


if __name__=='__main__':unittest.main()
