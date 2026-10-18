"""Receive one coupled orientation/topology change, not another case offset.

Preserve the prior rejected macro and every unchanged failure. The source
DFL is laid flat as a whole; both fore factory ends use different topology.
No native features, selected assembly, N01 or physical approval is produced.
"""
import hashlib
import itertools
import json
import math
import time
import zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_candidate_collision_scene import Scene
from feline_solid_distance import distance
from check_feline_all_current_lands import near
from check_feline_shared_space import tube_prefix
from plan_feline_front_service_split import line_tube
from plan_feline_fore_vertical_packet import prefix
from receive_feline_global_case_candidates import placement


def grip(q,d,r,radial,head_radial,custom):
    d=A.Vector(d);d.normalize();x=A.Vector(radial);x.normalize()
    assert abs(d.dot(x))<1e-8
    y=d.cross(x);rotation=np.column_stack((list(x),list(y),list(d)))
    assert np.linalg.det(rotation)>1-1e-8
    tf=placement(rotation,list(q));outer=r+2
    annulus=Part.makeCylinder(outer,9).cut(Part.makeCylinder(r,9))
    clip=(Part.makeBox(outer,outer,9) if custom else
          Part.makeBox(outer,2*outer,9,A.Vector(-outer,-outer,0)))
    seat=annulus.common(clip);seat.Placement=tf*seat.Placement
    centre=q+d*(1.25 if custom else 4.5)
    band=Part.makeCylinder(r+1.2,2.5,centre-d*1.25,d).cut(Part.makeCylinder(r,2.5,centre-d*1.25,d))
    h=A.Vector(head_radial);h.normalize();assert abs(h.dot(d))<1e-8
    head=Part.makeBox(6,6,6,A.Vector(-3,-3,-3))
    head.Placement=placement(rotation,list(centre+h*(r+3)))*head.Placement
    assert all(s.isValid() and s.Solids for s in (seat,band,head))
    return seat,band,head


def fore_packet(source,local,centre):
    from plan_feline_fore_vertical_packet import packet
    old,_,_=packet(source,local,centre,112)
    parts={'case':old['case'],'case_retention_ring_budget':old['case_retention_ring_budget']}
    recipes=[]
    from receive_feline_global_case_candidates import matrix_rotation
    r=placement(matrix_rotation([2,0,1]),[0,0,0]).Rotation
    for side in ('in','out'):
        e=local['F_HY.'+side];q=A.Vector(*centre)+r.multVec(A.Vector(*e['local_point_mm']))
        d=r.multVec(A.Vector(*e['departure_axis']));b=A.Vector(1,0,0)
        angle=math.pi/2 if d.z>0 else 0;first=9 if d.z>0 else 34
        factory,end,tangent=prefix(q,d,b,angle,first);tip=end+tangent*14
        sleeve=Part.makeCylinder(2.4,20,end,tangent)
        custom=Part.makeCylinder(1.55,26,tip-tangent*8,tangent)
        parts[side+':factory']=(factory,True);parts[side+':sleeve']=(sleeve,True);parts[side+':custom']=(custom,True)
        for kind,point,axis,rad,seatdir,headdir in (
            ('factory',q,d,1.7,A.Vector(1,0,0),A.Vector(-1,0,0)),
            ('custom',tip+tangent*9,tangent,1.55,
             A.Vector(0,-1,0) if d.z>0 else A.Vector(1,0,0),
             A.Vector(0,0,-1) if d.z>0 else A.Vector(-1,0,0))):
            for name,s in zip(('seat','band','head'),grip(point,axis,rad,seatdir,headdir,kind=='custom')):
                parts[side+':'+kind+'_full_grip_'+name]=(s,False)
        recipes.append(dict(side=side,point_mm=list(q),departure_axis=list(d),bend_unit=list(b),R_mm=6,
            first_mm=first,bend_degrees=math.degrees(angle),factory_grip_line_mm=[list(q),list(q+d*9)],
            sleeve_line_mm=[list(end),list(end+tangent*20)],custom_line_mm=[list(tip-tangent*8),list(tip+tangent*18)],
            custom_grip_line_mm=[list(tip+tangent*9),list(tip+tangent*18)],
            nominal_factory_blank_with3internal_mm=3+first+6*angle+14))
    assert max(r['nominal_factory_blank_with3internal_mm'] for r in recipes)<=84.5
    return parts,recipes


def main():
    tick=time.monotonic();dest=OUT/'n01-fore-topology.json';assert not dest.exists()
    parent=OUT/'n01-fore-service-macro.json';m=json.loads(parent.read_text())
    for n,h in m['source_sha256'].items():assert sha(ROOT/n)==h,n
    bundle=ROOT/m['bundle'];assert sha(bundle)==m['bundle_sha256']
    scene=Scene();original_dfl={n:s.copy() for n,s in scene.parts.items() if n=='Ref_Material_D_FL_0_0' or n.startswith('REV3Station:D_FL.')}
    for n in m['retired_source_parts']:scene.parts.pop(n);scene.meta.pop(n)
    retained={};meta={};proposal={};rows={}
    with zipfile.ZipFile(bundle) as z:
        for row in m['parts']:
            if row['group'] in ('D_FL','ForeFHAC'):continue
            raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode('utf-8'))
            retained[row['name']]=s;meta[row['name']]=row
    scene.parts.update(retained)
    scene.meta.update({n:dict(kind='wire' if r['wire'] else 'material',wire_owner=n if r['wire'] else None) for n,r in meta.items()})
    def put(n,s,group,wire=False):
        assert s.isValid() and s.Solids,n
        proposal[n]=s;rows[n]=dict(group=group,wire=wire)
    case=original_dfl['Ref_Material_D_FL_0_0'];centre=case.BoundBox.Center
    rotation=A.Rotation(A.Vector(1,0,0),90);tf=A.Placement(centre-rotation.multVec(centre),rotation)
    for n,s in original_dfl.items():s.Placement=tf*s.Placement;put(n,s,'D_FL',n!='Ref_Material_D_FL_0_0')
    extra=OUT/'n01-all-extra-interface-contract.json';e=json.loads(extra.read_text())
    local={x['endpoint']:x for sec in e['sections'] for x in sec['ends'] if x.get('local_point_mm') is not None}
    fore,recipes=fore_packet(scene.templates['F_HY'][1],local,m['fore_centre_mm'])
    for n,(s,w) in fore.items():put('ForeFHAC:'+n,s,'ForeFHAC',w)
    scene.bounds={n:s.BoundBox for n,s in scene.parts.items()}
    pins=dict(scene.pins)
    for p in (parent,bundle,extra,Path(__file__),Path(__file__).with_name('plan_feline_fore_vertical_packet.py')):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    carried=[f for f in m['failures'] if not (f['part'].startswith('REV3Station:D_FL.') or f['part']=='Ref_Material_D_FL_0_0' or f['part'].startswith('ForeFHAC:'))]
    result=dict(status='RUNNING_FORE_TOPOLOGY',selected=False,N01_complete=False,physical_pass=False,
        source_sha256=pins,carried_unchanged_failures=carried,DFL_rotation_X_degrees=90,DFL_same_centre_mm=list(centre),
        fore_recipes=recipes,receipts=[],failures=[],new_pairs=[],errors=[],
        ring_panel_partner_root_and_all_other_roots_OPEN=True,full_DFL_group_cap_levers_and_mount_OPEN=True,
        S1_four_full_R25_2_and_opposite_power_ports_OPEN=True,whole123portions246ends_OPEN=True)
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>240:raise TimeoutError('240s coupled topology cap; completed receipts retained')
    oldreceipts={r['part']:r for r in m['receipts']};save()
    try:
        for n,s in proposal.items():
            gate()
            if n in ('ForeFHAC:case','ForeFHAC:case_retention_ring_budget') or ':factory_full_grip_' in n:
                previous=oldreceipts[n];result['receipts'].append(dict(part=n,unchanged_receipt=previous))
                if previous.get('failure'):result['failures'].append(dict(part=n,unchanged_failure=True,**previous['failure']))
                continue
            failure,queries=scene.receive(s,wire=rows[n]['wire'])
            result['receipts'].append(dict(part=n,failure=failure,completed_queries=queries))
            if failure:result['failures'].append(dict(part=n,**failure))
            save();print(n,'CLEAR' if not failure else failure,flush=True)
        for a,b in itertools.combinations(proposal,2):
            gate();ra,rb=rows[a],rows[b]
            if ra['group']==rb['group']:continue
            minimum=.2 if ra['wire'] and rb['wire'] else 1.25
            if not near(proposal[a].BoundBox,proposal[b].BoundBox,minimum):continue
            g=distance(proposal[a],proposal[b]);q=dict(a=a,b=b,gap_mm=g,minimum_mm=minimum)
            result['new_pairs'].append(q)
            if g<minimum-1e-5:result['failures'].append(dict(kind='changed_shared_pair_gap',**q))
        result['status']='CHANGED_FORE_TOPOLOGY_REJECTED_OR_OPEN' if result['failures'] else 'CHANGED_FORE_EXTERNAL_SPACE_CLEAR_OTHER_MACRO_HOLDS_OPEN'
    except Exception as e:result['errors'].append(repr(e));result['status']='PARTIAL_FORE_TOPOLOGY'
    outbundle=OUT/'n01-fore-topology.breps.zip'
    with zipfile.ZipFile(outbundle,'w',compression=zipfile.ZIP_DEFLATED) as z:
        result['parts']=[]
        for i,(n,s) in enumerate(proposal.items()):
            raw=s.exportBrepToString().encode();entry=f'{i:04}.brep';z.writestr(entry,raw)
            result['parts'].append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),**rows[n]))
    result['bundle']=outbundle.relative_to(ROOT).as_posix();result['bundle_sha256']=sha(outbundle);save()
    print(json.dumps({k:result[k] for k in ('status','worker_seconds','failures','errors')}),flush=True)


if __name__=='__main__':main()
