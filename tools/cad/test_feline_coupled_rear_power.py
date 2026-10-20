"""Recipe/math regression only. Whole-scene clearances are separate receipts."""
import math,unittest
import FreeCAD as A
import Part
from plan_feline_coupled_rear_power import construct,factory_math,e2_z,feed_gate


def fixture():
    ends=[]
    for w,z in [('XP02',81.93904755831474),('XP03',84.93904755831474)]:
        for side,x,d in [('source',-80.3,-1),('module',-49.7,1)]:
            wire=w+'.'+side
            ends.append(dict(id=wire+'/extra/start',wire=wire,group='JPWM',physical_side=side,
                point_mm=[x,-78.8,z],departure_axis=[d,0,0]))
    for w,z,prefix in [('XP02.module',-26.18473506235435,19.47787445225672),
                       ('XP03.module',-28.82526493764565,22.017874452256724)]:
        ends.append(dict(id=w+'/extra/end',wire=w,group='U1',
            routing_exit_mm=[42.77,8.05,z],source_prefix_length_mm=prefix))
    ends.extend([dict(id='XA01/extra/start',point_mm=[88,68,98]),
        dict(id='XA01/extra/end',point_mm=[143,-25.5,-15]),
        dict(id='XP01/extra/start',point_mm=[68.5,68,98]),
        dict(id='XP01/extra/end',point_mm=None,jacket_routing_point_mm=[116,75,27])])
    fixed={'Station:P_REAR:case':Part.makeBox(37,22,11,A.Vector(56.5,68,92.5)),
        'Station:F_PWM_whole:F_PWM:case':Part.makeCylinder(3.2,42,A.Vector(116,75,27)),
        'Ref_Material_JPWM_0_0':Part.makeBox(26,12,12,A.Vector(-78,-84.8,77.43904755831474))}
    return fixed,ends


class CoupledRearPower(unittest.TestCase):
    def test_whole_units_both_sides_and_two_distinct_input_lands(self):
        fixed,ends=fixture();actors,groups,recipe=construct(fixed,ends,scoped_units_only=True)
        self.assertEqual(len([n for n in actors if n.startswith('JPWM')]),10)
        self.assertAlmostEqual(actors['JPWMSource:XP02.source'].BoundBox.YMin,-24.3)
        self.assertAlmostEqual(actors['JPWMSource:XP02.module'].BoundBox.YMax,24.3)
        self.assertAlmostEqual(actors['FPWM:input_independent9'].BoundBox.XLength,9.)
        self.assertAlmostEqual(recipe['XP01_total_mm'],49.05)
        self.assertLessEqual(recipe['XP01_total_mm'],recipe['XP01_max_mm'])
        self.assertTrue(recipe['same_physical_PREAR_cavity_ids'])
        self.assertFalse(recipe['selected']);self.assertFalse(recipe['N01_complete'])
        self.assertAlmostEqual(actors['FPWM:newcase'].Volume,fixed['Station:F_PWM_whole:F_PWM:case'].Volume)

    def test_four_whole_factory_budgets_keep_actual_formed_bare_tails(self):
        _,ends=fixture();r=factory_math(ends)
        self.assertEqual(set(r['routes']),{'XP02.module','XP03.module','XP02.source','XP03.source'})
        self.assertAlmostEqual(r['routes']['XP02.module']['actual_formed_bare_mm'],4.825731389149254)
        self.assertAlmostEqual(r['routes']['XP03.module']['actual_formed_bare_mm'],7.466261264440554)
        for row in r['routes'].values():
            self.assertGreaterEqual(row['minimum_catalogue_margin_mm'],0)
            self.assertTrue(row['factory_contact_preserved'])
            self.assertTrue(all(p.get('radius_mm',math.inf)>=12.4 for p in row['parts']))
        self.assertAlmostEqual(r['need_mm']['XP02.source'],217.26793484193473)
        self.assertFalse(r['N01_complete'])

    def test_both_fuses_required_before_any_whole_trial(self):
        fixed,ends=fixture();gate=feed_gate(ends)
        self.assertEqual({r['wire'] for r in gate['rows'] if r['hard_hold']},{'XP01','XA01'})
        with self.assertRaisesRegex(ValueError,'BOTH XP01 and XA01'):
            construct(fixed,ends)
        self.assertTrue(gate['not_a_routed_or_electrical_PASS'])


if __name__=='__main__':unittest.main()
