"""v35 evidence and load-path regression, not a physical release."""
import hashlib
import importlib.util
import json
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('aux35',ROOT/'tools/freecad/skorupa/aux35.py')
aux=importlib.util.module_from_spec(spec);spec.loader.exec_module(aux)

def read(name):return json.loads((aux.OUT/name).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def test_actual_hole_grid_and_supported_stack():
    assert len(aux.ADDITIONS)==14 and len(aux.REPLACEMENTS)==4
    for i,(x,y) in enumerate(aux.HOLES):
        assert x-89.2==pytest.approx(2.54 if i<2 else 38.1)
        assert y+24==pytest.approx(2.54 if i%2==0 else 17.78)
    assert 19-16.5548-1.6==pytest.approx(.8452)
    assert 38.52+13.48==44+8==52
    assert 19-(3+8+1.5748)-1.6==pytest.approx(4.8252)

def test_signed_geometry_and_inheritance():
    plan,native,fit,inherit=[read(n) for n in ['assembly-plan.json','assembly-validation.json','fit-audit.json','inheritance-check.json']]
    assert all(r['master_sha256']==sha(aux.MASTER) for r in [plan,native,fit,inherit])
    assert all(r['source_sha256']==sha(aux.TARGET) for r in [plan,native,inherit])
    assert fit['source_checkpoint_sha256']==inherit['inherited_from_sha256']==aux.SOURCE_SHA
    assert len(plan['components'])==native['components']==320
    assert (native['fixed'],native['revolute'],native['temporary'])==(306,13,29)
    assert inherit['verified'] and inherit['inherited_parts']==302
    assert len(inherit['master_snapshot_checks'])==18 and inherit['max_absolute_delta']<1e-9

def test_native_motion_retention_restored():
    native=read('assembly-validation.json')
    assert native['restored'] and native['solver_result']==0
    assert not native['physical_horn_verified'] and not native['head_actuation_tested']
    trial=native['tests'][0]
    assert len(trial['frames'])==22
    for n,v in trial['peak_angles_deg'].items():
        assert v==pytest.approx(30 if n=='Rev_TailYaw29' else 3,abs=1e-5)
    assert all(r['aux_mount_retained'] and max(r[k] for k in ['max_joint_gap_mm','max_fixed_error_rad','max_axis_error_rad'])<1e-5 for r in trial['frames'])

def test_real_contacts_clearance_and_bench_assembly():
    fit=read('fit-audit.json')
    assert not fit['geometric_checks_passed'] and not fit['print_release']
    scope=read('prototype-scope.json')
    assert scope['prototype_integration_allowed'] and not scope['strict_BOP_passed']
    assert not scope['shell_errors_repaired'] and not scope['mechanical_release']
    assert all(sha(aux.OUT/n)==digest for n,digest in scope['evidence_sha256'].items())
    assert not fit['rest_interferences']
    assert len(fit['sketches'])==11 and all(s['fully_constrained'] for s in fit['sketches'])
    assert len(fit['native_parts'])==9
    assert all(p['valid'] and p['solids']==1 and p['status']=='Valid' and p['fits_256'] for p in fit['native_parts'])
    assert all(not p['bop_errors'] for p in fit['native_parts'] if p['name']!='Shell35')
    for r in fit['contacts']:
        assert min(r['post_to_support_mm2'],r['post_to_pcb_mm2'],r.get('gap_to_deck_mm2',30),r.get('gap_to_bridge_mm2',30))>15
        assert r['shaft_interference_mm3']<1e-6
    assert all(not r['hits'] for r in fit['cable_reserves']+fit['bench_insertion_samples'])
    assert all(r['pin_to_pcb_mm3']<1e-6 for r in fit['terminal_checks'])
    assert fit['assembly_requires_removed_deck'] and not fit['thermal_validation'] and not fit['full_harness_validation']

def test_shell_passages_have_independent_mesh_evidence():
    proof=read('mesh-proof.json')
    assert proof['master_sha256']==sha(aux.MASTER) and not proof['mechanical_release']
    assert proof['required_clearance_passed']
    assert all(r['is_volume'] and r['nonmanifold_edges']==0 for r in proof['meshes'])
    assert all(r['volume_mm3']<.02 for r in proof['intersections'])

def test_one_parent_per_component_no_graph_cycles():
    plan=read('assembly-plan.json');names={r['name'] for r in plan['components']}
    parents={r['child']:r['parent'] for r in plan['joints']}
    assert len(parents)==len(plan['joints'])==len(names)-1
    roots=names-set(parents);assert len(roots)==1
    for start in names:
        seen=set();node=start
        while node in parents:
            assert node not in seen;seen.add(node);node=parents[node]
        assert node in roots
    assert parents['AuxBuck']=='AuxPost35_0'
    assert parents['AuxPost35_0']=='Part__Feature038'
    assert parents['AuxPost35_2']=='TailBridge29'
    assert parents['AuxBolt35_2']=='TailBridge29'
    assert parents['AuxNut35_2']=='AuxBuck'
    assert parents['TailRoot29']=='UpperHousing34'

def test_aux_purchased_masses_not_petg_volume():
    from cad_model import REVISION,OUT,mass_budget
    if REVISION!='v35':pytest.skip('v35 AUX model only')
    rows={r['name']:r for r in mass_budget(json.loads((OUT/'geometry.json').read_text()))}
    assert rows['AuxBuck']['mass_kg']==pytest.approx(.0048)
    for i in range(2):assert rows['AuxTerminal35_'+str(i)]['mass_kg']==pytest.approx(.002)
    posts=[r for n,r in rows.items() if n.startswith(('AuxPost35_','AuxGap35_'))]
    assert len(posts)==4 and all(r['basis'].startswith('solid CAD PETG') for r in posts)
    hardware=[r for n,r in rows.items() if n.startswith(('AuxBolt35_','AuxNut35_'))]
    assert len(hardware)==8 and all(r['basis'].startswith('steel') for r in hardware)
