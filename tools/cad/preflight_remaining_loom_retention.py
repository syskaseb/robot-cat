"""Whole actual roots and36oriented ports BEFORE expensive arm planning.

One coordinated static candidate; no native or motion approval. Keep the
received source carriers. Actual joint poses, whole arms and assembly/stock
remain required. New insulation cylinders are explicit PROJECT reservations.
"""
import itertools
import json
import math
import time
from pathlib import Path
import FreeCAD as A
import Part
import build_complete_source_carriers as B
from loom_land_port import build
P=B.P


def run():
    tick=time.monotonic()
    pf=P.OUT/'remaining-loom-roots-plan.json';ff=P.OUT/'remaining-loom-root-faces.json'
    nf=P.OUT/'complete-source-carriers-native.json';ef=P.OUT/'leg-extension-budget-plan.json'
    cf=P.OUT/'leg-splice-insulation-reference.json';familyfile=P.OUT/'leg-source-near-member-plan.json'
    plan,faces,native,extensions,insulation,family=[json.loads(f.read_text()) for f in (pf,ff,nf,ef,cf,familyfile)]
    assert faces['status']=='EXPOSED_ASSEMBLED_CASE_ROOT_FACES_REST_CLEAR_LAYOUT_OPEN' and not faces['errors']
    reader=B.H.P.SavedShapes();targets,wires,archive,sf,hw=B.current_scene(reader)
    model=P.ROOT/native['native'];assert P.SHA(model)==native['native_sha256']
    for name in reader.doc(model):
        if name.endswith('SourceCarrier') or name.startswith('Ref_'):
            targets[name.removeprefix('Ref_')]=reader.shape(model,name)
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    for route in family['routes']:
        wires[route['loom']]=(P.wire(B.parts_for_loom(family,route['loom'],0,0,axes)+route['source_parts']),3)
    sleeves=[]
    for extension in extensions['four_source_owned_extension_candidates']:
        rows=extension['staggered_core_schedule'];a=A.Vector(*rows[0]['joint_centre_world_mm']);b=A.Vector(*rows[-1]['joint_centre_world_mm'])
        direction=b-a;direction.normalize()
        for row in rows:
            centre=A.Vector(*row['joint_centre_world_mm']);name='SpliceReserve_'+row['wire']
            shape=Part.makeCylinder(5,21,centre-direction*10.5,direction)
            targets[name]=shape
            sleeves.append(dict(name=name,owner_stage=extension['owner'],centre_world_mm=list(centre),axis=list(direction),
                                length_mm=21,diameter_project_mm=10,
                                diameter_not_manufacturer_guarantee=True))
    bounds=B.ImmutableBounds();cache=B.PairReceipts(P.OUT/'remaining-retention-rest-pairs.json',bounds.near)
    chosen={};groups=[];pairs=0
    def contacts(parts,ignore=()):
        nonlocal pairs
        result=[]
        for label,s in parts.items():
            for name,t in itertools.chain(targets.items(),chosen.items()):
                if name in ignore or not bounds.near(s,t,.001):continue
                pairs+=1;gap,volume=cache.check(s,t)
                if volume>1e-5:result.append(dict(a=label,b=name,volume_mm3=volume))
            for name,(wire,radius) in wires.items():
                if not bounds.near(s,wire,radius+.001):continue
                pairs+=1;gap,_=cache.check(s,wire,0,radius)
                if gap<radius-1e-4:result.append(dict(a=label,b=name,gap_mm=gap,required_mm=radius))
        return result
    for group in plan['groups']:
        record=next(r for r in faces['groups'] if r['id']==group['id'])
        seeds=[];rejected=[]
        options=[dict(root_world_mm=record['root_world_mm'])] if 'root_world_mm' in record else record['candidate_faces']
        for option in options:
            if 'root_world_mm' in option:point=option['root_world_mm']
            else:
                n=A.Vector(*option['outward_normal']);c=A.Vector(*option['plane_centre_world_mm'])
                point=list(c+n*(6.2 if group['owner_stage'].endswith('_Knee') else -1))
            x,y,z=point;seed=P.box([x-2,y-3,z-2,x+2,y+3,z+2])
            ignore=[group['preserved_owner']] if 'preserved_owner' in group else []
            hits=contacts({'Seed_'+group['id']:seed},ignore)
            if hits:rejected.append(dict(choice=option,contacts=hits));continue
            score=sum(math.dist(point,r['centre_world_mm']) for r in group['lands'])
            seeds.append((score,point,option))
        if not seeds:
            groups.append(dict(id=group['id'],owner_stage=group['owner_stage'],root_candidates_rejected=rejected,
                               root_world_mm=None,ports=[],error='No complete nominal seed clear, not a path search failure'))
            print('retention root rejected',group['id'],len(rejected),flush=True);continue
        _,start,choice=min(seeds,key=lambda r:r[0]);ports=[]
        for land in group['lands']:
            centre=A.Vector(*land['centre_world_mm']);axis=A.Vector(*land['axis']);axis.normalize()
            radial=A.Vector(*start)-centre;radial-=axis*radial.dot(axis)
            if radial.Length<1:radial=A.Vector(0,0,-1)-axis*axis.dot(A.Vector(0,0,-1))
            radial.normalize();other=axis.cross(radial);orientations=[];rejections=[]
            for angle in (0,math.pi/4,-math.pi/4,math.pi/2,-math.pi/2,math.pi,3*math.pi/4,-3*math.pi/4):
                normal=radial*math.cos(angle)+other*math.sin(angle)
                port=build(land,list(normal))
                parts={'Port_'+land['id']:port['body'],'Band_'+land['id']:port['band']}
                hits=contacts(parts,[group.get('preserved_owner')])
                if hits:rejections.append(dict(angle_rad=angle,contacts=hits));continue
                orientations.append((math.dist(start,port['arrival_world_mm']),list(normal),port))
            if not orientations:
                ports.append(dict(land_id=land['id'],rejected_orientations=rejections,error='No actual complete port orientation clear in current rest scene'))
                print('retention port rejected',land['id'],len(rejections),flush=True);continue
            _,normal,port=min(orientations,key=lambda r:r[0])
            chosen['Port_'+land['id']]=port['body'];chosen['Band_'+land['id']]=port['band']
            ports.append(dict(land_id=land['id'],arrival_world_mm=port['arrival_world_mm'],arrival_normal=normal,
                              recipe=port['recipe'],clear_radial_orientations=len(orientations)))
            print('retention port candidate',land['id'],len(orientations),flush=True)
        groups.append(dict(id=group['id'],owner_stage=group['owner_stage'],root_world_mm=start,root_choice=choice,
                           root_candidates_rejected=rejected,ports=ports))
        cache.save()
    cache.save();errors=[g['id'] for g in groups if not g['root_world_mm'] or any('error' in p for p in g['ports'])]
    files=(pf,ff,nf,model,ef,cf,familyfile,af,archive,sf,B.H.HEAD,hw,Path(__file__),Path(B.__file__),Path(__file__).with_name('loom_land_port.py'))
    result=dict(status='REMAINING_RETENTION_REST_CLEAR_PATHS_MOTION_NATIVE_OPEN' if not errors else 'REMAINING_RETENTION_PREFLIGHT_REJECTED',
                groups=groups,sleeve_reservations=sleeves,pairs=pairs,errors=errors,
                selected=False,W5_complete=False,physical_pass=False,
                scope='Complete nominal root seeds and36ports/ties vs current retained material, complete12source wires and conservative21mm/OD10 PROJECT splice reservations at REST. Not whole arms or joint movement.',
                open=['Full support paths/current all coupled poses and combined port/arm/sleeve material gate',
                      'Delivered joint/insulation OD must fit projectOD10; no guaranteed OD from nominal wall catalogue',
                      'Complete wiring/stock/native selection and physical case retention gates'],
                source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files},
                worker_seconds=round(time.monotonic()-tick,3))
    (P.OUT/'remaining-retention-rest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],errors=errors,pairs=pairs,worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
