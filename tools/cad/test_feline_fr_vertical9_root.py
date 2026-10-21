import hashlib,json,unittest,zipfile
import FreeCAD
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_n01_shared import pipe
from plan_feline_vertical_cuff_bays import root_front_right


class FrontRight(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=json.loads((OUT/'n01-FR-vertical9-rooted-space.json').read_text())
        p=cls.packet;assert sha(ROOT/p['bundle'])==p['bundle_sha256'];cls.shapes={}
        with zipfile.ZipFile(ROOT/p['bundle']) as z:
            for row in p['geometry']:
                data=z.read(row['entry']);assert hashlib.sha256(data).hexdigest()==row['sha256']
                s=Part.Shape();s.importBrepFromString(data.decode());cls.shapes[row['name']]=s
        assert len(cls.shapes)==14

    def test_full_nine_current_sources_not_supplier_or_whole_motion_pass(self):
        p=self.packet;self.assertEqual(len(p['source_recipes']),9)
        for n,r in p['source_recipes'].items():
            self.assertEqual(r['leg'],'FR');self.assertEqual(r['new_axis'],[0.,0.,1.])
            self.assertEqual(r['parts'][0]['length_mm'],9.)
            self.assertGreaterEqual(r['parts'][1]['radius_mm'],12.4-1e-6)
            rebuilt=pipe(r['parts'],r['radius_mm']);old=self.shapes[n]
            self.assertAlmostEqual(rebuilt.Volume,old.Volume,places=5)
            self.assertAlmostEqual(rebuilt.common(old).Volume,old.Volume,places=5)
        self.assertFalse(p['N01_complete']);self.assertFalse(p['physical_pass'])
        self.assertTrue(p['full_moving_wire_and_head_tail_motion_NOT_received'])
        self.assertGreaterEqual(p['sampled36_leg_vertical_separation_lower_bound_mm'],1.25)
        self.assertGreaterEqual(p['restored_bbox_separation_lower_bound_mm'],1.25)
        self.assertTrue(all(r['ok'] for r in p['checks'].values()))

    def test_root_rebuild_is_single_print_and_inputs_are_immutable(self):
        inputs=[self.shapes[n] for n in ('Input:unrooted_guide','Input:parent')]
        before=[s.exportBrepToString() for s in inputs]
        rebuilt,joint=root_front_right(*inputs)
        self.assertEqual(before,[s.exportBrepToString() for s in inputs])
        self.assertGreaterEqual(joint['guide_bridge_common_mm3'],8-1e-5)
        self.assertGreaterEqual(joint['parent_bridge_common_mm3'],8-1e-5)
        received=self.shapes['VerticalGuide:FR']
        self.assertAlmostEqual(rebuilt.Volume,received.Volume,places=5)
        self.assertAlmostEqual(rebuilt.common(received).Volume,received.Volume,places=5)
        self.assertLess(max(self.packet['rooted_shared_print_envelope_mm']),250)


if __name__=='__main__':unittest.main()
