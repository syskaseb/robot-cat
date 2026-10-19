"""Shared rooted carrier planning from received actual material.

One connected network, not translated old towers. Current case-only backers
and independent complete grips remain different interfaces. Surface meshes
only propose paths; every selected whole segment needs an exact solid gate.
No native manufacture, adhesive strength or physical PASS is claimed here.
"""
import hashlib,itertools,json,math,os,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_shared_frame import box
from feline_two_lane_receive import world_context
from feline_solid_distance import bbox_lower_bound
from feline_fore_power_pair import SolidQueries
from receive_feline_global_case_candidates import placement
from plan_axial_source_supports import direct_elbows,arm_box
from source_arm_reservations import Reservations
from plan_remaining_loom_support_paths import search

HALF=[2.,2.,2.]


def archived(doc,key):
    result={};archive=ROOT/doc['bundle'];assert sha(archive)==doc['bundle_sha256']
    with zipfile.ZipFile(archive) as z:
        for r in doc[key]:
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());assert s.isValid() and s.Solids
            result[r['name']]=s
    return result


def case_backer(name,case,choice):
    """Opposite actual lever normal, nominal .5mm case-only adhesive.

    A small replaceable non-operating-face pad, NOT a bought snap-holder or
    adhesive load rating. Actual adhesion/lever operation remain delivery gates.
    """
    b=case.BoundBox;lo=np.array([b.XMin,b.YMin,b.ZMin]);hi=np.array([b.XMax,b.YMax,b.ZMax])
    vertical=choice.get('slot',{}).get('pose_family')=='VERTICAL_DEPARTURE_TWO_SIDE_TIERS'
    recipe=choice.get('base_recipe',choice.get('recipe',{}))
    normal=np.array([0.,-recipe.get('lever_sign',-1),0.]) if vertical else np.array([0.,0.,-1.])
    axis=int(np.argmax(abs(normal)));c=(lo+hi)/2
    c[axis]=(hi[axis] if normal[axis]>0 else lo[axis])+normal[axis]*2.5
    half=np.minimum((hi-lo)/2-2,6);half[axis]=2.
    body=box(c-half,c+half)
    return body,dict(case=name,point_mm=c.tolist(),backer_normal=normal.tolist(),adhesive_project_mm=.5,
        lever_face_opposite=True,not_wire_relief=True,delivered_casing_adhesive_and_operation_gate=True)


def face_entries(shape,goal,limit=6):
    entries=[]
    for face in shape.Faces:
        if type(face.Surface).__name__!='Plane' or face.Area<9:continue
        u,U,v,V=face.ParameterRange;n=face.normalAt((u+U)/2,(v+V)/2)
        p=face.CenterOfMass+n*.75
        seed=arm_box(list(p),list(p),HALF);common=seed.common(shape)
        if not common.isValid() or common.Volume<1:continue
        entries.append((math.dist(list(p),goal),list(p),common.Volume))
    return [dict(point_mm=p,positive_joint_mm3=volume) for _,p,volume in sorted(entries)[:limit]]


def main():
    corridor_gate=OUT/'n01-shared-corridor-allocation.json'
    assert corridor_gate.exists(),'Shared whole-harness corridors/capacity must be allocated BEFORE carrier branches; this draft root planner is not yet qualified'
    assert json.loads(corridor_gate.read_text())['status']=='CURRENT_WHOLE_CORRIDORS_ALLOCATED_BEFORE_ROOTS'
    tick=time.monotonic();foundation_file=OUT/'n01-channelled-foundation-static.json';f=json.loads(foundation_file.read_text())
    assert f['status']=='COMMON_FOUNDATION_CLEAR_NOT_ALL_ROOTS',f['status']
    current_file=OUT/'n01-shared54-current.json';current=json.loads(current_file.read_text())
    proposal=archived(current,'parts');foundation=archived(f,'geometry');world,fixed=world_context()
    assert f['world_source_sha256']==world.pins
    # The four actual seats root every branch in this common network.
    roots=dict(foundation);obstacles={**fixed,**proposal}
    for n in ('StructureReserve:BankBed-1','StructureReserve:BankBed1','ShelfPWM:carrier'):obstacles.pop(n,None)
    for p in world.motion:
        s=world.rest[p['name']].copy();s.Placement=placement(p['r'],p['t'])*s.Placement
        obstacles['Motion:'+p['name']+':'+str(p['pose'])]=s
    outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'))
    goals={};backers={};metadata={r['name']:r for r in current['parts']}
    for name,s in proposal.items():
        if name.startswith('Service:') or ':Anchor:' in name:continue
        if name.endswith(':case'):
            group=metadata[name]['group'];body,recipe=case_backer(name,s,current['chosen'][group])
            key='CaseBacker:'+group;backers[key]=body
            goals[key]=dict(owner=name,kind='case_only_retention',entries=[dict(point_mm=recipe['point_mm'])],recipe=recipe)
        elif name.endswith((':split_common_comb',':common_channelled_cap_exterior',':split_cap_exterior',':saddle')):
            b=s.BoundBox;centre=list(b.Center)
            # Root candidates come from actual flat material, not an empty bbox centre.
            nearest=min(roots.values(),key=lambda q:bbox_lower_bound(q.BoundBox,b)).BoundBox.Center
            goals['GripRoot:'+name]=dict(owner=name,kind='independent_wire_grip',entries=face_entries(s,list(nearest)))
    assert sum(g['kind']=='case_only_retention' for g in goals.values())==22
    assert sum(g['kind']=='independent_wire_grip' for g in goals.values())==52
    files=(foundation_file,current_file,Path(__file__),Path(__file__).with_name('source_arm_reservations.py'),Path(__file__).with_name('plan_remaining_loom_support_paths.py'))
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in files};dest=OUT/'n01-common-retention-roots.json'
    result=dict(status='RUNNING_SHARED_ROOT_NETWORK_NOT_N01',source_sha256=pins,world_source_sha256=world.pins,
        roots={},physical_pass=False,N01_complete=False,native_changed=False,wire_half_mm=HALF,
        adhesive_not_wire_relief=True,goals=goals,errors=[])
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins and result['world_source_sha256']==world.pins
        for key,r in result['roots'].items():
            if not r.get('points_mm'):continue
            if key in backers:roots[key]=backers[key]
            for i,(a,b) in enumerate(zip(r['points_mm'],r['points_mm'][1:])):roots[key+':'+str(i)]=arm_box(a,b,HALF)
        result.setdefault('previous_worker_seconds',[]).append(result['worker_seconds'])
    query=SolidQueries();bounds={n:s.BoundBox for n,s in obstacles.items()};checks=0
    gate_cache=result.setdefault('whole_segment_cache',{})
    def save():
        result.update(worker_seconds=round(time.monotonic()-tick,3),exact_queries_this_slice=checks,
            received=sum(bool(r.get('points_mm')) for r in result['roots'].values()),required=len(goals))
        save_json(dest,result)
    def blocked(s,owner,case=False):
        nonlocal checks
        if time.monotonic()-tick>235:raise TimeoutError('Completed exact whole-segment receipts saved')
        # Geometry + owner/interface key, never an endpoint-only airgap cache.
        key=hashlib.sha256((s.exportBrepToString()+owner+str(case)).encode()).hexdigest()
        if key in gate_cache:return gate_cache[key]
        witness=uncached(s,owner,case);gate_cache[key]=witness;save();return witness
    def uncached(s,owner,case):
        nonlocal checks
        outside=s.copy().cut(outer);assert outside.isNull() or outside.isValid()
        if outside.Volume>1e-5 or s.distToShape(outer.Shells[0])[0]<3.25-1e-6:return dict(other='true_outer',reason='outside_or_skin_margin')
        for n in sorted(obstacles,key=lambda n:bbox_lower_bound(s.BoundBox,bounds[n])):
            if n==owner and not case:continue # Named integral saddle joint only.
            minimum=.5 if n==owner and case else 1.25
            if bbox_lower_bound(s.BoundBox,bounds[n])>=minimum:continue
            q=s;t=obstacles[n]
            if n==world.bus['name']:q=s.copy();q.Placement=world.bus['inverse']*q.Placement;t=world.bus['original']
            checks+=1;gap=query.distance(q,t)
            if gap<minimum-1e-6:return dict(other=n,gap_mm=gap,required_mm=minimum)
        return None
    save()
    try:
        for key,g in sorted(goals.items(),key=lambda kv:min(bbox_lower_bound(proposal[kv[1]['owner']].BoundBox,s.BoundBox) for s in roots.values())):
            if key in result['roots'] and result['roots'][key].get('completed'):continue
            if time.monotonic()-tick>235:raise TimeoutError('Saved whole-root slice; receive before continuing')
            row=dict(points_mm=None,rejections=[],owner=g['owner'],kind=g['kind']);result['roots'][key]=row;save()
            if key in backers and (w:=blocked(backers[key],g['owner'],True)):
                row['rejections'].append(dict(case_backer=w));row['completed']=True;save();continue
            for entry in g['entries'][:3]:
                start=entry['point_mm'];seed=arm_box(start,start,HALF)
                if w:=blocked(seed,g['owner'],g['kind']=='case_only_retention'):
                    row['rejections'].append(dict(entry=start,witness=w));continue
                candidates=sorted(roots.items(),key=lambda q:bbox_lower_bound(q[1].BoundBox,seed.BoundBox))[:4]
                accepted=False
                for root_name,parent in candidates:
                    near=parent.distToShape(Part.Vertex(A.Vector(*start)))[1][0][0]
                    # Destination straddles an actual received face; exact positive union required.
                    finish=list(near);joint=arm_box(finish,finish,HALF).common(parent)
                    if joint.Volume<1:continue
                    if w:=blocked(arm_box(finish,finish,HALF),g['owner'],g['kind']=='case_only_retention'):
                        row['rejections'].append(dict(parent=root_name,witness=w));continue
                    for points in direct_elbows(start,finish):
                        witness=next((w for a,b in zip(points,points[1:]) if (w:=blocked(arm_box(a,b,HALF),g['owner'],g['kind']=='case_only_retention'))),None)
                        if witness:row['rejections'].append(dict(parent=root_name,witness=witness));continue
                        row.update(points_mm=points,parent=root_name,positive_root_joint_mm3=joint.Volume,entry=entry,method='shared_carrier_exact_whole_elbows');accepted=True;break
                    if accepted:break
                if accepted:break
            if row['points_mm']:
                if key in backers:roots[key]=backers[key]
                for i,(a,b) in enumerate(zip(row['points_mm'],row['points_mm'][1:])):roots[key+':'+str(i)]=arm_box(a,b,HALF)
            row['completed']=True
            save();print('Shared root',key,bool(row['points_mm']),result['received'],'/',len(goals),flush=True)
        result['status']='WHOLE_SHARED_ROOT_NETWORK_RECEIVED_CORRIDORS_OPEN' if all(r.get('points_mm') for r in result['roots'].values()) and len(result['roots'])==len(goals) else 'SHARED_ROOT_NETWORK_REQUIRES_CAUSE_CHANGE_NOT_N01'
    except TimeoutError as exc:result.update(status='PARTIAL_SHARED_ROOT_NETWORK',slice_note=str(exc))
    except Exception as exc:result['errors'].append(repr(exc));result['status']='SHARED_ROOT_NETWORK_ERROR'
    save();print(json.dumps(dict(status=result['status'],received=result['received'],required=len(goals),seconds=result['worker_seconds'],errors=result['errors'])),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
