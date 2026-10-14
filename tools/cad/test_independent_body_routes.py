"""Current body candidates keep exact endpoints/budgets; no wholeW5 claim."""
import json,math,unittest
import FreeCAD as A
import current_body_fanout_material as M


class BodyRoutesTests(unittest.TestCase):
    def test_received_routes_endpoints_lengths_radii_and_current_budget(self):
        plan=json.loads((M.P.OUT/'body-fanout-layout.json').read_text())
        rows={r['wire']:r for r in plan['rows']}
        self.assertGreaterEqual(len(plan['routes']),20)
        for name,route in plan['routes'].items():
            row=rows[name];parts=route['parts']
            self.assertFalse(row['loom'].endswith('1'))
            self.assertLess(math.dist(parts[0]['start'],row['start']),1e-7)
            self.assertLess(math.dist(parts[-1]['end'],row['receiver_point_mm']),1e-7)
            self.assertAlmostEqual(sum(p['length_mm'] for p in parts),route['guide_mm'],places=5)
            self.assertLessEqual(route['guide_mm'],row['capacity_before_terminal_mm']-row['terminal_allowance_project_mm']+1e-6)
            edges=[M.P.wire([p]).Edges[0] for p in parts]
            for part in parts:
                if part['kind']=='arc':self.assertGreaterEqual(part['radius_mm'],10)
            for a,b in zip(edges,edges[1:]):
                self.assertLess(a.Vertexes[-1].Point.distanceToPoint(b.Vertexes[0].Point),1e-6)
                self.assertGreater(a.tangentAt(a.LastParameter).dot(b.tangentAt(b.FirstParameter)),1-1e-6)


if __name__=='__main__':unittest.main()
