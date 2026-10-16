import json,math,unittest
from plan_bank_prototype_service import proposal,OUT


class PrototypeServiceTests(unittest.TestCase):
    def test_prefuse_limit_and_actual_guide_length_survive_parking(self):
        source=json.loads((OUT/'source-receiving-plan.json').read_text());ground=json.loads((OUT/'ground-tree-plan.json').read_text())
        roots=json.loads((OUT/'local-source-retention-roots.json').read_text());service=json.loads((OUT/'local-bank-cradle-space.json').read_text())
        p=proposal(source,ground,roots,service);park=p['W043_park'];old=source['factory_routes']['W043']
        self.assertAlmostEqual(sum(r['length_mm'] for r in park['parts']),sum(r['length_mm'] for r in old['parts']))
        self.assertLessEqual(park['unchanged_factory_blank_mm'],50)
        self.assertGreater(p['rejected_P_SYS_inward_rotation']['straight_distance_plus_strip_lower_bound_mm'],50)
        self.assertAlmostEqual(park['free_end_mm'][1],70.3)
        self.assertEqual(p['G1_change']['translation_mm'],[0,4.5,0])
        self.assertEqual(len(p['removable_rail']['occupied_ports']),4)
        self.assertEqual(p['removable_rail']['parking_transform']['resulting_heavy_wire_departure'],[0,0,1])
        for point in p['removable_rail']['parking_transform']['resulting_free_end_points_mm'].values():
            self.assertAlmostEqual(point[1],34);self.assertAlmostEqual(point[2],144.2)
        self.assertFalse(p['selected']);self.assertFalse(p['A2_complete'])
        for a,b in zip(park['parts'],park['parts'][1:]):self.assertLess(math.dist(a['end'],b['start']),1e-8)


if __name__=='__main__':unittest.main()
