"""One whole source/side-access stack from the actual bolt and flange limits.

No new lead length/SKU. F0 clocks+90, moves9mm axially past rear strap bolt;
W075 becomes29mm, whole POST andW076 gallery follow the derivedX change.
The explicit SERVICE budget is not an installed eighth component.
"""
import copy,itertools,json,math,zipfile,hashlib
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_battery_f0_joint import path
from plan_feline_n01_shared import pipe
from receive_feline_global_case_candidates import placement
from receive_feline_source_joint import receive


def construction(parts,ends):
    sf=OUT/'n01-BAT-F0-fork-exit.json';r=json.loads(sf.read_text());assert not r['failures']
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    actors={}
    with zipfile.ZipFile(ROOT/r['bundle']) as z:
        for n,row in r['geometry'].items():
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());actors[n]=s
    names={'F0':'Ref_Material_F0_CP2_0_0','XT60':'Ref_Material_XT60_CP2_0_0','POST':'Ref_Material_PostF0Splice_CP2_0_0'}
    u=A.Vector(2**-.5,2**-.5,0);v=A.Vector(u.y,-u.x,0);oldcentre=A.Vector(68,0,-13.75);shift=u*9
    rot=A.Rotation(u,90);tf=A.Placement(oldcentre+shift-rot.multVec(oldcentre),rot)
    body=actors[names['F0']].copy();body.Placement=tf*body.Placement;actors[names['F0']]=body
    datums=copy.deepcopy(r['current_nominal_datums'])
    for k in ('F0_in','F0_out'):datums[k]=list(A.Vector(*datums[k])+shift)
    recipes=copy.deepcopy(r['recipes']);recipes['W075_factory']=path(datums['BAT_plus'],list(u),[('line',29)],12.4)
    rows=recipes['W076_factory']['parts']
    for key in ('start','mid','end'):rows[0][key]=list(A.Vector(*rows[0][key])+shift)
    rows[1]['start']=rows[0]['end']
    for i in (1,2,3):
        for key in ('start','mid','end'):
            if key not in rows[i] or (i==1 and key=='start'):continue
            rows[i][key]=list(A.Vector(*rows[i][key])+A.Vector(shift.x,0,0))
    recipes['W076_factory']['length_mm']-=shift.y
    assert (A.Vector(*rows[0]['start'])-A.Vector(*datums['F0_out'])).Length<1e-6
    for n in ('W075_factory','W076_factory'):actors[n]=pipe(recipes[n]['parts'],1.55)
    for k in ('POST1','POST2'):datums[k]=list(A.Vector(*datums[k])+A.Vector(shift.x,0,0))
    actors[names['POST']].translate(A.Vector(shift.x,0,0))
    for row in recipes['W076_custom_prefix']['parts']:
        for key in ('start','mid','end'):
            if key in row:row[key]=list(A.Vector(*row[key])+A.Vector(shift.x,0,0))
    recipes['W076_custom_prefix']['end']=list(A.Vector(*recipes['W076_custom_prefix']['end'])+A.Vector(shift.x,0,0))
    actors['W076_custom_prefix']=pipe(recipes['W076_custom_prefix']['parts'],2.1)
    centre=oldcentre+shift;frame=placement(np.column_stack((list(u),list(v),[0,0,-1])),list(centre))
    tool=Part.makeBox(24,23.75,20.5,A.Vector(-12,11.25,-10.25));tool.Placement=frame*tool.Placement
    actors['F0SideServiceBudget']=tool
    mouths={frozenset((names['F0'],n)) for n in ('W075_factory','W076_factory')}
    mouths.update(frozenset((names['XT60'],n)) for n in ('W075_factory','W001_ground_prefix'))
    mouths.update(frozenset((names['POST'],n)) for n in ('W076_factory','W076_custom_prefix'))
    own={}
    for a,b in itertools.combinations(actors,2):
        s,t=actors[a],actors[b];minimum=0. if frozenset((a,b)) in mouths else .2 if set((a,b))=={names['F0'],'F0SideServiceBudget'} else 1.25
        gap=s.distToShape(t)[0];c=s.common(t);assert c.isNull() or c.isValid()
        own[a+'|'+b]=dict(ok=gap>=minimum-1e-6 and c.Volume<1e-5,gap_mm=gap,minimum_mm=minimum,common_mm3=c.Volume,
            exact_own_mouth=frozenset((a,b)) in mouths,own_case_access_face=set((a,b))=={names['F0'],'F0SideServiceBudget'})
    return actors,recipes,own,names,datums,dict(unchanged_existing_body_names=[names['XT60'],'W001_ground_prefix'],
        inherited_static_proof=dict(path=sf.relative_to(ROOT).as_posix(),sha256=sha(sf),actors=[names['XT60'],'W001_ground_prefix']),
        installed_source_actor_count=7,service_only_actor_names=['F0SideServiceBudget'],
        F0_clock_deg=90,F0_axial_translation_mm=9,axial_translation_not_incremental_offset_search=True,
        source_bolt_clearance_and_all_mouths_reallocated_together=True,
        service_budget_project_not_exact_manufacturer_cover=True,delivered_cap_tether_tool_fit_gate=True,
        nominal_service_zero_WAGO_disconnects_battery_must_be_unplugged=True,
        builder_dependency_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (
            ROOT/'tools/cad/plan_feline_battery_f0_joint.py',ROOT/'tools/cad/receive_feline_source_joint.py')})


if __name__=='__main__':receive(construction,Path(__file__),'n01-F0-access-stack.json')
