import json
import unittest
import FreeCAD as A
from plan_body_fanout_layout import OUT
from planar_csc_flex import domain,build
from planar_round_flex import domain as vertical_domain
from plan_low_hip_rail_exit import ends as vertical_ends
from oblique_source_fans import fan
import current_body_fanout_material as M
P=M.P


class ObliqueMotionTests(unittest.TestCase):
    def test_general_equations_match_received_vertical_domain(self):
        prior=json.loads((OUT/'body-low-hip-rail-exit-plan.json').read_text())
        for row in prior['hips']:
            for h in (-15,0,15):
                a,b,v,m=vertical_ends(row,h)
                for beta in (-40,0,40):
                    old=vertical_domain(a,b,v,beta);new=domain(a,b,[0,0,-1],v,beta)
                    self.assertEqual(old is None,new is None)
                    if old is not None:
                        self.assertAlmostEqual(old['minimum_mm'],new['minimum_mm'],places=6)
                        self.assertAlmostEqual(old['maximum_mm'],new['maximum_mm'],places=6)

    def test_all124_actual_endpoints_tangencies_and_nominal_length(self):
        plan=json.loads((OUT/'body-oblique-port-motion-plan.json').read_text())
        family=json.loads((OUT/'leg-source-near-member-plan.json').read_text())
        axes=json.loads((P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
        count=0
        for row in plan['hips']:
            original=next(r for r in family['routes'] if r['loom']==row['loom'])
            for pose in row['poses']:
                parts=pose['parts'];factory=M.B.moved_parts(original['source_parts'],original['source'],pose['angle'],0,axes)
                self.assertLess(A.Vector(*parts[-1]['end']).distanceToPoint(A.Vector(*factory[0]['start'])),1e-6)
                self.assertAlmostEqual(sum(p['length_mm'] for p in parts),row['guide_mm'],places=6)
                edges=[P.wire([p]).Edges[0] for p in parts]
                for a,b in zip(edges,edges[1:]):self.assertGreater(a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter)),1-1e-7)
                for part in parts:
                    if part['kind']=='arc':self.assertEqual(part['radius_mm'],31.5)
                count+=1
        self.assertEqual(count,124)

    def test_rigid_breakout_rotation_preserves_core_separation(self):
        plan=json.loads((OUT/'body-oblique-port-motion-plan.json').read_text())
        for row in plan['hips']:
            for direction in ([1,0,0],[-1,0,0],[0,1,0],[0,-1,0]):
                cores=fan(row,direction);wires=[P.wire(r['parts']) for r in cores]
                for i,w in enumerate(wires):
                    for q in wires[:i]:self.assertGreaterEqual(w.distToShape(q)[0],2.25-1e-6)
                for core in cores:self.assertAlmostEqual(sum(p['length_mm'] for p in core['parts'])-sum(p['length_mm'] for p in core['after_5mm']),5)


if __name__=='__main__':unittest.main()
