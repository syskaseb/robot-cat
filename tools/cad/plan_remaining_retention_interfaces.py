"""Choose all retention roots/ports together using sampled actual motion.

This complements the shared routing plan with full seat/band/arrival shapes.
Nominal reservations and supplier data remain distinct; no physical approval.
"""
import copy
import itertools
import json
import math
import sys
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import build_complete_source_carriers as B
from loom_land_port import build
from compact_loom_land_port import build as compact_build
from diagnose_remaining_support_endpoints import transform,moved

P=B.P
ANGLES=(-15,0,15)


def run():
    tick=time.monotonic()
    rf=P.OUT/'remaining-retention-rest.json';pf=P.OUT/'remaining-loom-roots-plan.json'
    ff=P.OUT/'leg-source-near-member-plan.json';nf=P.OUT/'front-fixed-port-clearance-native.json'
    rest,plan,family,native=[json.loads(f.read_text()) for f in (rf,pf,ff,nf)]
    compact_mode='--compact-failed' in sys.argv
    basefile=P.OUT/'remaining-retention-motion.json'
    previous=json.loads(basefile.read_text()) if compact_mode else None
    failed_ids={p['land_id'] for g in previous['groups'] for p in g['ports'] if p.get('error')} if previous else set()
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    reader=B.H.P.SavedShapes();targets,wires,archive,sf,hw=B.current_scene(reader)
    zf=P.ROOT/'hardware/simulation/v35/inputs.zip'
    with zipfile.ZipFile(zf) as z:members=json.loads(z.read('geometry.json'))['components']
    membership={'P0_'+r['name']:tuple(r['stage'].split('_')[1:]) for r in members if r['stage'].startswith('Motion_')}
    model=P.ROOT/native['native'];assert P.SHA(model)==native['native_sha256']
    for name in reader.doc(model):
        if not (name.endswith('SourceCarrier') or name.startswith('Ref_')):continue
        actual=name.removeprefix('Ref_');targets[actual]=reader.shape(model,name)
        if actual.endswith(('SourceCarrier','SourceCaseBond')):
            leg=actual.removesuffix('SourceCarrier').removesuffix('SourceCaseBond')
            code=next(r['cad_code'] for r in family['hips'] if r['physical_leg']==leg)
        else:
            code=next(r['cad_code'] for r in family['hips'] if r['loom']==actual.removesuffix('IndependentBand'))
        membership[actual]=(code,'Hip')
    owners={g['id']:tuple(g['owner_stage'].split('_')[1:]) if g['owner_stage']!='Body' else (None,'Body') for g in plan['groups']}
    lands={r['id']:r for g in plan['groups'] for r in g['lands']}
    for group in rest['groups']:
        for port in group['ports']:
            if previous:
                received=next(p for g in previous['groups'] for p in g['ports'] if p['land_id']==port['land_id'])
                if not received.get('error'):port=received
            shapes=build(lands[port['land_id']],port['arrival_normal'],port['recipe']['band_axial_offset_mm'])
            for prefix,key in (('PlannedPort_','body'),('PlannedBand_','band')):
                name=prefix+port['land_id'];targets[name]=shapes[key];membership[name]=owners[group['id']]
    for sleeve in rest['sleeve_reservations']:
        a=A.Vector(*sleeve['axis']);c=A.Vector(*sleeve['centre_world_mm'])
        name=sleeve['name'];targets[name]=B.Part.makeCylinder(sleeve['diameter_project_mm']/2,sleeve['length_mm'],c-a*sleeve['length_mm']/2,a)
        membership[name]=tuple(sleeve['owner_stage'].split('_')[1:])
    transforms={}
    for code in ('FL','FR','RL','RR'):
        for h,k,a in itertools.product(ANGLES,repeat=3):
            t=transform(axes,code,h,k,'Knee')
            transforms[code,h,k,0,'Hip']=transform(axes,code,h,k,'Hip')
            transforms[code,h,k,0,'Knee']=t
            ax=next(r for r in axes if r['code']==code and r['stage']=='Ankle')
            p=A.Vector(*ax['pivot_mm']);r=A.Rotation(A.Vector(*ax['axis']),a)
            transforms[code,h,k,a,'Ankle']=t*A.Placement(p-r.multVec(p),r)
    actual=[]
    for name,s in targets.items():
        code,stage=membership.get(name,(None,'Body'))
        poses=itertools.product(ANGLES,repeat=3) if stage=='Ankle' else ((h,k,0) for h,k in itertools.product(ANGLES,repeat=2)) if stage=='Knee' else ((h,0,0) for h in ANGLES) if code else [(0,0,0)]
        for h,k,a in poses:
            t=transforms[code,h,k,a,stage] if code else A.Placement()
            actual.append((name,moved(s,t),code,stage,h,k,a))
    actual_wires=[(name,s,r,None,0,0) for name,(s,r) in wires.items()]
    for route in family['routes']:
        code=route['source']['cad_code']
        for h,k in itertools.product(ANGLES,repeat=2):
            w=P.wire(B.parts_for_loom(family,route['loom'],h,k,axes)+B.moved_parts(route['source_parts'],route['source'],h,k,axes))
            actual_wires.append((route['loom'],w,3,code,h,k))
    bounds=B.ImmutableBounds();cache=B.PairReceipts(P.OUT/'remaining-retention-motion-pairs.json',bounds.near)
    checked=0
    def contacts(parts,group,land_id=None):
        nonlocal checked
        code,stage=owners[group['id']]
        poses=itertools.product(ANGLES,repeat=2) if stage=='Knee' else [(h,0) for h in ANGLES] if code else [(0,0)]
        ownlands={r['id'] for r in group['lands']};hits=[]
        for h,k in poses:
            tr=transforms[code,h,k,0,stage] if code else A.Placement()
            for label,s in parts.items():
                q=moved(s,tr)
                for name,t,other,otherstage,hh,kk,aa in actual:
                    if name==group.get('preserved_owner'):continue
                    if name=='PlannedBand_'+str(land_id):continue
                    if name.startswith('PlannedPort_') and name.removeprefix('PlannedPort_') in ownlands:continue
                    if code and code==other and (hh!=h or (stage=='Knee' and otherstage in ('Knee','Ankle') and kk!=k)):continue
                    if not bounds.near(q,t,.001):continue
                    checked+=1;gap,vol=cache.check(q,t)
                    if vol>1e-5:
                        hits.append(dict(part=label,target=name,pose=[h,k],other_pose=[hh,kk,aa],volume_mm3=vol));return hits
                for name,w,r,other,hh,kk in actual_wires:
                    if code and code==other and (hh!=h or (stage=='Knee' and kk!=k)):continue
                    # Own jacket intentionally bears on its band; all other
                    # wire interfaces retain0.5mm design clearance.
                    margin=0 if land_id and name==land_id.split('/')[0] else .5
                    if not bounds.near(q,w,r+margin+.001):continue
                    checked+=1;gap,_=cache.check(q,w,0,r+margin)
                    if gap<r+margin-1e-4:
                        hits.append(dict(part=label,target=name,pose=[h,k],other_pose=[hh,kk],gap_mm=gap,required_mm=r+margin));return hits
        return hits
    result=dict(status='PARTIAL_SHARED_RETENTION_MOTION',groups=[],sleeve_reservations=rest['sleeve_reservations'],
        selected=False,W5_complete=False,physical_pass=False,continuous_sweep_verified=False,
        source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (rf,pf,ff,nf,af,zf,model,archive,sf,hw,Path(__file__),Path(__file__).with_name('loom_land_port.py'))})
    destination=P.OUT/'remaining-retention-motion.json'
    if previous:
        result['groups']=copy.deepcopy(previous['groups'])
        result['inherited_unchanged_ports']=36-len(failed_ids)
        result['source_sha256'][basefile.relative_to(P.ROOT).as_posix()]=P.SHA(basefile)
        result['source_sha256'][Path(__file__).with_name('compact_loom_land_port.py').relative_to(P.ROOT).as_posix()]=P.SHA(Path(__file__).with_name('compact_loom_land_port.py'))
        destination=P.OUT/'remaining-retention-current.json'
    def save():
        cache.save();result['pairs']=checked;result['worker_seconds']=round(time.monotonic()-tick,3)
        result['errors']=[g['id'] for g in result['groups'] if g.get('root_error') or any(p.get('error') for p in g['ports'])]
        destination.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    for group in plan['groups']:
        if previous and not any(r['id'] in failed_ids for r in group['lands']):continue
        old=next(g for g in rest['groups'] if g['id']==group['id']);choice=old['root_choice']
        root=list(old['root_world_mm'])
        # Fixed supports depart OUTWARD from the qualified parent face.
        # The old inward seed was only0.25mm below WAGO and inverted the
        # face inspector's actual exposed-direction result.
        if group['id'].endswith('FixedCarrier'):
            root=list(A.Vector(*choice['plane_centre_world_mm'])+A.Vector(*choice['outward_normal']))
        x,y,z=root;seed=P.box([x-2,y-3,z-2,x+2,y+3,z+2])
        inherited=next(g for g in previous['groups'] if g['id']==group['id']) if previous else None
        root_hits=inherited['root_error'] if inherited else contacts({'Root':seed},group)
        if inherited:root=inherited['root_world_mm']
        record=dict(id=group['id'],owner_stage=group['owner_stage'],root_world_mm=root,root_choice=choice,
            root_error=root_hits,ports=[])
        for port in old['ports']:
            if previous and port['land_id'] not in failed_ids:
                record['ports'].append(next(p for p in inherited['ports'] if p['land_id']==port['land_id']));continue
            land=lands[port['land_id']];options=[];rejected=[]
            for sign in (1,-1):
                normal=[sign*v for v in port['arrival_normal']]
                shapes=(compact_build if compact_mode else build)(land,normal,port['recipe']['band_axial_offset_mm'])
                x,y,z=shapes['arrival_world_mm'];seed=P.box([x-2,y-3,z-2,x+2,y+3,z+2])
                parts={'Port':shapes['body'],'Band':shapes['band'],'Arrival':seed}
                if seed.common(shapes['band']).Volume>1e-5 or seed.common(shapes['body']).Volume<1:
                    rejected.append(dict(normal=normal,error='manufacturing arrival'));continue
                hits=contacts(parts,group,land['id'])
                if hits:rejected.append(dict(normal=normal,contacts=hits));continue
                options.append((math.dist(root,shapes['arrival_world_mm']),normal,shapes))
            if options:
                _,normal,shapes=min(options,key=lambda r:r[0])
                record['ports'].append(dict(land_id=land['id'],arrival_world_mm=shapes['arrival_world_mm'],arrival_normal=normal,
                    recipe=shapes['recipe'],rejected=rejected))
            else:record['ports'].append(dict(land_id=land['id'],error='Both aligned full profiles blocked in sampled common motion',rejected=rejected))
            print('motion retention',land['id'],'options',len(options),'pairs',checked,flush=True)
        if previous:result['groups']=[record if g['id']==group['id'] else g for g in result['groups']]
        else:result['groups'].append(record)
        save()
    result['status']='SHARED_RETENTION_MOTION_CLEAR_ARMS_NATIVE_OPEN' if not result['errors'] else 'SHARED_RETENTION_MOTION_REQUIRES_LAYOUT_CHANGE'
    save();print(json.dumps(dict(status=result['status'],errors=result['errors'],pairs=checked,worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
