"""Run with FreeCAD Python unittest; geometric proposals, not N01 approval."""
import json
import ast
from pathlib import Path
import subprocess
import sys
import unittest

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from feline_s1_saddle_layout import fan, pose_points
from plan_feline_whole50_joint import source_after_arc_saddle,source_rear_resume_contract
from plan_feline_layout import OUT


class SaddleContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet=json.loads((OUT/'n01-intrinsic-s1-whole-pose.json').read_text())
        cls.pose=dict(centre_mm=cls.packet['centre_mm'],rotation_rows=np.eye(3).tolist())

    def test_all_four_actual_jacket_datums_kept(self):
        self.assertEqual(len(self.packet['recipes']),4)
        for r in self.packet['recipes']:
            m=fan(self.packet,self.pose,r,4,0,0)
            np.testing.assert_allclose(m['point_mm'],r['point_mm'],atol=1e-12)
            np.testing.assert_allclose(m['departure_axis'],r['departure_axis'],atol=1e-12)
            self.assertEqual(m['core_pose_id'],4)
            self.assertEqual((m['first_mm'],m['R_mm'],m['grip_start_mm'],m['grip_length_mm']),(12,25.2,3,9))
            self.assertTrue(m['each_wire_independent_tie'])
            self.assertTrue(m['common_carrier_root_and_exact_core_fit_OPEN'])

    def test_independent_bends_not_copies_of_one_fixed_fan(self):
        r=self.packet['recipes'][0]
        a=fan(self.packet,self.pose,r,0,0,90)
        b=fan(self.packet,self.pose,r,0,180,90)
        np.testing.assert_allclose(a['point_mm'],b['point_mm'])
        np.testing.assert_allclose(a['bend_unit'],-np.array(b['bend_unit']),atol=1e-12)
        self.assertGreater(np.linalg.norm(np.array(a['after_arc_end_mm'])-b['after_arc_end_mm']),60)

    def test_rigid_pose_applied_once_to_full_wire_saddle_band_head(self):
        r=self.packet['recipes'][2]
        a=fan(self.packet,self.pose,r,0,45,270)
        pose=dict(centre_mm=[36,12,48],rotation_rows=[[0,-1,0],[1,0,0],[0,0,1]])
        b=fan(self.packet,pose,r,7,45,270)
        np.testing.assert_allclose(b['points'],pose_points(a['points'],self.packet,pose),atol=1e-12)
        np.testing.assert_array_equal(a['radii'],b['radii'])
        self.assertEqual(b['head_budget_mm'],[6,6,6])
        self.assertTrue(b['upper_rigid_cap_removed'])
        self.assertEqual(set(b['types']),{1,2})

    def test_received_core_attempts_complete_without_requery(self):
        c=json.loads((OUT/'n01-s1-core-pose-domains.json').read_text())
        self.assertEqual(c['attempts'],2800)
        self.assertEqual(c['resumed_attempts_without_requery'],2797)
        self.assertEqual(len(c['pose_domains']),34)
        self.assertFalse(c['N01_complete'])

    def test_after_arc_saddle_keeps_full_wire_and_existing9mm_land(self):
        m=fan(self.packet,self.pose,self.packet['recipes'][0],43,45,90)
        for side in (-1,1):
            changed=source_after_arc_saddle(m,side,90)
            np.testing.assert_array_equal(changed['points'][:65],m['points'][:65])
            np.testing.assert_array_equal(changed['radii'][:65],m['radii'][:65])
            np.testing.assert_allclose(np.array(changed['grip_point_mm'])+9*np.array(changed['grip_axis']),
                                       m['after_arc_end_mm'],atol=1e-12)
            self.assertEqual(changed['grip_site'],'EXISTING_AFTER_ARC9_JACKET')
            self.assertEqual(changed['R_mm'],25.2)

    def test_interrupted_core_metadata_restored_from_complete_pairs_and_inherited_pins(self):
        result=json.loads((OUT/'n01-source-saddles-whole-joint.json').read_text())
        proposal=result['rear_bay_stack_budget']
        proposal.pop('core_pair_failures',None)
        name=(OUT/'n01-s1-current-source-datums.json').relative_to(Path(__file__).resolve().parents[1]).as_posix()
        result['source_sha256'].pop(name,None)
        restored=source_rear_resume_contract(result,self.packet)
        self.assertEqual(restored['core_pair_failures'],[])
        self.assertEqual(len(restored['core_pair_receipts']),380)

    def test_actual_terminal_and_frame_failures_cannot_be_reported_as_clearance(self):
        c=json.loads((OUT/'n01-source-saddles-whole-joint.json').read_text())
        receipt=c['actual_terminal_witness']
        self.assertEqual(receipt['checked_terminal_count'],24)
        positive=[r for r in receipt['failures'] if r['positive_common_mm3'] is not None and r['positive_common_mm3']>1e-6]
        self.assertTrue(any(r['terminal']=='Ref_Material_F_R4_CP2_IN_0_0' for r in positive))
        self.assertTrue(receipt['source_context_placements_verified'])
        self.assertFalse(receipt['N01_complete'])
        frame=c['outboard_terminal_gallery']
        self.assertEqual(frame['status'],'SOURCE_GALLERY_REJECTED_BY_ACTUAL_CORE_PAIR')
        self.assertTrue(any(r['obstacle']=='Ref_Material_P0_SideRight22_0_0' and r['positive_common_mm3']>900
                            for r in frame['core_pair_failures']))

    def test_legacy47_domain_builder_body_not_changed_by_new_entry_modes(self):
        root=Path(__file__).resolve().parents[1]
        rel='tools/cad/plan_feline_whole50_joint.py'
        previous=subprocess.check_output(['git','show','91765ecf:'+rel],cwd=root,text=True,encoding='utf-8')
        current=(root/rel).read_text(encoding='utf-8')
        def main_tree(text):
            return ast.dump(next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='main'),include_attributes=False)
        self.assertEqual(main_tree(previous),main_tree(current))

    def test_unsigned_core_proposals_are_not_accepted_as_solid_clearance(self):
        result=json.loads((OUT/'n01-source-saddles-whole-joint.json').read_text())
        gate=result['exact_complete_source_core_gate']
        self.assertEqual(gate['received_pose_count'],46)
        self.assertEqual(gate['surviving_core_ids'],[])
        self.assertEqual(gate['errors'],[])
        self.assertTrue(all(r['first_failure'] is not None for r in gate['receipts']))
        self.assertFalse(gate['selected'])
        self.assertFalse(gate['N01_complete'])

    def test_fore_critical_pass_has_all_P0_and_F_HY_not_just_two_side_rails(self):
        result=json.loads((OUT/'n01-source-saddles-whole-joint.json').read_text())
        p=result['fore_outboard_budget']
        self.assertTrue(p['all_fixed_P0_parts_included'])
        self.assertEqual(p['core_pair_failures'],[])
        self.assertEqual(len(p['core_pair_receipts']),900)
        self.assertEqual(len(p['F_PI_complete_field_owner_checked']),20)
        # Legacy list-key spelling is descriptive metadata, not actual owner.
        # Exact ForeFHAC source is F_HY, established from its construction.
        self.assertIn('actual_F_HY_fore_case_bottom_mm',p)
        self.assertFalse(p['N01_complete'])


if __name__=='__main__':unittest.main()
