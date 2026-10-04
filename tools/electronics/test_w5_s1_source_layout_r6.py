import unittest,math
from w5_s1_source_layout_r6 import layout

class WholeSourceAndAux(unittest.TestCase):
    def test_no_vacant_cage_or_lost_aux(self):
        rows=layout()
        self.assertEqual([r['wire'] for r in rows],['W064','W065','W067','W068','XA01'])
        source=rows[1];aux=rows[-1]
        self.assertEqual(source['a'],'P_REAR.1');self.assertEqual(aux['a'],'P_REAR.5')
        self.assertEqual(source['start'],[32,0,129])
        self.assertEqual(aux['start'],[32,13.6,129])
        self.assertEqual(aux['b'],'F_AUX.in')
        self.assertEqual(aux['wire_sku'],'HELU23502')
        self.assertEqual(aux['complete_prefuse_limit_mm'],50)
        self.assertIsNone(aux['holder_internal_path_mm'])
        self.assertFalse(aux['full_prefuse_length_verified'])
        self.assertGreater(aux['holder_internal_available_budget_mm'],0)

    def test_complete_continuous_nominal_lengths(self):
        for row in layout():
            self.assertFalse(row['selected']);self.assertFalse(row['physical_pass'])
            for a,b in zip(row['edges'],row['edges'][1:]):
                self.assertLess(math.dist(a['end'],b['start']),1e-7)
            for edge in row['edges']:
                self.assertGreater(edge['length_mm'],0)
                if edge['kind']=='arc':
                    self.assertGreaterEqual(edge['radius_mm'],row['minimum_static_radius_mm'])
            allowance=12 if row['wire']=='XA01' else 52.73
            self.assertGreaterEqual(row['nominal_trial_blank_mm'],row['exposed_path_mm']+allowance)

    def test_ring_datums_unchanged_and_upper_roof_not_inferred(self):
        rows=layout()
        for row in rows[:4]:
            self.assertAlmostEqual(row['end'][2],64.8067)
            self.assertEqual(row['ring_seating_Z_provisional_mm'],62)
        max_z=max(p[2] for r in rows for e in r['edges'] for p in (e['start'],e['end']))
        self.assertAlmostEqual(max_z,215.2)
        self.assertGreater(max_z+2.1,185)

if __name__=='__main__':unittest.main()
