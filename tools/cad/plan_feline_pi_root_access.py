"""Choose one actual material root WITH whole arm, hardware and tool access.

Face centroids may be inside holes. A straddling cube's positive volume is
not evidence that its centre is usable material. No module pose catalogue.
"""
import json,math,time,os
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_usb_service_bight import outer_margin


def material_entries(shape,goal,limit=18):
    entries=[]
    for face in shape.Faces:
        if not isinstance(face.Surface,Part.Plane) or face.Area<9:continue
        u,U,v,V=face.ParameterRange;n=face.normalAt((u+U)/2,(v+V)/2)
        point=face.CenterOfMass-n*.5
        if not shape.isInside(point,1e-7,False):continue
        entries.append(dict(point_mm=list(point),distance_mm=(point-A.Vector(*goal)).Length,strictly_inside_actual_parent=True))
    return sorted(entries,key=lambda r:r['distance_mm'])[:limit]


def profile_gap(solid,curve,radius,minimum=1.25):
    assert curve.isValid() and not curve.Solids and radius>0
    connected=curve.ShapeType in ('Wire','Edge') or len(curve.Wires)==1 and abs(curve.Wires[0].Length-curve.Length)<1e-6
    inside=any(s.isInside(curve.Vertexes[0].Point,1e-7,True) for s in solid.Solids)
    gap=float(curve.distToShape(solid)[0])-radius
    return dict(ok=connected and not inside and gap>=minimum-1e-6,gap_lower_bound_mm=gap,minimum_mm=minimum,
        connected_curve_verified=connected,first_point_inside_material=inside,
        method='Connected curve outside actual closed material with positive continuous boundary distance, minus enclosing profile radius')


def root_arm(point,stem,keepout=None):
    p=np.array(point);stem=np.array(stem);v=stem-p
    s=Part.makeSphere(2,A.Vector(*p)).fuse(Part.makeCylinder(1.5,float(np.linalg.norm(v)),A.Vector(*p),A.Vector(*v))).fuse(Part.makeSphere(1.5,A.Vector(*stem))).removeSplitter()
    if keepout is not None:s=s.cut(keepout).removeSplitter()
    assert s.isValid() and len(s.Solids)==1,'Root arm must be an actual fused solid, not overlapping Compound children'
    return s


def main():
    from plan_feline_long_return import frozen_core
    tick=time.monotonic();pf=OUT/'n01-shared-Pi-carrier-r2-core-received.json';parent=json.loads(pf.read_text())
    world,parts,meta,pins,actors,roles,rows,inverse,outer,baseline,recipe=frozen_core(parent)
    rootname=recipe['Pi_actual_root']['owner'];root=parts[rootname]
    alias_difference=root.cut(parts['ShelfPWM:carrier']).Volume+parts['ShelfPWM:carrier'].cut(root).Volume
    assert alias_difference<1e-5
    obstacles={n:s for n,s in parts.items() if meta[n].get('group')!='PiUpper' and meta[n].get('role')!='BUS' and not n.startswith('CurrentBUS:')}
    for n in recipe['fixed_replaced_names']:obstacles.pop(n,None)
    obstacles.update({n:s for n,s in actors.items() if n!=recipe['Pi_frame_actor']})
    obstacles.pop(rootname,None);obstacles.pop('ShelfPWM:carrier',None)
    records={**meta,**rows};bounds={n:s.BoundBox for n,s in obstacles.items()}
    stem=np.array([-6.,-5.984390365286,105.6]);entries=material_entries(root,stem);assert entries
    b=actors['PiBudget:UnlabelledTopComponentsBudget'].BoundBox
    keepout=Part.makeBox(b.XLength+2.5,b.YLength+2.5,104.8-b.ZMin+1.25,A.Vector(b.XMin-1.25,b.YMin-1.25,b.ZMin-1.25))
    query=SolidQueries();trials=[];accepted=None
    for entry in entries:
        p=np.array(entry['point_mm']);v=stem-p
        candidate=root_arm(p,stem,keepout)
        assert candidate.isValid() and candidate.Solids
        common=root.common(candidate);assert common.isNull() or common.isValid();joint=common.Volume
        if joint<=1e-5:
            trials.append(dict(entry=entry,hold=dict(owner='parent_root',reason='No exact positive material joint despite interior proposal'),positive_joint_mm3=joint));continue
        cb=candidate.BoundBox;hold=None;queries=0
        out=outer_margin(candidate,outer)
        if not out['ok']:hold=dict(owner='outer',**out)
        for n in sorted(obstacles,key=lambda k:bbox_lower_bound(cb,bounds[k])):
            if hold:break
            s=obstacles[n];rr=records.get(n,{}).get('nominal_profile_radius_mm')
            if bbox_lower_bound(cb,bounds[n])>=1.25+(rr or 0):continue
            queries+=1
            if s.Solids:
                if n==world.bus['name']:
                    q=candidate.copy();q.Placement=inverse*q.Placement;gap=query.distance(q,world.bus['original'])
                else:gap=query.distance(candidate,s)
                if n=='Ref_Material_Pi4NominalPCB_0_0':
                    common=candidate.common(s);ok=common.Volume<1e-5
                else:ok=gap>=1.25-1e-6
                r=dict(ok=ok,gap_mm=gap,minimum_mm=1.25)
            elif rr:r=profile_gap(candidate,s,rr)
            else:r=dict(ok=False,reason='Unknown curve profile cannot be treated as empty')
            if not r['ok']:hold=dict(owner=n,**r)
        trials.append(dict(entry=entry,positive_joint_mm3=joint,queries=queries,hold=hold))
        if not hold:accepted=dict(**entry,positive_joint_mm3=joint,stem_mm=stem.tolist(),whole_arm_and_all_static_neighbors_checked=True);break
    result=dict(status='WHOLE_PI_ROOT_ACCESS_PLAN_RECEIVED' if accepted else 'WHOLE_PI_ROOT_REQUIRES_DIFFERENT_PATH_NOT_OFFSETS',accepted=accepted,trials=trials,
        parent_core_file=pf.relative_to(ROOT).as_posix(),source_sha256={**pins,pf.relative_to(ROOT).as_posix():sha(pf),ROOT.joinpath('tools/cad/plan_feline_pi_root_access.py').relative_to(ROOT).as_posix():sha(ROOT/'tools/cad/plan_feline_pi_root_access.py')},
        named_printed_alias_symmetric_difference_mm3=alias_difference,N01_complete=False,physical_pass=False,geometry_changed=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-Pi-root-access-plan.json',result)
    print(json.dumps(dict(status=result['status'],accepted=accepted,trials=len(trials),seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
