"""Receipt invariants, not repeated raster/CAD/primitive searches."""
import hashlib,json,unittest
from pathlib import Path
import numpy as np
from scipy.sparse import load_npz
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'


class ReceivedDelta(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.field=json.loads((OUT/'n01-cuff-space-delta.json').read_text())
        cls.graph=json.loads((OUT/'n01-cuff-corridor-topology.json').read_text())

    def test_field_scope(self):
        r=self.field
        self.assertEqual(r['status'],'CURRENT_CUFF_OWNER_SPACE_DELTA_RECEIVED_PROPOSALS_ONLY')
        self.assertEqual(r['changed_owners_rasterized'],35)
        self.assertEqual(r['unchanged_source_caches_reused'],1204)
        self.assertTrue(r['motion3888_outer_and_inside_fields_unchanged'])
        self.assertFalse(r['N01_complete'])

    def test_receipt_bytes(self):
        for r,keys in [(self.field,['field','inherited_fields','voxel_source_archive'])]:
            for k in keys:self.assertEqual(hashlib.sha256((ROOT/r[k]).read_bytes()).hexdigest(),r[k+'_sha256'])

    def test_filters_do_not_invent_arcs(self):
        self.assertEqual(len(self.graph['classes']),6)
        self.assertFalse(self.graph['N01_complete'])
        for r in self.graph['classes'].values():
            self.assertEqual(r['parent_primitives'],r['reused_primitives']+r['removed_by_changed_space'])
            self.assertTrue(r['existing_constructive_arcs_not_regenerated'])
            for k in ['nodes','graph']:
                self.assertEqual(hashlib.sha256((ROOT/r[k]).read_bytes()).hexdigest(),r[k+'_sha256'])
            g=load_npz(ROOT/r['graph'])
            with np.load(ROOT/r['nodes'],allow_pickle=False) as n:
                self.assertEqual(g.shape[0],len(n['component']))
                self.assertEqual(g.nnz,r['primitives'])
                self.assertEqual(int(n['step_mm']),4)


if __name__=='__main__':unittest.main()
