import json,math,unittest
from bank_service_source_routes import routes
from plan_current_harness_interfaces import OUT


class SourceServiceTests(unittest.TestCase):
    def test_both_full_curves_factory_bound_and_actual_new_opposed_gap(self):
        m=json.loads((OUT/'mta-interface-plan.json').read_text());p=json.loads((OUT/'main-source-plan.json').read_text());q=routes(m,p)
        self.assertAlmostEqual(q['W041_FACTORY']['guide_mm'],m['factory_routes']['W041_FACTORY']['guide_mm'])
        self.assertAlmostEqual(math.dist(q['W041_FACTORY']['parts'][-1]['end'],q['W041_CUSTOM']['parts'][0]['start']),35.5)
        for r in q.values():
            for a,b in zip(r['parts'],r['parts'][1:]):self.assertLess(math.dist(a['end'],b['start']),1e-7)
            for part in r['parts']:
                if part['kind']=='arc':self.assertEqual(part['radius_mm'],25.2)


if __name__=='__main__':unittest.main()
