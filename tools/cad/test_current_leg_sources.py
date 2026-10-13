"""Contracts for the current full source-to-body-grip candidate, not W5."""
import itertools,json,math,unittest
import FreeCAD as A
from plan_current_main_sources import ROOT,OUT
from plan_circular_source_leg_looms import parts_for_loom,moved_parts
from current_prototype_harness_scene import wire


class CurrentLegSources(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads((OUT/'leg-source-current-plan.json').read_text())
        cls.axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']

    def test_twelve_complete_unique_sources_not_selected(self):
        self.assertEqual(len({r['loom'] for r in self.p['routes']}),12)
        self.assertFalse(self.p['selected']);self.assertFalse(self.p['W5_complete'])
        self.assertFalse(self.p['physical_pass']);self.assertFalse(self.p['errors'])

    def test_source_land_is_independent_nine_mm(self):
        for r in self.p['routes']:
            end=r['source_parts'][-1];src=r['source']
            port=src['connector_reservation_world_mm'][src['project_connector_choice']]
            axis=src['cable_exit_world_axis']
            self.assertEqual(end['kind'],'line')
            self.assertAlmostEqual(end['length_mm'],9,places=6)
            self.assertLess(math.dist(end['end'],[a+14*b for a,b in zip(port,axis)]),1e-6)
            self.assertTrue(r['body_route_not_included'])

    def test_fixed_length_connected_tangent_family(self):
        for r in self.p['routes']:
            lengths=[]
            for hip,knee in itertools.product((-15,0,15),repeat=2):
                parts=parts_for_loom(self.p,r['loom'],hip,knee,self.axes)+moved_parts(r['source_parts'],r['source'],hip,knee,self.axes)
                for a,b in zip(parts,parts[1:]):self.assertLess(math.dist(a['end'],b['start']),1e-6)
                s=wire(parts);self.assertTrue(s.isValid())
                for a,b in zip(s.Edges,s.Edges[1:]):
                    self.assertLess((a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length,1e-5)
                    self.assertGreater(a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter)),1-1e-5)
                lengths.append(s.Length)
            # Bezier planner integrates sampled chords; OCC integrates its
            # exact curve. Bound that independent difference to one micron.
            self.assertLess(max(lengths)-min(lengths),.001,r['loom'])
            self.assertLess(abs(lengths[4]-r['guide_to_body_grip_mm']),.001,r['loom'])

    def test_knee_radius_constant31_5_all248(self):
        for r in self.p['knees']:
            self.assertEqual([p['angle'] for p in r['poses']],list(range(-15,16)))
            for p in r['poses']:
                self.assertEqual(p['radius_mm'],31.5)
                self.assertAlmostEqual(sum(s['length_mm'] for s in p['parts']),r['guide_mm'],places=5)

    def test_front_whole_hip_one_upper_other_sections_retained(self):
        parent=json.loads((OUT/'circular-shared-planes-leg-plan.json').read_text())
        self.assertEqual(self.p['knees'],parent['knees'])
        self.assertEqual(self.p['interstage'],parent['interstage'])
        for row,old in zip(self.p['hips'],parent['hips']):
            if row['loom'] in ('FL1','FR1'):
                self.assertEqual(row['fixed_tangent_world'],[0,0,1])
                self.assertEqual(len(row['poses']),31)
            else:self.assertEqual(row,old)


class SharedUnderbodySources(CurrentLegSources):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads((OUT/'leg-source-shared-underbody-plan.json').read_text())
        cls.axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']

    def test_front_whole_hip_one_upper_other_sections_retained(self):
        parent=json.loads((OUT/'leg-source-current-plan.json').read_text())
        for kind in ('hips','knees'):
            for row in self.p[kind]:
                if row['loom'].endswith('2'):
                    self.assertEqual(row,next(q for q in parent[kind] if q['loom']==row['loom']))
        # Every Hip1 and Hip3 circle lies in the actual Hip normal plane.
        for row in self.p['hips']:
            if row['loom'].endswith('2'):continue
            self.assertAlmostEqual(row['fixed_anchor_world_mm'][0],row['moving_anchor_rest_world_mm'][0])
            self.assertEqual(len(row['poses']),31)
            for pose in row['poses']:
                self.assertEqual(pose['radius_mm'],31.5)
                self.assertAlmostEqual(sum(s['length_mm'] for s in pose['parts']),row['guide_mm'],places=5)
        self.assertEqual(self.p['shared_cases'],36)
        self.assertFalse(any(q['status']=='REJECT_PLANNING_PROXIMITY' for q in self.p['near_pairs']))

    def test_whole_receiving_channel_derived_from_swept_cables_and_cases(self):
        allocation=json.loads((OUT/'underbody-channel-allocation.json').read_text())
        stations=json.loads((OUT/'data-ground-mounts-plan.json').read_text())['stations']
        high=max(r['case_bounds_world_mm'][3] for r in stations if r['name'] in ('FL_P','FR_P'))
        for row in self.p['hips']:
            if not row['loom'].endswith('1'):continue
            x=row['fixed_anchor_world_mm'][0]
            self.assertGreaterEqual(x,high+8)
            for q in allocation['results']:
                self.assertTrue(any(lo<=x<=hi for lo,hi in q['free_x_intervals_mm']))
        self.assertEqual({row['fixed_anchor_world_mm'][0] for row in self.p['hips'] if row['loom'].endswith('1')},{63,71})


class NearMemberSources(SharedUnderbodySources):
    @classmethod
    def setUpClass(cls):
        cls.p=json.loads((OUT/'leg-source-near-member-plan.json').read_text())
        cls.axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']

    def test_whole_receiving_channel_derived_from_swept_cables_and_cases(self):
        for row in self.p['hips']:
            if row['loom'].endswith('3'):
                self.assertAlmostEqual(abs(row['fixed_anchor_world_mm'][1]),104,places=6)
                self.assertEqual(row['fixed_anchor_world_mm'][2],91)
            elif row['loom'].endswith('1'):
                self.assertEqual(row['fixed_anchor_world_mm'][2],-8)
                self.assertEqual(abs(row['fixed_anchor_world_mm'][1]),35.5)
                route=next(r for r in self.p['routes'] if r['loom']==row['loom'])
                if row['physical_leg'].startswith('Front'):
                    # Both front source bends stay in one plane; no remote
                    # cross-body return or arbitrary200mm rotating arm.
                    self.assertLess(max(p[k][0] for p in route['source_parts'] for k in ('start','end')),-120)
                else:self.assertEqual(row['fixed_anchor_world_mm'][0],125)

    def test_no_full_turn_branch_accepted_for_new_hip_sections(self):
        for row in self.p['hips']:
            if row['loom'].endswith('2'):continue
            for pose in row['poses']:
                self.assertLessEqual(sum(q['length_mm']/31.5 for q in pose['parts'] if q['kind']=='arc'),math.radians(195)+1e-6)


if __name__=='__main__':unittest.main()
