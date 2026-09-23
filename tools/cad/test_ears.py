"""Recorded E1 geometry/assembly contracts; stdlib, no CAD process."""
import json,unittest
import pilot,author_ears as task
from release_check import sha256,verify

class EarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g=json.loads((task.OUT/'module.json').read_text());cls.a=json.loads((task.OUT/'assembly.json').read_text())
        cls.m=json.loads((task.OUT/'migration.json').read_text())

    def test_source_integrity(self):
        for r,t in [(self.g,'validate_ears.py'),(self.a,'validate_ear_assembly.py')]:
            for p,h in r['file_sha256'].items():self.assertEqual(sha256(pilot.ROOT/p),h)
            self.assertEqual(r['tool_sha256'],sha256(pilot.ROOT/'tools/cad'/t))
        self.assertEqual(self.m['assembly_sha256'],sha256(task.TARGET))
        self.assertEqual(self.m['module_sha256'],sha256(task.MODULE))
        self.assertEqual(self.m['predecessor_sha256'],sha256(task.PREDECESSOR))

    def test_new_geometry_and_known_legacy_failure(self):
        for n,g in self.g['new_geometry'].items():
            self.assertTrue(g['valid']);self.assertEqual(g['solids'],1)
            if n!='RearHead':self.assertIs(g['strict_bop'],True)
        self.assertEqual(self.g['new_geometry']['RearHead']['strict_bop'],self.g['inherited_rear_head_strict_bop'])
        self.assertIsInstance(self.g['inherited_rear_head_strict_bop'],str)
        self.assertFalse(self.g['intersections']);self.assertFalse(self.a['new_intersections'])
        self.assertFalse(self.a['legacy_head_bop_passed'])

    def test_editability_and_print_envelope(self):
        self.assertEqual(len(self.g['sketches']),31)
        self.assertTrue(all(s['fully_constrained'] and s['solve']==0 for s in self.g['sketches']))
        for n in ['EarL','EarR','RearHead']:self.assertLess(max(self.g['new_geometry'][n]['bbox_mm'])+20,256)

    def test_physical_mounts(self):
        self.assertEqual(len(self.g['mounts']),4)
        for m in self.g['mounts']:
            self.assertGreater(m['head_bearing_mm2'],9);self.assertGreater(m['nut_bearing_mm2'],6)
            self.assertAlmostEqual(m['protrusion_mm'],.4)
            self.assertLess(max(m['nut_insertion_intersections_mm3']),1e-4)
            self.assertLess(m['driver_rear_shell_overlap_mm3'],1e-4)
            self.assertLess(m['front_entry_rear_shell_overlap_mm3'],1e-4)

    def test_parameter_propagation_and_sampled_restoration(self):
        self.assertEqual(len(self.g['parameters']),3)
        for p in self.g['parameters']:
            self.assertTrue(p['valid']);self.assertLess(p['restore_relative_volume_error'],2e-6)
            self.assertLess(max(p['restored_sample_distance_mm'].values()),1e-4)
            self.assertTrue(all(x is True for x in p['restored_strict_bop'].values()))
        self.assertTrue(all(v<-.001 for v in self.a['linked_hole_parameter_delta_mm3'].values()))

    def test_relocation_and_inheritance(self):
        self.assertEqual(self.a['relocated_documents'],11);self.assertEqual(len(self.a['links']),65)
        self.assertFalse(self.a['outside_dependencies']);self.assertTrue(self.a['fresh_process'])
        self.assertEqual(len(self.a['geometry_comparison']),324);self.assertEqual(self.a['unchanged_joint_frames'],324)

    def test_native_motion_and_accounting(self):
        n=self.a['native'];self.assertEqual((n['components'],n['fixed'],n['revolute'],n['temporary']),(335,321,13,25))
        self.assertEqual(len(n['frames']),22);self.assertTrue(n['restored'])
        for r in n['frames']:
            for k in ['gap_mm','fixed_rad','axis_rad','geometry_mm']:self.assertLess(r[k],1e-5)
        self.assertEqual(len(n['peaks_deg']),13);self.assertAlmostEqual(n['peaks_deg']['Rev_TailYaw29'],30)
        self.assertEqual(set(self.m['removed']),{'EarInsetL','EarInsetR'})
        self.assertEqual(len(self.m['added']),8)

    def test_fail_closed_checkpoint(self):
        m=json.loads((pilot.ROOT/'hardware/releases/ears-e1.json').read_text())
        self.assertTrue(verify(pilot.ROOT,m)['integrity_ok'])
        self.assertFalse(verify(pilot.ROOT,m,True)['integrity_ok'])
        entry=json.loads((pilot.CAD/'current-assembly.json').read_text())
        current=json.loads((pilot.ROOT/entry['manifest']).read_text())
        self.assertTrue(verify(pilot.ROOT,current)['integrity_ok'])
        self.assertFalse(self.a['cad_saved']);self.assertFalse(self.g['cad_saved'])

    def test_no_mcp_backup_dependencies(self):
        import zipfile,xml.etree.ElementTree as E
        with zipfile.ZipFile(task.TARGET) as f:root=E.fromstring(f.read('Document.xml'))
        paths={n.get('file') for n in root.iter('XLink') if n.get('file')}
        self.assertEqual(len(paths),10)
        self.assertTrue(all(p.startswith(('../modules/','../parameters/')) for p in paths))
        self.assertFalse(any('backup' in p.lower() or 'appdata' in p.lower() for p in paths))

if __name__=='__main__':unittest.main()
