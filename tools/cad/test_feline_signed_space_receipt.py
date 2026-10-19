"""Integrity of the completed proposal artifact, never CAD/PASS or N01."""
import json,unittest
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
            self.assertEqual(sha(ROOT/p),d['source_sha256'][p],p)
        self.assertEqual(d['source_sha256']['hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/phase1-whole-assembly/RobotCatPhase1Current.FCStd'],
            'aff0a45bfc4bb430179e80d8e9b4267dc4727a7bb93cadb9c9083911d3d6d4ee')


if __name__=='__main__':unittest.main()
