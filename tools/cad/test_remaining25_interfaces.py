import json
import unittest
from plan_remaining25_interfaces import endpoint_land, allocate, OUT


class RemainingInterfacesTests(unittest.TestCase):
    def test_end_orientation_and_downstream_land(self):
        p=[dict(kind='line',start=[0,0,0],end=[0,0,20],length_mm=20),
           dict(kind='arc',start=[0,0,20],end=[5,0,25],length_mm=8),
           dict(kind='line',start=[5,0,25],end=[7.5,0,25],length_mm=2.5)]
        r=endpoint_land(p,'end',9)
        self.assertEqual(r['part_index'],0)
        self.assertEqual(r['centre_world_mm'],[0,0,15.5])
        self.assertEqual(r['intervening_guide_mm'],10.5)

    def test_short_insulation_is_not_invented(self):
        with self.assertRaises(AssertionError):
            endpoint_land([dict(kind='line',start=[0,0,0],end=[2,0,0],length_mm=2)],'start',3)

    def test_current_twenty_five_complete_physical_binding(self):
        reg=json.loads((OUT/'harness-interfaces-plan.json').read_text())
        names={r['guide']['plan'] for r in reg['body_conductors'] if r['route_status']=='SCOPED_NOMINAL_GUIDE_QUALIFIED_NATIVE_OPEN'}
        names.update(r['factory_segment']['plan'] for r in reg['body_conductors'] if r.get('factory_segment'))
        plans={n:json.loads((OUT/n).read_text()) for n in names}
        ends,cuts,groups=allocate(reg,plans)
        self.assertEqual((len(ends),len(cuts),len(groups)),(66,33,55))
        self.assertEqual(sum('_Joint.' in e['role'] for e in ends),16)
        self.assertEqual(sum(bool(e['already_native_source_group']) for e in ends),3)
        self.assertFalse(any(e['qualified'] for e in ends))
        w052=next(e for e in ends if e['wire']=='W052' and e['segment']=='custom' and e['side']=='end')
        self.assertGreater(w052['land']['intervening_guide_mm'],0)
        self.assertEqual(w052['land']['land_mm'],9)


if __name__=='__main__':unittest.main()
