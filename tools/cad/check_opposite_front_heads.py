"""Qualify the two changed tie installations against ALL retained material.

Reuse the first four complete clear carrier bodies. No inward seat/arm changes,
new native build or acceptance of the still-conflicting RR knee support.
"""
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from opposite_loop_head import band
from support_entry_port import build
from whole_current_body_material import load
from check_low_hip_shared_space import AtomicMaterial
from immutable_bounds import ImmutableBounds
import current_body_fanout_material as M
P=M.P


def run():
    tick=time.monotonic();pf=P.OUT/'body-rail-hip-retention-plan.json';plan=json.loads(pf.read_text())
    archive=P.ROOT/plan['archive'];assert P.SHA(archive)==plan['archive_sha256']
    targets,wires,pins=load();shapes={}
    with zipfile.ZipFile(archive) as z:
        for row in json.loads(z.read('index.json')):
            s=Part.Shape();s.importBrepFromString(z.read(row['file']).decode());shapes[row['name']]=s
    for row in plan['changed']:
        targets[row['owner']+'/0/0']=shapes[row['owner']]
        targets[row['band']+'/0/0']=shapes[row['band']]
    portsfile=P.OUT/'body-rail-hip-ports.json';ports=json.loads(portsfile.read_text());new={}
    for row in plan['changed']:
        if not row['owner'].startswith('Front'):continue
        port=next(r for g in ports['groups'] if g['id']==row['owner'] for r in g['ports'] if r['land_id']==row['land']['id'])
        name=row['band']+'/0/0';new[name]=band(build(row['land'],port));targets[name]=new[name]
    # Replace obsolete Hip1 source curves in this scoped head test.
    familyfile=P.OUT/'leg-source-near-member-plan.json';family=json.loads(familyfile.read_text())
    mf=P.OUT/'body-low-hip-rail-exit-plan.json';mathplan=json.loads(mf.read_text())
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    for row in mathplan['hips']:
        loom=row['loom'];wires={n:q for n,q in wires.items() if not n.startswith('leg/'+loom+'/')}
        source=next(r for r in family['routes'] if r['loom']==loom)
        for pose in row['poses']:
            if pose['angle'] not in (-15,0,15):continue
            h=pose['angle'];wires[f'changed/{loom}/{h}']=(P.wire(pose['parts']),3)
            wires[f'factory-source/{loom}/{h}']=(P.wire(M.B.moved_parts(source['source_parts'],source['source'],h,0,axes)),3)
    bf=P.OUT/'body-fanout-layout.json'
    for n,r in json.loads(bf.read_text())['routes'].items():wires['newbody/'+n]=(P.wire(r['parts']),1)
    bounds=ImmutableBounds();cache=AtomicMaterial(P.OUT/'opposite-front-head-pairs.json',bounds.near)
    contacts=[];pairs=0
    for name,s in new.items():
        for other,q in targets.items():
            if other==name or not bounds.near(s,q,.0001):continue
            pairs+=1;gap,volume=cache.check(s,q)
            if volume>1e-5:contacts.append(dict(a=name,b=other,volume_mm3=volume))
        loom=name.removeprefix('Band_').split('/')[0]
        for other,(w,r) in wires.items():
            required=r if other.startswith('changed/'+loom+'/') else r+.25
            if not bounds.near(s,w,required):continue
            pairs+=1;gap,volume=cache.check(s,w,0,required)
            if gap<required-1e-6:contacts.append(dict(a=name,b=other,gap_mm=gap,required_mm=required))
    cache.save();dest=P.OUT/'opposite-front-heads.zip'
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in new.items():z.writestr(n.replace('/','_')+'.brep',s.exportBrepToString())
    result=dict(status='TWO_OPPOSITE_FRONT_HEAD_INSTALLATIONS_CLEAR_OTHER_W5_OPEN' if not contacts else 'REJECTED_OPPOSITE_FRONT_HEADS',
        contacts=contacts,pairs=pairs,material_instances=len(targets),worker_seconds=round(time.monotonic()-tick,3),
        archive=dest.relative_to(P.ROOT).as_posix(),archive_sha256=P.SHA(dest),
        source_sha256={**pins,**{f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in (pf,archive,portsfile,mf,familyfile,af,bf,Path(__file__),Path(__file__).with_name('opposite_loop_head.py'))}},
        preserved='Same full first four carrier bodies, radial seat/loop and cable roots; only provisional front tie closure head on opposite exposed loop side. Fit after delivery required.',
        selected=False,W5_complete=False,physical_pass=False)
    (P.OUT/'opposite-front-heads-proof.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],contacts=contacts,pairs=pairs,worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
