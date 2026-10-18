"""Coupled source-clock/whole-station space search after two DFL failures.

Rebuilds fixed surface layers per source; never deletes single-owner union
voxels, which would lose overlapping owners. Reuses unchanged36pose field.
Numerical screens rank proposals only. No native or mechanical acceptance.
"""
import hashlib
import io
import itertools
import json
import math
import time
import zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from scipy.spatial import cKDTree
from scipy.interpolate import RegularGridInterpolator
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_current_candidate_scene import current
from plan_feline_skin_access import surface_samples
from compose_feline_shared_space_atlas import inside_ruled
from receive_feline_global_case_candidates import placement


def cloud(shape,step=2):
    assert shape.isValid() and shape.Solids
    v,f=shape.tessellate(.3)
    return surface_samples(np.array([list(p) for p in v])[np.array(f,dtype=int)],step)


def rotations():
    out=[]
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((-1,1),repeat=3):
            r=np.zeros((3,3))
            for i,j in enumerate(perm):r[j,i]=signs[i]
            if np.linalg.det(r)>.99:out.append(r)
    assert len(out)==24
    return out


def lead(q,d,b,first,R=25.2):
    a=q+first*d;angles=np.linspace(0,math.pi/2,31)
    arc=a+R*np.sin(angles)[:,None]*d+R*(1-np.cos(angles))[:,None]*b
    p=np.vstack((np.linspace(q,a,first+1),arc,np.linspace(arc[-1],arc[-1]+9*b,10)))
    radii=np.full(len(p),2.1);radii[-10:]=4.1
    # Full9mm grip with2mm seat budget, and a6cube head below source Y.
    h=q+4.5*d+np.array([0,-5.1,0])
    head=np.array(list(itertools.product((-3,0,3),repeat=3)))+h
    return np.vstack((p,head)),np.r_[radii,np.zeros(len(head))]


def compatible(a,b,minimum=.2):
    # Source samples do NOT classify solid interiors. This is a loose numeric
    # proposal filter, not an exact contact or global infeasibility result.
    t=cKDTree(b['points']);g,ix=t.query(a['points'],workers=1)
    return float(np.min(g-a['radii']-b['radii'][ix]))>=minimum-1e-6


def main():
    tick=time.monotonic();dest=OUT/'n01-joint-fore-domains.json';assert not dest.exists()
    scene,meta,templates,pins,bus,changed,removed,variable=current()
    capfile=OUT/'n01-global-case-capacity.json';capacity=json.loads(capfile.read_text())
    rawfile=OUT/'n01-shared-space-atlas.json';raw=json.loads(rawfile.read_text());bundle=ROOT/raw['bundle']
    macrofile=OUT/'n01-fore-service-macro.json';macro=json.loads(macrofile.read_text())
    topologyfile=OUT/'n01-fore-topology.json';topology=json.loads(topologyfile.read_text())
    sourcefile=OUT/'n01-s1-current-source-datums.json';source=json.loads(sourcefile.read_text())
    fieldfile=OUT/'n01-global-current-case-field.npz';assert sha(fieldfile)==capacity['field_sha256']
    field=np.load(fieldfile,allow_pickle=False);axes=[field[k] for k in ('x','y','z')]
    grid=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1);query=grid.reshape(-1,3)
    for p in (capfile,rawfile,bundle,macrofile,topologyfile,sourcefile,fieldfile,Path(__file__)):
        pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def gate():
        if time.monotonic()-tick>240:raise TimeoutError('240s joint fore numeric gate; completed proposals retained')
    def packed(doc):
        file=ROOT/doc['bundle'];assert sha(file)==doc['bundle_sha256'];pins[file.relative_to(ROOT).as_posix()]=sha(file)
        result={}
        with zipfile.ZipFile(file) as z:
            for row in doc['parts']:
                blob=z.read(row['entry']);assert hashlib.sha256(blob).hexdigest()==row['sha256']
                s=Part.Shape();s.importBrepFromString(blob.decode('utf-8'));result[row['name']]=(s,row)
        return result
    mp=packed(macro);tp=packed(topology)
    s1names={r['name'] for r in source['source_parts']}
    dflnames={n for n in scene if n=='Ref_Material_D_FL_0_0' or n.startswith('REV3Station:D_FL.')}
    dflcentre=np.array(list(scene['Ref_Material_D_FL_0_0'].BoundBox.Center))
    dflcloud=np.vstack([cloud(scene[n]) for n in sorted(dflnames)])-dflcentre
    source_s1={n:scene[n].copy() for n in s1names}
    conditional_frame={'StructureReserve:Post-69_1','StructureReserve:LowerRail1'}
    excluded=set(macro['retired_source_parts'])|conditional_frame
    fixed={n:s for n,s in scene.items() if n not in excluded};fixedmeta={n:meta[n] for n in fixed}
    s1context=[]
    for n,(s,row) in mp.items():
        if row['group'] in ('D_FL','S1Wire') or '_S1_ring_' in n:continue
        if row['group']=='S1Rigid':s1context.append(cloud(s));continue
        fixed[n]=s;fixedmeta[n]=dict(kind='wire' if row['wire'] else 'material')
    for n,(s,row) in tp.items():
        if row['group']!='ForeFHAC':continue
        fixed[n]=s;fixedmeta[n]=dict(kind='wire' if row['wire'] else 'material')
    cache={r['source']:r for r in capacity['completed_clouds']}
    chunks={k:[] for k in ('material','reservation','curve_hold')};reused=0;new=0
    with zipfile.ZipFile(bundle) as z:
        for n,s in fixed.items():
            gate();row=cache.get(n)
            is_reused=row and row['reused_raw_cloud'] and n not in macro['retired_source_parts'] and n not in tp and n not in mp
            if is_reused:
                r=row['source_record'];blob=z.read(r['entry']);assert hashlib.sha256(blob).hexdigest()==r['sha256']
                p=np.load(io.BytesIO(blob),allow_pickle=False);category=row['category'];reused+=1
            else:
                m=fixedmeta[n];category=('curve_hold' if not s.Solids else 'reservation' if
                    'reservation' in m.get('kind','') or m.get('role')=='ScaffoldPlanning' or
                    n.startswith(('StructureReserve:','PiBudget:')) or n=='RetainedMAINCutForeCap' else 'material')
                if category=='curve_hold':p=np.array([list(v) for e in s.Edges for v in e.discretize(Distance=1)])
                else:p=cloud(s)
                new+=1
            if len(p):chunks[category].append(p)
    interpolators={};counts={}
    for cat,items in chunks.items():
        gate();p=np.vstack(items) if items else np.empty((0,3));counts[cat]=len(p)
        values=cKDTree(p).query(query,workers=1)[0] if len(p) else np.full(len(query),1e6)
        interpolators[cat]=RegularGridInterpolator(axes,values.reshape(grid.shape[:3]),bounds_error=False,fill_value=0)
    for cat in ('motion36','outer'):
        interpolators[cat]=RegularGridInterpolator(axes,field[cat+'_distance'],bounds_error=False,fill_value=0)
    s1tree=cKDTree(np.vstack(s1context))
    def score(p,radius=0,own_ring_mates=False):
        if not np.all(inside_ruled(p)):return -1e6
        values=[float(np.min(interpolators[c](p)-radius-gap)) for c,gap in
                (('material',1.25),('reservation',1.25),('curve_hold',3.35),('motion36',1.25),('outer',3.25))]
        if not own_ring_mates:values.append(float(np.min(s1tree.query(p,workers=1)[0]-radius-1.25)))
        return min(values)
    result=dict(status='RUNNING_JOINT_FORE_DOMAINS',selected=False,N01_complete=False,physical_pass=False,
        source_sha256=pins,unchanged_clouds_reused=reused,changed_clouds_sampled=new,fixed_surface_samples=counts,
        conditional_frame_replacement_NOT_approved=sorted(conditional_frame|variable),
        all_other_scaffold_kept=True,body_and_operator_current_macro_pose_kept=True,
        operator_actual_outside443_97_and_panel_interface_STILL_OPEN=True,
        full_source_R_mm=25.2,source_OD_mm=4.2,prototype_grip_seat_budget_mm=2,
        sample_fields_do_not_classify_solid_interiors=True,screen_is_not_CAD_qualification=True,
        opposite_four_WAGO_ends_and_P_REAR_whole_case_change_OPEN=True,
        full123portions246ends_roots_tools_assembly_stock_OPEN=True,
        dfl_domains=[],source_domains={},joint_assignment=None,errors=[])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    save();domains={};internal={}
    try:
        # DFL whole case plus all five complete current prefixes and after9
        # portions, not only a box or one source land. No native cap yet.
        tested=0;df=[]
        for r in rotations():
            rotated=dflcloud@r.T
            for centre in itertools.product(range(-104,9,16),(44,58,72,86),(14,30,46,62,78,94)):
                gate();tested+=1;p=rotated+centre;s=score(p)
                if s>=0:df.append(dict(score=s,centre_mm=list(centre),rotation_rows=r.tolist(),points=p,radii=np.zeros(len(p))))
        df.sort(key=lambda r:-r['score']);domains['D_FL']=df[:24]
        result['DFL_tested_whole_poses']=tested
        result['dfl_domains']=[{k:v for k,v in r.items() if k not in ('points','radii')} for r in df[:24]];save()
        print('Joint DFL full profile domains',len(df),'/',tested,flush=True)
        from plan_feline_fore_service_macro import rigid_tf
        body=source_s1['Ref_Material_current_S1_body_CP2_0_0'];tf=rigid_tf(body.BoundBox.Center,[15,0,0],180)
        for receipt in source['receipts']:
            gate();endpoint=receipt['endpoint'];ringname=receipt['matching_nominal_source_planes'][0]['part']
            number=int(ringname.split('_ring_')[1].split('_')[0]);screw=source_s1[f'Ref_Material_current_S1_screw_{number}_0_0']
            qold=A.Vector(*receipt['source_point_mm']);dold=A.Vector(*receipt['source_departure'])
            eye=A.Vector(screw.BoundBox.Center.x,qold.y,screw.BoundBox.Center.z)
            assert abs((qold-eye).Length-22.123)<1e-5
            ring=source_s1[ringname];bores=[f.Surface for f in ring.Faces if type(f.Surface).__name__=='Cylinder'
                and abs(f.Surface.Axis.y)>.999 and (eye-f.Surface.Center).cross(f.Surface.Axis).Length<1e-5]
            assert bores,'Ring eye must be actually coaxial before clocking'
            e=np.array(list(tf.multVec(eye)));ringcloud=cloud(ring);choices=[]
            for angle in range(0,360,30):
                d=np.array([math.cos(math.radians(angle)),0,math.sin(math.radians(angle))])
                target=tf.Rotation.inverted().multVec(A.Vector(*d))
                delta=math.degrees(math.atan2(dold.z,dold.x)-math.atan2(target.z,target.x))
                rot=A.Rotation(A.Vector(0,1,0),delta)
                assert rot.multVec(dold).isEqual(target,1e-7)
                clock=A.Placement(eye-rot.multVec(eye),rot);ct=tf*clock
                rc=np.array([list(ct.multVec(A.Vector(*v))) for v in ringcloud])
                if score(rc,own_ring_mates=True)<0:continue
                u=np.array([0,1,0]);v=np.cross(d,u);q=e+22.123*d
                for first in (9,18):
                    for bendangle in range(0,360,45):
                        gate();b=u*math.cos(math.radians(bendangle))+v*math.sin(math.radians(bendangle))
                        p,radii=lead(q,d,b,first);s=score(p,radii)
                        if s<0:continue
                        choices.append(dict(score=s,clock_target_degrees=angle,first_mm=first,bend_degrees=bendangle,
                            point_mm=q.tolist(),departure_axis=d.tolist(),bend_unit=b.tolist(),ring_name=ringname,
                            clock_tf_translation_mm=list(clock.Base),clock_tf_rotation_quaternion=list(clock.Rotation.Q),
                            points=np.vstack((rc,p)),radii=np.r_[np.zeros(len(rc)),radii]))
            choices.sort(key=lambda r:-r['score']);domains[endpoint]=choices[:24]
            result['source_domains'][endpoint]=[{k:v for k,v in r.items() if k not in ('points','radii')} for r in choices[:24]]
            save();print(endpoint,'full R25.2/9grip domains',len(choices),flush=True)
        order=sorted(domains,key=lambda k:len(domains[k]));memo={};visited=0
        def solve(chosen):
            nonlocal visited
            gate();visited+=1
            if len(chosen)==len(order):return chosen
            n=order[len(chosen)]
            for i,candidate in enumerate(domains[n]):
                ok=True
                for key,j in chosen.items():
                    pair=(n,i,key,j)
                    if pair not in memo:memo[pair]=compatible(candidate,domains[key][j])
                    if not memo[pair]:ok=False;break
                if ok:
                    found=solve({**chosen,n:i})
                    if found:return found
            return None
        assignment=solve({});result['joint_assignment']=assignment;result['joint_search_nodes']=visited
        result['numeric_mutual_pair_queries']=len(memo)
        result['status']='JOINT_FORE_NUMERIC_PROPOSAL_EXACT_AND_OPPOSITE_PORTS_OPEN' if assignment else 'NO_JOINT_PROPOSAL_IN_THIS_BOUNDED_NUMERIC_FAMILY'
    except Exception as e:result['errors'].append(repr(e));result['status']='PARTIAL_JOINT_FORE_NUMERIC_DOMAINS'
    save();print(json.dumps({k:result[k] for k in ('status','worker_seconds','joint_assignment','errors')}),flush=True)


if __name__=='__main__':main()
