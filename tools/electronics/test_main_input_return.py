"""Pure checks for the all-parameter bend proof and inherited datums."""
import math
import json
from pathlib import Path
import unittest
import main_input_return_r1 as R1
import main_input_return_r2 as R2

def test_straight_has_infinite_radius():
    assert math.isinf(R1.radius_bound([[0,0,0],[0,0,1],[0,0,2],[0,0,3]]))

def test_cubic_quarter_circle_bound_is_conservative():
    k=4*(math.sqrt(2)-1)/3
    p=[[1,0,0],[1,k,0],[k,1,0],[0,1,0]]
    assert .98<R1.radius_bound(p)<1

def test_rigid_translation_does_not_change_radius():
    p=R2.POLES
    moved=[[x+30,y-10,z+12] for x,y,z in p]
    assert math.isclose(R1.radius_bound(moved),R1.radius_bound(p),rel_tol=1e-6)

def test_uniform_scaling_scales_radius():
    p=R2.POLES
    assert math.isclose(R1.radius_bound([[2*v for v in q] for q in p]),2*R1.radius_bound(p),rel_tol=1e-7)

def test_east_fan_preserves_vertical_end_tangents():
    a,b,c,d=R2.POLES
    assert a[:2]==b[:2] and c[:2]==d[:2]
    assert a[2]>b[2] and c[2]>d[2]
    assert R1.radius_bound(R2.POLES)>6

def test_selected_wago_and_actual_main_pad_datums():
    assert R1.START==[81,11,113.5]
    assert all(math.isclose(a,b) for a,b in zip(R1.PAD,[9.049+105.82,.25+8.16,10.5748+52]))

def test_second_corridor_does_not_repeat_first_fan():
    assert R2.POLES[0][0]==133 and R2.POLES[0][1]==21
    assert R2.POLES!=R1.POLES

ROOT=Path(__file__).resolve().parents[2]
FINAL=ROOT/'hardware/electronics/full-cat/main-input-return-finish-r3'

def read_final(name):
    return json.loads((FINAL/name).read_text(encoding='utf-8'))

def test_corrected_deck_has_finite_open_mouth_and_floor():
    c=read_final('deck-mouth-checks.json')
    rise=c['seat_top_mm']-c['wire_centre_z_mm']
    assert c['groove_radius_mm']>rise
    width=2*math.sqrt(c['groove_radius_mm']**2-rise**2)
    assert width>1 and c['minimum_floor_mm']>=2.9
    assert c['relocated_reopen'] and c['strict_BOP_errors']==0
    assert c['parameter_probe_mm3'][0]==c['parameter_probe_mm3'][2]
    assert c['parameter_probe_mm3'][0]!=c['parameter_probe_mm3'][1]

def test_finished_sources_and_mesh_do_not_hide_soft_contact():
    c=read_final('checks.json');i=read_final('interface.json')
    assert c['mesh_export_complete'] and not c['blocking_hits']
    assert all(v['closed'] and v['components']==1 for v in c['mesh_checks'].values())
    assert not c['physical_pass'] and not c['collision_free'] and not c['W5_complete']
    assert c['geometry_gate']=='open' and len(c['nominal_soft_contacts'])==1
    assert c['hits']==c['nominal_soft_contacts']
    assert c['hits'][0]['part']=='W060_input_outer_boot' and 0<c['hits'][0]['hit_mm3']<.2
    assert i['native_sources']['Deck']=='hardware/cad/studies/main-input-return-finish-r3/DeckMainInput.FCStd'
    assert i['native_sources']['MAIN']=='hardware/cad/studies/main-input-return-finish-r2/MainInputMount.FCStd'

def test_package_changes_only_two_prints_and_three_existing_ties():
    import package_main_input_return_r40 as P
    before=P.read(P.PARENT/'selection.json');quantities=P.read(P.PARENT/'one-order-quantities.json')
    s,q=P.payload(before,quantities,read_final('checks.json'))
    changed={a['identity'] for a,b in zip(s['prints'],before['prints']) if a!=b}
    assert changed=={'electronics:DeckP10-cover-mount','P0-MAIN-MOUNT-R5'}
    assert len(s['prints'])==71 and s['installed_petg_parts']==110 and s['fit_samples']==4
    assert len(q['lines'])==114
    assert next(r for r in q['lines'] if r['id']=='tie:111-02370')['installed']==93
    assert next(r for r in q['lines'] if r['id']=='p0:PI-POWER-CABLE')['planning_quantity']==1

def load_tests(loader,tests,pattern):
    return unittest.TestSuite(unittest.FunctionTestCase(f) for n,f in globals().items() if n.startswith('test_'))

if __name__=='__main__': unittest.main()
