"""Seat AUX on actual structural material and include all3R15 departures.

The higher straight-only proposal isn't a wiring result. Start every escape
at its OWN full9 land, shorten only uncommitted custom straight allocation,
and turn inward before roof/skin. No factory shortening or bought-part edit.
"""
import copy,gzip,hashlib,json,math,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load
from plan_feline_n01_shared import pipe
from feline_source_restraint_plan import joined,box
from receive_feline_aux_vertical_unit import material_spacing
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from feline_atomic_save import save_json


def construct(fixed,pins,stem='n01-AUX-upper-seat-escape',height_from_joint=False):
    tick=time.monotonic();sf=OUT/'n01-AUX-upper-supported-plan.json';old=json.loads(sf.read_text());actors=load(old)
    oldroot=actors.pop('AuxGrip:UpperRoot');rows={g['name']:dict(g) for g in old['geometry']}
    chosen_z=55.;shared_height=None
    if height_from_joint:
        host=old['root_host'];hb=fixed[host].BoundBox;y=oldroot.BoundBox.Center.y
        patch=fixed[host].copy().common(box([hb.XMax-3,y-1.5,30],[hb.XMax,y+1.5,50]))
        assert patch.isValid() and patch.Solids and patch.Volume>1
        base_rel=actors['AuxInboard:Carrier'].BoundBox.ZMin-old['actual_AUX_PCB_centre_mm'][2]
        highest_arc_rel=max(e['jacket_grip9_mm'][-1][2]-old['actual_AUX_PCB_centre_mm'][2]+15+1.25 for e in old['updates'].values())
        shared_height=[patch.BoundBox.ZMin+.5-(base_rel+2),
            min(patch.BoundBox.ZMax-.5-base_rel,112-3.25-highest_arc_rel)]
        assert shared_height[0]<shared_height[1],shared_height
        chosen_z=sum(shared_height)/2
    shift=A.Placement(A.Vector(0,0,chosen_z-old['actual_AUX_PCB_centre_mm'][2]),A.Rotation())
    for s in actors.values():s.Placement=shift*s.Placement
    updates=copy.deepcopy(old['updates']);escapes={};changed=[]
    for e in updates.values():
        for key in ('point_mm','jacket_routing_point_mm','routing_exit_mm'):
            if e.get(key) is not None:e[key]=list(shift.multVec(A.Vector(*e[key])))
        e['jacket_grip9_mm']=[list(shift.multVec(A.Vector(*p))) for p in e['jacket_grip9_mm']]
        name=e['prefix_geometry_owner'];wire=name.split(':')[1]
        a=np.asarray(e['jacket_routing_point_mm']);p=np.asarray(e['jacket_grip9_mm'][-1]);u=np.asarray(e['routing_exit_axis'])
        assert np.allclose(u,[0,0,1]);v=np.asarray([-2**-.5,2**-.5,0.]);R=15.
        first=dict(kind='line',start=a.tolist(),end=p.tolist())
        actors[name]=pipe([first],1.25);changed.append(name)
        mid=p+R*math.sqrt(.5)*u+R*(1-math.sqrt(.5))*v;end=p+R*u+R*v
        arc=dict(kind='arc',start=p.tolist(),mid=mid.tolist(),end=end.tolist(),radius_mm=R)
        n='AuxEscape:'+wire;actors[n]=pipe([arc],1.25);rows[n]=dict(name=n,kind='wire',wire=wire);changed.append(n)
        e.update(routing_exit_mm=end.tolist(),routing_exit_axis=v.tolist(),received_prefix_R_mm=R,
            prefix_geometry_owner=n,prefix_geometry_owners=[name,n],
            source_prefix_length_mm=float(np.linalg.norm(p-a)+R*math.pi/2),
            routing_boundary_status='AUX_INWARD_R15_AFTER_EXACT_FULL9_PLAN_NOT_WORLD_RECEIVED')
        escapes[wire]=dict(straight=first,arc=arc,full_grip_end_is_arc_start=True,extra_mandatory_straight_after9=False)
    # The old4.58mm air gap disappears at this structural seat. A short tab
    # occupies ONLY real rail/base material, not the entire carrier bbox.
    host=old['root_host'];hb=fixed[host].BoundBox
    y=oldroot.BoundBox.Center.y;carrier=actors['AuxInboard:Carrier'];z=carrier.BoundBox.ZMin
    tab=box([hb.XMax-3,y-1.5,z],[hb.XMax,y+1.5,z+2])
    ca=tab.copy().common(carrier.copy()).Volume;ch=tab.copy().common(fixed[host].copy()).Volume
    assert ca>1 and ch>1,(ca,ch)
    actors['AuxGrip:UpperRoot']=tab;rows['AuxGrip:UpperRoot']=dict(name='AuxGrip:UpperRoot',kind='PETG');changed.append('AuxGrip:UpperRoot')
    printing=set(old['print_group']);whole=joined([actors[n] if n in actors else fixed[n] for n in printing])
    bb=whole.BoundBox;assert max(bb.XLength,bb.YLength,bb.ZLength)<250
    q=SolidQueries();checks={};names=list(actors)
    def save_local(status):
        result=dict(status=status,checks=checks,failures=[k for k,v in checks.items() if not v['ok']],
            changed_actor_names=changed,rigid_unchanged33_and_custom_straight_material_subsets_reused=True,
            full9_and_selected_source_forms_preserved=True,N01_complete=False,physical_pass=False,
            worker_seconds=round(time.monotonic()-tick,3))
        save_json(OUT/(stem+'-local-progress.json'),result);return result
    for a in changed:
        for b in names:
            if a==b or a in printing and b in printing:continue
            if a+'|'+b in checks or b+'|'+a in checks:continue
            ar,br=rows[a],rows[b];same=ar.get('wire') and ar.get('wire')==br.get('wire')
            if a.startswith('AuxSource:') and same:continue # smaller own source profile, retained intrinsic mates
            limit=0. if same and b in ('AuxSource:'+ar['wire']+':jacket','AuxGrip:'+ar['wire']+':pad') else .2 if same else material_spacing(a,ar,b,br)
            if bbox_lower_bound(actors[a].BoundBox,actors[b].BoundBox)>limit+1e-6:continue
            gap=q.distance(actors[a],actors[b]);row=dict(ok=gap>=limit-1e-6,gap_mm=gap,minimum_mm=limit)
            if limit==0:
                common=actors[a].copy().common(actors[b].copy()).Volume;row.update(common_mm3=common,ok=common<1e-5)
            checks[a+'|'+b]=row
            if not row['ok']:
                print('AUX_SEAT_ESCAPE_LOCAL_HOLD',a,b,row,flush=True);return save_local('AUX_SEAT_ESCAPE_LOCAL_HOLD')
    dest=OUT/(stem+'-plan.json');assert not dest.exists();bundle=dest.with_suffix('.breps.zip');geometry=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as zz:
        for n,s in actors.items():
            assert s.isValid() and s.Solids,n
            raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';zz.writestr(entry,raw)
            geometry.append(dict(rows[n],entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    p=copy.deepcopy(old);p.update(status='WHOLE_AUX_SEATED_FOUNDATION_WITH_THREE_R15_ESCAPES_WORLD_TOOLS_OPEN',geometry=geometry,
        updates=updates,bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),
        actual_AUX_PCB_centre_mm=[140.,-64.,chosen_z],source_escapes=escapes,changed_local_actor_names=[],
        shared_full_escape_roof_and_actual_material_seat_Z_interval_mm=shared_height,
        whole_fore_support_envelope_mm=[bb.XLength,bb.YLength,bb.ZLength],
        root_carrier_common_mm3=ca,root_host_common_mm3=ch,
        source_sha256={**pins,**{str(f.relative_to(ROOT)):sha(f) for f in (sf,ROOT/old['bundle'],Path(__file__))}},
        construction_worker_seconds=round(time.monotonic()-tick,3),N01_complete=False,physical_pass=False)
    save_json(dest,p)
    lr=save_local('AUX_UPPER33_SUBSETS_WITH_FULL_R15_ESCAPES_AND_ROOT_LOCAL_RECEIVED')
    lr.update(source_plan=dest.relative_to(ROOT).as_posix(),source_plan_sha256=sha(dest),source_bundle_sha256=p['bundle_sha256'])
    save_json(OUT/(stem+'-local-received.json'),lr)
    print(p['status'],len(actors),ca,ch,p['construction_worker_seconds'],flush=True);return p
