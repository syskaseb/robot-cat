import json
import unittest
import FreeCAD as A
from check_rail_hip_shared_space import P,fan
from prepare_rail_hip_retention import overlay
from plan_low_hip_rail_exit import ends
from planar_round_flex import domain,build


class RailHipScopeTests(unittest.TestCase):
    def setUp(self):
        self.plan=json.loads((P.OUT/'body-low-hip-rail-exit-plan.json').read_text())

    def test_joint_fan_packing_real_curves(self):
        for row in self.plan['hips']:
            for direction in ([1,0,0],[-1,0,0],[0,1,0],[0,-1,0]):
                rows=fan(row,direction)
                for core in rows:
                    self.assertGreater(core['entry_mm'],2)
                    self.assertLessEqual(core['entry_mm'],5+1e-8)
                    self.assertAlmostEqual(sum(p['length_mm'] for p in core['parts'])-sum(p['length_mm'] for p in core['after_5mm']),5)
                wires=[P.wire(r['parts']) for r in rows]
                for i,w in enumerate(wires):
                    for q in wires[:i]:self.assertGreaterEqual(w.distToShape(q)[0],2.25-1e-7)

    def test_plus_minus_5_length_has_nonnegative_exact_construction(self):
        for row in self.plan['hips']:
            for angle in range(-15,16):
                a,b,v,moving=ends(row,angle)
                for length in (150,155,160):
                    valid=[]
                    for beta in range(-60,61,2):
                        d=domain(a,b,v,beta)
                        if d and d['minimum_mm']-1e-8<=length<=d['maximum_mm']+1e-8:valid.append(d)
                    self.assertTrue(valid,(row['loom'],angle,length))
                    parts=build(a,b,v,length,valid[0]);self.assertIsNotNone(parts)
                    self.assertAlmostEqual(sum(p['length_mm'] for p in parts),length,places=6)

    def test_only_four_fixed_hip1_interfaces_changed(self):
        inputs=[json.loads((P.OUT/n).read_text()) for n in ('remaining-support-shared-paths.json','remaining-retention-entry.json','remaining-loom-roots-plan.json')]
        paths,ports,roots,changed=overlay(self.plan,*inputs)
        self.assertEqual(len(changed),4)
        for current,original,key in zip((paths,ports,roots),inputs,('paths','ports','lands')):
            for group in current['groups']:
                old=next(g for g in original['groups'] if g['id']==group['id'])
                ids={r['land']['id'] for r in changed}
                self.assertEqual([r for r in group[key] if r.get('land_id',r.get('id')) not in ids],
                                 [r for r in old[key] if r.get('land_id',r.get('id')) not in ids])


if __name__=='__main__':unittest.main()
