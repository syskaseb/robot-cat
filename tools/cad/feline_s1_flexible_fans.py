"""Four actual S1 mouths, flexible sweep angles and after-bend saddles.

One current fore-bay proposal. No old12mm/quarter90 template reruns, unsigned
distance acceptance or independent movement of purchased rings. Full roots,
tools and other47 variable kits are a subsequent shared N01 gate, not hidden.
"""
import hashlib
import itertools
import json
import math
import sys
import time
import zipfile
from pathlib import Path

import FreeCAD as A
import Part
import numpy as np

from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed
from plan_feline_front_bulkhead_architecture import tube
from feline_solid_distance import distance,bbox_lower_bound
from receive_feline_global_case_candidates import placement


LOW=np.array([-141.5,-100,-48])+3.25
HIGH=np.array([183.5,100,112])-3.25


def curve(recipe,pose,packet,bend_degrees,sweep_degrees):
    r=np.array(pose['rotation_rows']);q=(np.array(recipe['point_mm'])-packet['centre_mm'])@r.T+pose['centre_mm']
    d=r@np.array(recipe['departure_axis']);d/=np.linalg.norm(d)
    n=np.array([0.,1.,0.]);assert abs(n@d)<1e-6
    return mouth_curve(recipe['ref'],q,d,n,bend_degrees,sweep_degrees)


def mouth_curve(ref,q,d,normal,bend_degrees,sweep_degrees,first=3.):
    """Actual current world mouth; arbitrary proper3D bend plane.

    The old helper's fixedY normal is not valid after the switch's axial
    rotation. Keep R25.2/first3/full9; do not optimize by shrinking wire.
    """
    q=np.asarray(q,dtype=float);d=np.asarray(d,dtype=float);d=d/np.linalg.norm(d)
    n=np.asarray(normal,dtype=float);n=n-d*(n@d)
    assert np.linalg.norm(n)>1e-7
    n/=np.linalg.norm(n)
    v=np.cross(d,n);phi=math.radians(bend_degrees)
    b=math.cos(phi)*n+math.sin(phi)*v
    assert first>=0
    R=25.2;angle=math.radians(sweep_degrees);a=q+first*d
    angles=np.linspace(0,angle,65)
    arc=a+R*np.sin(angles)[:,None]*d+R*(1-np.cos(angles))[:,None]*b
    tangents=np.cos(angles)[:,None]*d+np.sin(angles)[:,None]*b
    tangent=tangents[-1];end=arc[-1];tip=end+9*tangent
    points=np.vstack((q,a,arc,tip));directions=np.vstack((d,d,tangents,tangent))
    radial=2.1*np.sqrt(np.maximum(0,1-directions**2))
    sample_inside=bool(np.all(points-radial>=LOW-1e-6) and np.all(points+radial<=HIGH+1e-6))
    return dict(ref=ref,point_mm=q.tolist(),departure_axis=d.tolist(),bend_unit=b.tolist(),
                bend_degrees=bend_degrees,sweep_degrees=sweep_degrees,R_mm=R,first_project_mm=first,
                grip_start_mm=end.tolist(),grip_end_mm=tip.tolist(),grip_axis=tangent.tolist(),
                full_grip_mm=9,jacket_radius_mm=2.1,sample_inside_absolute_envelope=sample_inside)


def wire_shape(row):
    q,d,b=(A.Vector(*row[k]) for k in ('point_mm','departure_axis','bend_unit'))
    first=row.get('first_project_mm',3);a=q+d*first;t=math.radians(row['sweep_degrees']);R=row['R_mm']
    mid=a+R*math.sin(t/2)*d+R*(1-math.cos(t/2))*b
    end=A.Vector(*row['grip_start_mm']);tip=A.Vector(*row['grip_end_mm'])
    edges=([Part.makeLine(q,a)] if first>1e-8 else [])+[Part.Arc(a,mid,end).toShape(),Part.makeLine(end,tip)]
    return tube(Part.Wire(edges),2.1)


def half_ring(q,axis,n,inner,outer,length,sign=-1):
    q,axis,n=(A.Vector(*x) for x in (q,axis,n));u=axis.cross(n)
    edges=[Part.Arc(q+outer*u,q+sign*outer*n,q-outer*u).toShape(),
           Part.makeLine(q-outer*u,q-inner*u),
           Part.Arc(q-inner*u,q+sign*inner*n,q+inner*u).toShape(),
           Part.makeLine(q+inner*u,q+outer*u)]
    s=Part.Face(Part.Wire(edges)).extrude(axis*length)
    assert s.isValid() and len(s.Solids)==1
    return s


def saddle_shapes(row,normal_angle,head_angle):
    radius=row.get('jacket_radius_mm',2.1)
    t=np.array(row['grip_axis']);q=np.array(row['grip_start_mm'])
    n=np.array([-1.,0,0]);n=n-t*(n@t)
    if np.linalg.norm(n)<.1:n=np.array([0.,0,-1]);n=n-t*(n@t)
    n/=np.linalg.norm(n);v=np.cross(t,n);a=math.radians(normal_angle)
    n=math.cos(a)*n+math.sin(a)*v;u=np.cross(n,t)
    lower=half_ring(q,t,n,radius+.15,radius+2,9)
    qb=q+t*3.25
    bandparts=[half_ring(qb,t,n,radius+2,radius+3.2,2.5),half_ring(qb,t,n,radius,radius+1.2,2.5,1)]
    matrix=A.Matrix()
    assert np.linalg.det(np.column_stack((u,n,t)))>1-1e-7,'Strap frame must be proper, not a reflection'
    for i in range(3):
        for j,col in enumerate((u,n,t)):setattr(matrix,f'A{i+1}{j+1}',col[i])
    rot=A.Rotation(matrix)
    for side in (-1,1):
        # Strap shoulders lie ABOVE the saddle's flat rim, never half inside
        # its PETG wall. Lower/upper arcs meet these shoulders at full faces.
        lo=qb+side*radius*u
        if side<0:lo=qb-(radius+3.2)*u
        sh=Part.makeBox(3.2,1.2,2.5);sh.Placement=A.Placement(A.Vector(*lo),rot);bandparts.append(sh)
    band=bandparts[0].multiFuse(bandparts[1:]).removeSplitter()
    a=math.radians(head_angle);radial=radius if math.sin(a)>=0 else radius+2
    h=q+4.5*t+(radial+1.2+3)*(math.cos(a)*u+math.sin(a)*n)
    head=Part.makeBox(6,6,6,A.Vector(*(h-3)))
    return {'saddle':lower,'band_budget':band,'head_budget':head}


def absolute_inside(s):
    b=s.BoundBox
    return all(x>=v-1e-6 for x,v in zip((b.XMin,b.YMin,b.ZMin),LOW)) and all(x<=v+1e-6 for x,v in zip((b.XMax,b.YMax,b.ZMax),HIGH))


def main():
    from feline_candidate_collision_scene import Scene
    from feline_pwm_board_shelf import build,source_inputs
    tick=time.monotonic();dest=OUT/'n01-s1-flexible-fore-fans.json';archive=OUT/'n01-s1-flexible-fore-fans.breps.zip'
    # Never start detailed fans after only900critical/first-failure checks.
    # All retained owners in the current whole source plan must be received.
    core=OUT/'n01-shared-power-backplane.json'
    assert core.exists(),'Complete shared source/board core gate BEFORE source fans'
    coreproof=json.loads(core.read_text())
    assert coreproof.get('whole_power_core_gate_complete') is True,'Shared power case gate not closed; do not resume the rejected fan family'
    previous=None
    if dest.exists():
        assert '--receive-partial' in sys.argv,'Receive previous result before duplicating flexible fans'
        previous=json.loads(dest.read_text());assert previous['status']=='PARTIAL_FLEXIBLE_SOURCE_DOMAINS'
    pwmfile=OUT/'n01-pwm-board-shelf.json';pwm,pwmparts,pwmrows=packed(pwmfile)
    assert pwm['status']=='OWNER_OWN_AND_FIXED_CLEAR_SHARED47_OUTER_PENDING'
    sourcepath=OUT/'n01-source-saddles-whole-joint.json';source=json.loads(sourcepath.read_text())
    packetpath=OUT/'n01-intrinsic-s1-whole-pose.json';packet=json.loads(packetpath.read_text())
    pose=source['fore_outboard_budget']['pose']
    _,_,s1,_=build(*source_inputs())
    world=Scene();proof=json.loads((OUT/'n01-flat20-field-modulejoint.json').read_text())
    for file,groups in (('n01-fore-service-macro.json',{'F_HP','F_TY'}),('n01-fore-topology.json',{'ForeFHAC'})):
        _,extra,rows=packed(OUT/file)
        for n,s in extra.items():
            if rows[n]['group'] in groups:world.parts[n]=s;world.meta[n]=rows[n]
    fixed={r['source']:world.parts[r['source']] for r in proof['material_clouds']
           if r['category']!='S1_mating_context' and r['source'] not in pwm['retired_whole_owner']}
    fixed.update(s1);fixed.update(pwmparts)
    datum=json.loads((OUT/'n01-s1-current-source-datums.json').read_text())
    mates={r['endpoint']:r['matching_nominal_source_planes'][0]['part'] for r in datum['receipts']}
    service={}
    for side,i in itertools.product(('L','R'),range(1,7)):
        key=side+str(i);b=world.parts[f'Ref_Material_F_{key}_CP2_ATO_0_0'].optimalBoundingBox();sign=1 if side=='L' else -1
        service['ATO:'+key]=Part.makeBox(b.XLength,b.YLength+60,b.ZLength,A.Vector(b.XMin,b.YMin if sign>0 else b.YMin-60,b.ZMin))
        service['Tool:'+key]=Part.makeBox(25,66,12,A.Vector(b.Center.x-12.5,b.YMax-6 if sign>0 else b.YMin-60,b.Center.z-6))
    rec=dict(status='RUNNING_FLEXIBLE_SOURCE_FANS',pose=pose,selected=False,N01_complete=False,physical_pass=False,
             first3_is_project_transition_not_supplier_length=True,full9mm_grip_AFTER_bend=True,
             roots_tools_other47_whole_joint_and_true_outer_STILL_OPEN=True,domains={},rejections={},
             actual_pairs=0,wire_attempts=0,complete_ports=[],completed_wire_families={},parts=[],errors=[],
             source_sha256={**world.pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in (pwmfile,ROOT/pwm['bundle'],sourcepath,packetpath,Path(__file__))}})
    if previous:
        assert rec['source_sha256']==previous['source_sha256'],'Changed source requires affected receiver, not old fan requery'
        rec=previous;assert sha(archive)==rec['bundle_sha256']
        rec.setdefault('previous_worker_seconds',[]).append(rec['worker_seconds'])
        rec['status']='RUNNING_FLEXIBLE_SOURCE_FANS'
    def save():
        rec['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(rec,indent=2)+'\n',encoding='utf-8',newline='\n')
    def reject(ref,why):
        d=rec['rejections'].setdefault(ref,{});d[why]=d.get(why,0)+1
    def receive(s,ref,iswire=False):
        if not absolute_inside(s):return 'Absolute325x200x160+3.25'
        for other,t in fixed.items():
            wire=other in pwmrows and pwmrows[other]['kind'] in ('wire','bare') or other in world.meta and world.wire(other)
            minimum=.2 if iswire and wire else 1.25
            mate=iswire and other==mates[ref]
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum and not mate:continue
            if not t.isValid() or not t.Solids:return 'Invalid_or_curve_owner:'+other
            q=s
            if other==world.bus['name']:
                q=s.copy();q.Placement=world.bus['inverse']*q.Placement;t=world.bus['original']
            gap=distance(q,t);rec['actual_pairs']+=1
            if mate:
                if gap<1e-6:
                    common=q.copy().common(t.copy());assert common.isValid()
                    if common.Volume>1e-5:return 'Own_crimp_material_penetration:'+other
            elif gap<minimum-1e-6:return 'Actual_owner:'+other
        for other,t in service.items():
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=.01:continue
            rec['actual_pairs']+=1
            if distance(s,t)<.01-1e-6:return 'ATO_access:'+other
        for p in world.motion:
            if bbox_lower_bound(s.BoundBox,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
            q=s.copy();q.Placement=placement(p['r'],p['t']).inverse()*q.Placement
            rec['actual_pairs']+=1
            if distance(q,world.rest[p['name']])<1.25-1e-6:return 'Actual_motion36:'+p['name']+':'+str(p['pose'])
        return None
    save()
    try:
        with zipfile.ZipFile(archive,'a' if previous else 'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for recipe in packet['recipes']:
                ref=recipe['ref']
                if ref in rec['complete_ports']:continue
                accepted=rec['domains'].setdefault(ref,[])
                wirechoices=len({(r['bend_degrees'],r['sweep_degrees']) for r in accepted})
                done=rec['completed_wire_families'].setdefault(ref,[])
                for sweep,bend in itertools.product((45,60,75,90,120),(0,45,-45,90,-90,30,-30,60,-60)):
                    identity=str(sweep)+':'+str(bend)
                    if identity in done:continue
                    if time.monotonic()-tick>240:raise TimeoutError('240s flexible-source budget; receive saved completed ports')
                    row=curve(recipe,pose,packet,bend,sweep);rec['wire_attempts']+=1
                    if not row['sample_inside_absolute_envelope']:reject(ref,'Sample_outside_absolute');done.append(identity);continue
                    wire=wire_shape(row);why=receive(wire,ref,True)
                    if why:reject(ref,why);done.append(identity);save();continue
                    rowchoices=0
                    for normal,head in itertools.product((0,90,180,270),(0,90,180,270)):
                        parts=saddle_shapes(row,normal,head)
                        # Own saddle is a channel mate; head must not punch
                        # into the jacket or saddle. Closed band may touch.
                        if distance(wire,parts['head_budget'])<.2-1e-6 or distance(parts['saddle'],parts['head_budget'])<.2-1e-6:
                            reject(ref,'Own_full_head_gap');continue
                        own=wire.copy().common(parts['saddle'].copy());assert own.isNull() or own.isValid()
                        if own.Volume>1e-5:reject(ref,'Own_jacket_saddle_penetration');continue
                        why=next((w for s in parts.values() if (w:=receive(s,ref))),None)
                        if why:reject(ref,why);continue
                        candidate=dict(row,normal_degrees=normal,head_degrees=head,parts=[],common_carrier_root_OPEN=True)
                        for kind,s in {'wire':wire,**parts}.items():
                            assert s.isValid() and s.Solids
                            blob=s.exportBrepToString().encode();entry=f'{len(rec["parts"]):04d}.brep';z.writestr(entry,blob)
                            record=dict(name=ref+':'+str(len(accepted))+':'+kind,entry=entry,sha256=hashlib.sha256(blob).hexdigest(),kind=kind)
                            candidate['parts'].append(record);rec['parts'].append(record)
                        accepted.append(candidate);rowchoices+=1;save()
                        if rowchoices>=2:break
                    if rowchoices:wirechoices+=1
                    done.append(identity);save()
                    if len(accepted)>=8 and wirechoices>=3:break
                rec['domains'][ref]=accepted;rec['complete_ports'].append(ref);save()
                print('Flexible S1',ref,len(accepted),'full wire/saddle/band/head domains',flush=True)
            rec['status']='FLEXIBLE_SOURCE_DOMAINS_RECEIVED_SHARED_ROOTS_TOOLS_OTHER47_OPEN'
    except TimeoutError as e:rec['status']='PARTIAL_FLEXIBLE_SOURCE_DOMAINS';rec['stop_note']=str(e)
    except Exception as e:rec['status']='FLEXIBLE_SOURCE_ERROR_NOT_CLEARANCE';rec['errors'].append(repr(e))
    rec.update(bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive))
    save();print(json.dumps(dict(status=rec['status'],seconds=rec['worker_seconds'],ports={k:len(v) for k,v in rec['domains'].items()},pairs=rec['actual_pairs'],errors=rec['errors'])),flush=True)


if __name__=='__main__':
    import os
    print('WORKER_PID',os.getpid(),flush=True)
    main()
