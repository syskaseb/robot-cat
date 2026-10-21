"""Snapshot coverage/source guards, not mechanical N01 acceptance."""
import json,unittest
from collections import Counter
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from compose_feline_rr_two_tier_boundaries import current
import feline_tangent_routes as ft


class CurrentWholeSpace(unittest.TestCase):
    def test_map_preserves_whole_current_scene_and_received_motion(self):
        d=OUT/'joint-corridor-space-20261021'
        space=json.loads((d/'n01-integrated-signed-space.json').read_text())
        bridge=json.loads((d/'owner-source-cache-bridge.json').read_text())
        self.assertEqual(space['status'],'CURRENT_SIGNED_CLOSED_VOLUME_SPACE_PROPOSALS_ONLY')
        self.assertEqual(space['errors'],[])
        self.assertEqual(sha(ROOT/space['field']),space['field_sha256'])
        self.assertEqual(len(bridge['source_geometry_sha256']),1524)
        self.assertEqual(bridge['byte_identical_reused_sources'],925)
        self.assertTrue(bridge['no_variable_or_dropped_power_owners'])
        self.assertEqual(space['layer_checkpoint']['motion_count'],3888)
        self.assertFalse(space['N01_complete'])
        for n in ('RRUpperHead','RRGJointRoot','RRDirectGround:W074','AuxGrip:CommonRoot','PowerMount:Trunk:PETG'):
            self.assertIn(n,bridge['source_geometry_sha256'])

    def test_all123_and246_current_boundaries_are_classified_not_awarded(self):
        _,rows,_=current();ends={e['id']:e for e in rows}
        p=json.loads((OUT/'joint-corridor-space-20261021/current123-macro-corridors.json').read_text())
        self.assertEqual(p['status'],'CURRENT123_MACRO_CLASSIFICATION_AND_GUIDES_RECORDED_NOT_N01')
        self.assertEqual(len(p['portions']),123)
        identities=[e for r in p['portions'].values() for e in r['end_ids']]
        self.assertEqual(Counter(identities),Counter(ends.keys()))
        self.assertFalse(p['N01_complete']);self.assertFalse(p['selected'])
        for row in p['portions'].values():
            if row['status']=='CURRENT_WHOLE_PORTION_RECEIVED_NOT_REROUTED':
                self.assertTrue(all(ends[e].get('full_middle_route_accepted') for e in row['end_ids']))
            for a in row.get('anchors',[]):
                eid=a.get('end_id',a.get('end'));self.assertIn(eid,ends)
                self.assertEqual(a['point_mm'],ends[eid]['routing_exit_mm'])

    def test_curved_links_and_whole_paths_keep_actual_endpoint_tangents(self):
        d=OUT/'joint-corridor-space-20261021'
        links=json.loads((d/'current-curved-source-links.json').read_text())
        self.assertEqual(len(links['ends']),246)
        self.assertFalse(links['N01_complete'])
        for e in links['ends'].values():
            for r in e.get('field_positive',[]):
                self.assertTrue(np.allclose(r['parts'][0]['start'],e['point_mm']))
                self.assertGreaterEqual(ft.min_radius(r['parts'])+1e-6,e['minimum_R_mm'])
                self.assertTrue(all(v>=0 for v in r['field']['minima_mm'].values()))
        paths=json.loads((d/'current-curved-path-preflight.json').read_text())
        self.assertFalse(paths['N01_complete']);self.assertEqual(len(paths['paths']),4)
        for pid,r in paths['paths'].items():
            parts=r['parts'];start=links['ends'][pid+'/start'];end=links['ends'][pid+'/end']
            self.assertTrue(np.allclose(parts[0]['start'],start['point_mm']))
            self.assertTrue(np.allclose(parts[-1]['end'],end['point_mm']))
            for a,b in zip(parts,parts[1:]):
                self.assertTrue(np.allclose(a['end'],b['start']))
                ta=ft.unit(ft.sub(a['end'],a['start'])) if a['kind']=='line' else a['end_tangent']
                tb=ft.unit(ft.sub(b['end'],b['start'])) if b['kind']=='line' else b['tangent']
                self.assertTrue(np.allclose(ta,tb,atol=1e-6))
            self.assertTrue(np.allclose(parts[0]['tangent'] if parts[0]['kind']=='arc' else ft.unit(ft.sub(parts[0]['end'],parts[0]['start'])),start['outward_axis']))
            self.assertTrue(np.allclose(parts[-1]['end_tangent'] if parts[-1]['kind']=='arc' else ft.unit(ft.sub(parts[-1]['end'],parts[-1]['start'])),-np.asarray(end['outward_axis'])))
        self.assertEqual(paths['paths']['W047/body']['status'],'SELF_SEPARATION_PROPOSAL_HOLD')
        self.assertTrue(any(r['a']=='W022/body' and r['b']=='W024/body' and r['status'].startswith('SHARED_LANE') for r in paths['mutual']))


if __name__=='__main__':unittest.main()
