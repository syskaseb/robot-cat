import unittest
from compose_current_retained_endpoints import endpoints,compose


class EndpointTests(unittest.TestCase):
    def test_same_rail_map_attaches_to_correct_route_side(self):
        names=['W001','W060','W076']+[f'TEST{i}' for i in range(16)]
        inventory=dict(guides={});register=dict(body_conductors=[])
        for i,wid in enumerate(names):
            segments=[dict(parts=[dict(start=[i,0,0],end=[i,0,10])])]
            if wid=='W076':segments.append(dict(parts=[dict(start=[i,0,20],end=[i,0,30])]))
            inventory['guides'][wid]=dict(recipe_file='test.json',segments=segments)
            register['body_conductors'].append(dict(id=wid,roles=['old_a','old_b'],current_ends=[dict(role='unknown')]))
        ground=dict(G1_same_ground_port_mapping={'W001':2,'W060':1},routes={
            'W001':dict(endpoints=['BAT.minus','G1.1']),
            'W060':dict(endpoints=['G1.4','MAIN.GND'])})
        rows={r['wire']:r for r in compose(inventory,register,ground)}
        self.assertEqual(rows['W001']['nominal_geometry_endpoints'][-1]['current_G1_cavity'],'G1.2')
        self.assertEqual(rows['W060']['nominal_geometry_endpoints'][0]['current_G1_cavity'],'G1.1')
        self.assertNotIn('current_G1_cavity',rows['W060']['nominal_geometry_endpoints'][-1])
        self.assertIn('No coordinate supplied',rows['W060']['nominal_geometry_endpoints'][0]['old_register_comparison'])

    def test_two_disconnected_portions_keep_four_boundaries(self):
        rows=endpoints([dict(parts=[dict(start=[0,0,0],end=[0,0,10])]),
                        dict(parts=[dict(start=[0,0,20],end=[0,0,30])])])
        self.assertEqual(len(rows),4)
        self.assertEqual(rows[1]['point_world_mm'],[0,0,10])
        self.assertEqual(rows[2]['point_world_mm'],[0,0,20])
        self.assertIn('DO NOT bridge',rows[1]['boundary'])

    def test_discontinuous_parts_within_one_recipe_rejected(self):
        with self.assertRaises(AssertionError):endpoints([dict(parts=[
            dict(start=[0,0,0],end=[0,0,10]),dict(start=[0,0,20],end=[0,0,30])])])


if __name__=='__main__':unittest.main()
