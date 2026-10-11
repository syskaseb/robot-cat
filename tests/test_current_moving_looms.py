import json,math,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools/cad'))
from plan_current_moving_looms import OUT,metrics,curve_length,sub,norm,dot

class MovingLoomPlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.p=json.loads((OUT/'moving-looms-plan.json').read_text())
    def test_complete_math_family_is_not_material_or_W5_acceptance(self):
        self.assertEqual(self.p['status'],'PROJECT_FLEX_ALLOCATION_ONLY')
        self.assertEqual(len(self.p['looms']),12)
        self.assertFalse(self.p['selected']);self.assertFalse(self.p['W5_complete'])
        for r in self.p['looms']:
            self.assertEqual(set(r['cores']),{'D','G','V'});self.assertFalse(r['manufacturer_flex_data_verified'])
            self.assertEqual(r['rejected_poses'],0)
            self.assertFalse(r['factory_mating_geometry_verified'])
            self.assertAlmostEqual(r['body_fanout_budget_remaining_mm'],850-r['project_factory_mating_reservation_mm']-r['initial_land_mm']-r['constant_flex_budget_mm']-30)
            self.assertGreater(r['body_fanout_budget_remaining_mm'],0)
            self.assertIn('OPEN',r['body_fanout_routes_and_native_grips'])
    def test_exact_length_and_sampled_radius_at_all84_poses(self):
        count=0
        for r in self.p['looms']:
            for v in r['poses']:
                count+=1;qq=v.get('spans_mm',[v.get('poles_mm')])
                length=sum(curve_length(q) for q in qq)
                for q in qq:self.assertGreaterEqual(metrics(q,600)[1],30)
                length+=sum(q['length_mm'] for q in v.get('return_parts_mm',[]))
                length+=sum(q['length_mm'] for q in v.get('transition_parts_mm',[]))
                length+=sum(q['length_mm'] for q in v.get('departure_parts_mm',[]))
                for q in v.get('departure_parts_mm',[]):
                    if q['kind']=='arc':self.assertGreaterEqual(q['radius_mm'],30)
                self.assertAlmostEqual(length,r['constant_flex_budget_mm'],places=3)
        self.assertEqual(count,84)
    def test_knee_return_continuity_and_no_fictitious_clamp(self):
        for r in self.p['looms']:
            if not r['loom'].endswith('2'):continue
            for v in r['poses']:
                self.assertTrue(v['intermediate_waypoint_is_not_a_support'])
                if v.get('low_return_topology'):
                    self.assertEqual(v['body_arrival_axis_mm'],[0,0,1])
                    parts=v['transition_parts_mm'];self.assertTrue(all(q.get('radius_mm',30)>=30 for q in parts))
                    for one,two in zip(parts,parts[1:]):self.assertLess(math.dist(one['end'],two['start']),1e-8)
                    self.assertLess(math.dist(parts[-1]['end'],r['body_dock_mm']),1e-8)
                    continue
                parts=v['return_parts_mm']
                if v['spans_mm']:
                    q=v['spans_mm'][0];self.assertLess(math.dist(q[-1],parts[0]['start']),1e-8)
                    a=sub(q[-1],q[-2]);b=sub(parts[0]['end'],parts[0]['start'])
                    self.assertAlmostEqual(dot(a,b)/norm(a)/norm(b),1)
                else:
                    transition=v['transition_parts_mm']
                    self.assertLess(math.dist(transition[-1]['end'],parts[0]['start']),1e-8)
                    self.assertTrue(all(q.get('radius_mm',31)>=30 for q in transition))
                self.assertEqual([p['kind'] for p in parts],['line','arc','arc','line'])
                self.assertEqual([p['radius_mm'] for p in parts if p['kind']=='arc'],[35,35])
                for one,two in zip(parts,parts[1:]):self.assertLess(math.dist(one['end'],two['start']),1e-8)
                self.assertLess(math.dist(parts[-1]['end'],r['body_dock_mm']),1e-8)

    def test_external_project_outlet_is_not_a_manufacturer_plug_claim(self):
        for r in self.p['looms']:
            self.assertFalse(r['factory_mating_geometry_verified'])
            for v in r['poses']:
                self.assertAlmostEqual(math.dist(v['contact_datum_mm'],v['start']),14)
                self.assertAlmostEqual(math.dist(v['start'],v['flex_start']),r['initial_land_mm'])
                if r['loom'].endswith('3'):
                    self.assertEqual(r['initial_land_mm'],0)
                    land=v['departure_parts_mm'][1]
                    self.assertEqual(land['kind'],'line');self.assertAlmostEqual(land['length_mm'],9)

if __name__=='__main__':unittest.main()
