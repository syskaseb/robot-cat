"""Current data rack must be an auditable native result, not partial routing."""
import hashlib
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/wiring-checkpoint'


class DataShelfPackage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=json.loads((OUT/'data-shelf-package.json').read_text())

    def test_complete_local_native_result(self):
        self.assertEqual(self.p['status'],'NATIVE_DATA_MOUNT_AND_TEN_STRAIGHT_APPROACHES_PREPARED')
        self.assertTrue(self.p['local_data_mount_complete']);self.assertTrue(self.p['reopen_verified'])
        self.assertEqual(self.p['contacts'],[]);self.assertEqual(self.p['errors'],[])

    def test_not_whole_wiring_acceptance(self):
        for k in ('selected','stage_completed','physical_pass'):self.assertFalse(self.p[k])
        self.assertTrue(self.p['full_data_conductors_and_source_family_still_open'])
        self.assertEqual(len(self.p['invalidated_wires']),8)

    def test_correct_full_ten_new_endpoints(self):
        self.assertEqual(len(self.p['changed_ports']),10)
        for station in self.p['changed_stations']:
            left=station['role']=='D_RL'
            self.assertEqual(station['size_mm'],[19,30,9] if left else [30,19,9])
            self.assertEqual(station['rotation'],'90' if left else '0')
            x=station['centre_mm'][0]
            for i in range(1,6):
                v=self.p['changed_ports'][station['role']+'.'+str(i)]
                self.assertEqual(v['point_mm'],[x+9.5,-20+(i-3)*4.75,128] if left else [x+(i-3)*4.75,-29.5,128])
                self.assertEqual(v['departure'],[1,0,0] if left else [0,-1,0])
        self.assertTrue(all(e['straight_mm']==9 and e['support_mm']==8 for e in self.p['entry_lands']))

    def test_native_export_and_input_integrity(self):
        digest=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
        self.assertEqual(digest(OUT/'DataShelfCurrent.FCStd'),self.p['model_sha256'])
        self.assertEqual(len(self.p['exports']),2)
        for n,v in self.p['exports'].items():
            self.assertEqual(digest(OUT/n),v['sha256']);self.assertTrue(v['closed'] and v['manifold'])
        for n,h in self.p['source_sha256'].items():self.assertEqual(digest(ROOT/n),h,n)

    def test_full_root_and_print_margin(self):
        self.assertGreater(self.p['root_bearing_area_mm2'],239)
        self.assertTrue(all(max(v)<=246 for v in self.p['print_bounds_mm'].values()))
        self.assertEqual(self.p['parameter_test']['thickness_mm'],[3,3.2,3])
        self.assertTrue(self.p['parameter_test']['restored'])

    def test_hardware_not_lost_or_used_as_unknown_pad_clamp(self):
        self.assertEqual(self.p['hardware_contribution'],{'M3x10':2,'M3_washer':2,'M3_nut':2,'T18I':2})
        t=self.p['tie_budget']
        self.assertGreater(t['slot_width_mm'],t['strap_width_mm'])
        self.assertGreater(t['slot_height_mm'],t['strap_thickness_mm'])
        self.assertLess(t['loop_perimeter_max_mm']+10,t['nominal_stock_length_mm'])
        self.assertTrue(t['not_manufacturer_measured_shape'])


if __name__=='__main__':unittest.main()
