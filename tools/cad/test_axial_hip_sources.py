import json,math,unittest,os
import numpy as np
import FreeCAD as A
import current_body_fanout_material as M
from plan_axial_hip_sources import OUT,ROOT,ends,build
from search_axial_source_layout import ends as current_ends,solve_flex
from plan_current_moving_looms import add,mul,exact_turn_to
from open_prototype_path_preflight import samples
PLAN_NAME=os.environ.get('ROBOT_CAT_AXIAL_PLAN_NAME','body-axial-hip-plan.json')


class AxialSourceTests(unittest.TestCase):
    def test_solver_against_independent_inclined_arc_fixtures(self):
        for x in (-1,1):
            for y in (-1,1):
                for beta in (15,45,60):
                    cb=math.cos(math.radians(beta));sb=math.sin(math.radians(beta))
                    u=[-x*.8*cb,y*.6*cb,sb];exit=[x,0,0]
                    first=exact_turn_to([0,0,-60],[0,0,-1],u,31.5)
                    second=exact_turn_to(add(first['end'],mul(u,50)),u,exit,31.5)
                    end=add(second['end'],mul(exit,40));length=150+first['length_mm']+second['length_mm']
                    parts=build([0,0,0],end,exit,length,beta)
                    self.assertIsNotNone(parts,(x,y,beta))
                    self.assertLess(math.dist(parts[-1]['end'],end),1e-6)
                    self.assertAlmostEqual(sum(p['length_mm'] for p in parts),length,places=6)

    def test_all124_current_axial_endpoints_tangencies_and_length_margin(self):
        plan=json.loads((OUT/PLAN_NAME).read_text());self.assertFalse(plan['rejected'])
        axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes'];count=0
        for row in plan['hips']:
            self.assertAlmostEqual(row['factory_guide_mm'],9)
            for pose in row['poses']:
                factory=M.B.moved_parts(row['source_parts'],row['source'],pose['angle'],0,axes)
                edges=[M.P.wire([p]).Edges[0] for p in pose['parts']+factory]
                for a,b in zip(edges,edges[1:]):
                    self.assertLess(a.Vertexes[-1].Point.distanceToPoint(b.Vertexes[0].Point),1e-6)
                    self.assertGreater(a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter)),1-1e-6)
                parameter=row.get('bridge_cosine') if row.get('flex_construction')=='antiparallel_axial_return' else row['bridge_beta_degrees']
                for d in (-5,5):self.assertIsNotNone(solve_flex(row,pose['angle'],row['flex_length_mm']+d,parameter))
                self.assertAlmostEqual(sum(p['length_mm'] for p in pose['parts']),row['guide_mm'],places=6)
                count+=1
        self.assertEqual(count,124)

    def test_current_families_have_no_sampled_mutual_contact(self):
        plan=json.loads((OUT/PLAN_NAME).read_text());self.assertFalse(plan['rejected'])
        axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes'];curves=[]
        for row in plan['hips']:
            for pose in row['poses']:
                if pose['angle'] not in (-15,0,15):continue
                parts=pose['parts']+M.B.moved_parts(row['source_parts'],row['source'],pose['angle'],0,axes)
                curves.append((row['loom'],pose['angle'],np.asarray([p for _,p in samples(parts,step=2)])))
        for i,(loom,h,p) in enumerate(curves):
            for other,oh,q in curves[:i]:
                if other==loom:continue
                gap=float(np.sqrt(((p[:,None,:]-q[None,:,:])**2).sum(axis=2).min()))
                self.assertGreaterEqual(gap,6.25,(loom,h,other,oh,gap,'Reject only; no clearance certificate'))


if __name__=='__main__':unittest.main()
