import math
import json
import itertools
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/cad'))
from plan_current_fl_bus_group import WitnessSpace, receiver, arch_middle, usable_blank, LONG_SOURCE, ground_middle,descending_s,rising_s_family
from plan_current_mta_interfaces import line
from plan_current_joined_leg_looms import exact_quarter


class CoupledFLBUS(unittest.TestCase):
    def test_rising_s_solves_each_actual_pose_without_shared_closure(self):
        poses=[]
        for i,start in enumerate(([0,0,0],[8,2,3],[-4,-2,-2])):
            poses.append(dict(angles=[i],start=start,flex_start=start,departure_parts_mm=[],
                spans_mm=[[start,[start[0],start[1],start[2]+30],start,start]]))
        q=rising_s_family(dict(poses=poses),[80,0,180])
        self.assertIsNotNone(q)
        for original,pose in zip(poses,q['poses']):
            p=pose['transition_parts_mm']
            self.assertLess(math.dist(p[0]['start'],original['start']),1e-7)
            self.assertLess(math.dist(p[-1]['end'],[80,0,180]),1e-7)
            self.assertAlmostEqual(sum(s['length_mm'] for s in p),q['fixed_bundle_guide_mm'],places=5)
            self.assertTrue(all(s['radius_mm']>=31 for s in p if s['kind']=='arc'))

    def test_descending_s_preserves_endpoints_radius_and_length(self):
        from plan_current_moving_looms import vertical_s
        for target in ([40,25,60],[8,2,60],[0,0,60]):
            start=[0,0,170];q=descending_s(start,target)
            base=vertical_s([0,0,-170],[target[0],target[1],-60],10)
            self.assertIsNotNone(q)
            self.assertLess(math.dist(q[0]['start'],start),1e-7)
            self.assertLess(math.dist(q[-1]['end'],target),1e-7)
            self.assertAlmostEqual(sum(s['length_mm'] for s in q),sum(s['length_mm'] for s in base),places=7)
            for a,b in zip(q,q[1:]):self.assertLess(math.dist(a['end'],b['start']),1e-7)
            self.assertTrue(all(s['radius_mm']==10 for s in q if s['kind']=='arc'))
            if len(q)>1:self.assertEqual(q[-1]['kind'],'arc')

    def test_static_guides_have_no_nonlocal_self_crossing(self):
        from plan_current_fl_bus_group import OUT,sampling_parts,samples
        p=json.loads((OUT/'fl-bus-group-plan.json').read_text())
        for name,row in p['routes'].items():
            grid={};walked=0;previous=None;diameter=4.2 if name=='W025' else 2
            for _,point in samples(sampling_parts(row['parts']),step=1):
                if previous is not None:walked+=math.dist(previous,point)
                previous=point;key=tuple(math.floor(v/6) for v in point)
                for delta in itertools.product((-1,0,1),repeat=3):
                    for other,at in grid.get(tuple(a+b for a,b in zip(key,delta)),()):
                        if walked-at>12:self.assertGreaterEqual(math.dist(point,other),diameter,name)
                grid.setdefault(key,[]).append((point,walked))

    def test_complete_receipt_pins_lengths_and_actual_terminals(self):
        from plan_current_fl_bus_group import OUT,SHA
        p=json.loads((OUT/'fl-bus-group-plan.json').read_text())
        self.assertFalse(p['selected']);self.assertFalse(p['W5_complete'])
        for n,h in p['source_sha256'].items():self.assertEqual(SHA(ROOT/n),h,n)
        if p['status']=='REJECTED_COUPLED_FL_BUS_PLAN':
            self.assertTrue(p['endpoint_failures'])
            return
        self.assertEqual(p['status'],'COUPLED_FL_BUS_PLANNING_ONLY')
        self.assertFalse(p['endpoint_failures'])
        self.assertEqual(len(p['routes']),40)
        self.assertEqual(len(p['factory_assignment']),12)
        self.assertFalse(p['selected']);self.assertFalse(p['W5_complete'])
        e=json.loads((OUT/p.get('body_ends_reference','front-receiver-relayout-plan.json')).read_text())
        ends=e.get('wires',e.get('leg_body_ends'))
        for q in ends:
            route=p['routes'][q['wire']]
            self.assertLess(math.dist(route['parts'][-1]['end'],q['body_point_mm']),1e-7,q['wire'])
        for n,r in p['routes'].items():
            for a,b in zip(r['parts'],r['parts'][1:]):self.assertLess(math.dist(a['end'],b['start']),1e-7,n)
            self.assertAlmostEqual(sum(q['length_mm'] for q in r['parts']),r['guide_mm'],places=6)
        long=[]
        for name,q in p['factory_assignment'].items():
            self.assertGreaterEqual(q['nominal_mm']-50,q['maximum_three_core_requirement_mm'])
            if q['component']=='SPMA3007':long.append(name)
        self.assertTrue(set(long).issubset(p['factory_assignment']))

    def test_longer_component_keeps_same_trim_reserve(self):
        q=json.loads(LONG_SOURCE.read_text())
        self.assertEqual(q['SKU'],'SPMA3007')
        self.assertAlmostEqual(q['derived']['nominal_length_mm'],48*25.4,places=8)
        self.assertAlmostEqual(usable_blank('FL3'),48*25.4-50,places=8)
        self.assertEqual(usable_blank('RL3'),usable_blank('FL3'))
        self.assertEqual(usable_blank('FR3'),usable_blank('FL3'))

    def test_ground_search_preserves_R21_and_endpoints(self):
        p,states=ground_middle(WitnessSpace(),[54.5,84,170.5],[21.5,-54,242])
        self.assertIsNotNone(p)
        self.assertEqual(states,1)
        self.assertLess(math.dist(p[0]['start'],[54.5,84,170.5]),1e-8)
        self.assertLess(math.dist(p[-1]['end'],[21.5,-54,242]),1e-8)
        self.assertTrue(all(s['radius_mm']==21 for s in p if s['kind']=='arc'))
        for a,b in zip(p,p[1:]):self.assertLess(math.dist(a['end'],b['start']),1e-8)

    def test_cross_row_approaches_do_not_intersect_adjacent_ports(self):
        s=WitnessSpace()
        for x in (60.5,65.25,70,74.75,79.5):
            p=receiver([x,60,119.5],[0,0,1],[0,-1,0])
            self.assertTrue(s.clear(p),s.hit)
            s.insert(dict(wire=str(x),OD_mm=2,segments=p))

    def test_core_overlap_follows_travel_across_short_first_segment(self):
        s=WitnessSpace()
        s.insert(dict(wire='Loom/test',OD_mm=6,segments=[line([0,0,10],[0,0,0])]))
        p=[line([1.2,0,0],[1.2,0,-.75]),exact_quarter([1.2,0,-.75],[0,0,-1],[1,0,0],10)]
        self.assertTrue(s.clear(p,margin=0,root=('Loom/test',[0,0,0])),s.hit)

    def test_other_owner_is_never_exempt_at_split(self):
        s=WitnessSpace()
        s.insert(dict(wire='other',OD_mm=6,segments=[line([0,0,10],[0,0,0])]))
        self.assertFalse(s.clear([line([1.2,0,0],[1.2,0,-10])],margin=0,root=('Loom/test',[0,0,0])))

    def test_remote_same_bundle_is_not_exempt(self):
        s=WitnessSpace()
        s.insert(dict(wire='Loom/test',OD_mm=6,segments=[line([0,0,-7],[0,0,-8])]))
        self.assertFalse(s.clear([line([1.2,0,0],[1.2,0,-10])],margin=0,root=('Loom/test',[0,0,0])))

    def test_receiving_insulation_land_and_ground_radius_stay_real(self):
        p=receiver([100.5,84,119.5],[0,0,1],[-1,0,0],21)
        self.assertEqual(p[0]['length_mm'],9)
        self.assertTrue(all(s['radius_mm']==21 for s in p if s['kind']=='arc'))
        for a,b in zip(p,p[1:]):self.assertLess(math.dist(a['end'],b['start']),1e-8)

    def test_ground_middle_keeps_R21_and_both_endpoints(self):
        p=arch_middle([54.5,84,170.5],[21.5,-54,242],21)
        self.assertEqual(p[0]['start'],[54.5,84,170.5])
        self.assertLess(math.dist(p[-1]['end'],[21.5,-54,242]),1e-8)
        self.assertTrue(all(s['radius_mm']==21 for s in p if s['kind']=='arc'))
        for a,b in zip(p,p[1:]):self.assertLess(math.dist(a['end'],b['start']),1e-8)


if __name__=='__main__':unittest.main()
