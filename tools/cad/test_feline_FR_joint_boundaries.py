"""The three accepted body portions do not imply N01 or factory loom acceptance."""
import FreeCAD
import json,unittest
from compose_feline_FR_joint_boundaries import current,parent
from plan_feline_layout import OUT
from check_main_p0_placement import ROOT,sha


class CommonFR(unittest.TestCase):
    def test_whole_portions_and_unchanged_identity(self):
        _,rows,_=current();_,old,_=parent()
        complete=lambda rr:{r['portion_id'] for r in rr if r.get('full_middle_route_accepted')}
        self.assertEqual(complete(rows)-complete(old),{'W031/body','W033/body','W035/body'})
        self.assertEqual(len(complete(rows)),29)
        self.assertEqual(len(rows),246)
        r=json.loads((OUT/'n01-FR-W031-W033-common-body-plan.json').read_text())
        self.assertFalse(r['N01_complete']);self.assertFalse(r['physical_pass'])
        self.assertTrue(r['root_assembly_compression_and_full_factory_lengths_OPEN'])
        self.assertEqual(sha(ROOT/r['bundle']),r['bundle_sha256'])
        for e in rows:
            if e['id'] in r['updates']:self.assertTrue(e['whole_portion_received'])


if __name__=='__main__':unittest.main()
