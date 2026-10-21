import unittest
import FreeCAD as A
import Part
from receive_feline_underplate_return_gallery import bend
from feline_source_saddles import build
from plan_feline_opposed_power_unit import receive_own_grips,construct,xa02_corridor


class OpposedUnit(unittest.TestCase):
    def test_corridor_uses_all_station_and_whole_trunk_boundaries(self):
        import math
        from plan_feline_n01_shared import pipe
        rows,p=xa02_corridor([151.43,-57.73,73.21],[94,25,84],[.5,-math.sqrt(3)/2,0],
            A.BoundBox(78,-54.521384,84,106,-40,104),62.65,
            A.BoundBox(69,-69.25,94.45,91,-60.25,101.55),92.7,83.)
        self.assertGreater(p['shared_Y_interval_mm'][1],p['shared_Y_interval_mm'][0])
        self.assertEqual(p['shared_high_Z_interval_mm'],[85.5,90.2])
        s=pipe(rows,1.25)
        self.assertTrue(s.isValid())
        self.assertEqual(len(s.Solids),1)

    def test_whole_five_port_identity_and_short_feed_contract(self):
        fixed={
            'Station:P_REAR:case':Part.makeBox(30,22,19,A.Vector(-15,-11,-9.5)),
            'Ref_Material_F_AUX_candidate_case_0_0':Part.makeBox(22,51,20.25,A.Vector(-11,-25.5,-10.125)),
            'Station:F_PWM_whole:F_PWM:case':Part.makeBox(6.4,6.4,42,A.Vector(-3.2,-3.2,-21))}
        ends=[];portions={}
        for w,x in [('W065',-13),('XP01',-6.5),('W044',0),('W052',6.5),('XA01',13)]:
            ends.append(dict(group='WAGO:P_REAR',wire=w,id=w+'/start',portion_id=w,point_mm=[x,-11,0]))
            portions[w]=dict(minimum_project_R_mm=12.4 if w=='XA01' else 12.6 if w=='XP01' else 25.2,
                             project_radius_mm=2 if w=='XA01' else 1.05 if w=='XP01' else 2.1)
        actors,_,_,_,plan=construct(fixed,ends,dict(portions=portions))
        self.assertEqual(set(plan['recipes']),set(portions))
        changed={w for w,p in plan['planned_cavity_points_mm'].items() if p!=plan['old_cavity_points_mm'][w]}
        self.assertEqual(changed,{'XP01','W065'})
        self.assertTrue(all(v['total_nominal_unfused_mm']<=50 for v in plan['feeds'].values()))
        out=plan['recipes']['XP01']
        self.assertEqual(out['output_grip']['full_jacket_grip_arclength_mm'],[0,9])
        self.assertLess(out['output_prefix_length_mm'],14)
        self.assertTrue(all(s.isValid() and len(s.Solids)==1 for s in actors.values()))
        shared,_,_,_,common=construct(fixed,ends,dict(portions=portions),True)
        self.assertEqual(len(shared),29)
        self.assertEqual(len(shared['PowerFan:trunk:comb'].Solids),1)
        self.assertEqual(common['common_comb_grip_rows_mm'],[0.,9.,18.])
        for w in ('W065','W044','W052'):
            self.assertEqual(common['recipes'][w]['parts'][-1]['length_mm'],27.)
            self.assertGreaterEqual(shared['PowerFan:trunk:comb'].distToShape(shared['PowerFan:wire:'+w])[0],.2-1e-6)
        self.assertEqual(common['recipes']['XA01']['output9']['grip']['full_jacket_grip_arclength_mm'],[0,9])
        self.assertTrue(all(s.isValid() and len(s.Solids)==1 for s in shared.values()))

    def test_inside_arc_has_real_tie_channel_and_full_nine(self):
        rows=[];bend(rows,[0,0,0],[0,1,0],[0,0,-1],25.2,1.5707963267948966)
        kit,proof=build(rows[0],0,[0,0,-1],4.5,channel_band=True)
        self.assertEqual(proof['full_jacket_grip_arclength_mm'],[0,9])
        self.assertEqual(len(kit['pad'].Solids),1)
        self.assertLess(kit['pad'].common(kit['band']).Volume,1e-5)
        self.assertGreaterEqual(kit['pad'].distToShape(kit['band'])[0],.2-1e-6)

    def test_real_own_contact_remains_hold(self):
        key='PowerFan:wire:W044|PowerFan:grip:W044:pad'
        raw=dict(status='HOLD',checks={key:dict(ok=False,gap_mm=0,minimum_mm=1.25)})
        self.assertEqual(receive_own_grips(raw)['failures'],[key])

    def test_foreign_margin_is_never_reclassified(self):
        key='PowerFan:wire:W044|SomeOtherBoard'
        raw=dict(status='HOLD',checks={key:dict(ok=False,gap_mm=.5,minimum_mm=1.25)})
        result=receive_own_grips(raw)
        self.assertEqual(result['failures'],[key])
        self.assertEqual(result['checks'][key]['minimum_mm'],1.25)

    def test_own_order_is_symmetric_without_modifying_raw(self):
        key='PowerFan:wire:W044|PowerFan:grip:W044:pad'
        raw=dict(status='HOLD',checks={key:dict(ok=False,gap_mm=.4,minimum_mm=1.25)})
        self.assertEqual(receive_own_grips(raw)['failures'],[])
        self.assertFalse(raw['checks'][key]['ok'])


if __name__=='__main__':unittest.main()
