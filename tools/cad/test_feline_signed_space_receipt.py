"""Integrity of the completed proposal artifact, never CAD/PASS or N01."""
import ast,hashlib,io,json,subprocess,unittest,zipfile
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT


class SignedSpaceReceipt(unittest.TestCase):
    def test_current_layers_complete_and_not_geometry_acceptance(self):
        d=json.loads((OUT/'n01-current-signed-space.json').read_text())
        self.assertEqual(d['status'],'CURRENT_SIGNED_CLOSED_VOLUME_SPACE_PROPOSALS_ONLY')
        self.assertEqual(d['layer_checkpoint']['motion_count'],3888)
        self.assertEqual(len(set(d['layer_checkpoint']['static_names'])),1240)
        self.assertFalse(d['errors']);self.assertFalse(d['N01_complete']);self.assertFalse(d['selected']);self.assertFalse(d['physical_pass'])
        self.assertTrue(d['closed_volume_fill']);self.assertTrue(d['surface_only_voids_are_not_free'])
        for p,h in ((d['field'],d['field_sha256']),(d['voxel_source_archive'],d['voxel_source_archive_sha256']),
                    (d['layer_checkpoint']['file'],d['layer_checkpoint']['sha256'])):
            self.assertEqual(sha(ROOT/p),h,p)
        for p in ('tools/cad/build_feline_current_signed_space.py','tools/cad/feline_signed_voxels.py','tools/cad/feline_common_space_context.py'):
            if p=='tools/cad/build_feline_current_signed_space.py' and sha(ROOT/p)!=d['source_sha256'][p]:
                old=subprocess.check_output(['git','show','30453cb5:'+p],cwd=ROOT)
                self.assertEqual(hashlib.sha256(old).hexdigest(),d['source_sha256'][p])
                def main_ast(source):return ast.dump(next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='main'),include_attributes=False)
                self.assertEqual(main_ast(old),main_ast((ROOT/p).read_text()))
            else:self.assertEqual(sha(ROOT/p),d['source_sha256'][p],p)
        self.assertEqual(d['source_sha256']['hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/phase1-whole-assembly/RobotCatPhase1Current.FCStd'],
            'aff0a45bfc4bb430179e80d8e9b4267dc4727a7bb93cadb9c9083911d3d6d4ee')

    def test_two_fore_units_change_only_their_cached_cells(self):
        from feline_signed_voxels import deposit
        old=json.loads((OUT/'n01-current-signed-space.json').read_text())
        new=json.loads((OUT/'n01-two-fore-lower-deck-signed-space.json').read_text())
        gate=json.loads((OUT/'n01-usb-fore-lower-deck-space.json').read_text())
        self.assertEqual(new['translated_sources'],16);self.assertEqual(new['retessellated_sources'],0)
        self.assertFalse(gate['failures']);self.assertFalse(gate['errors'])
        self.assertFalse(new['N01_complete']);self.assertFalse(new['selected']);self.assertFalse(new['physical_pass'])
        self.assertEqual(sha(ROOT/new['field']),new['field_sha256'])
        with np.load(ROOT/old['field'],allow_pickle=False) as a,np.load(ROOT/new['field'],allow_pickle=False) as b:
            for key in ('origin_mm','grid_mm','motion36_occupied','motion36_signed_distance','outer_distance','inside'):
                self.assertTrue(np.array_equal(a[key],b[key]),key)
            allowed=np.zeros_like(a['rigid_occupied'])
            with zipfile.ZipFile(ROOT/old['voxel_source_archive']) as z:
                for name in gate['changed_owners']:
                    row=old['parts']['Static:'+name];raw=z.read(row['entry'])
                    self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256'])
                    with np.load(io.BytesIO(raw),allow_pickle=False) as f:
                        for delta in (0,-8):deposit(allowed,f['occupied'],f['origin']+np.array([0,0,delta]),a['origin_mm'])
            change=a['rigid_occupied']^b['rigid_occupied'];self.assertTrue(change.any())
            self.assertFalse(np.any(change&~allowed))
            self.assertTrue(np.all(b['harness_occupied'][a['harness_occupied']]))


if __name__=='__main__':unittest.main()
