"""Read-only candidate Pololu layout. Probe solids are not production features."""
from pathlib import Path
import hashlib,json
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[3]
CACHE=ROOT/'hardware/skorupa/v30/shape-cache';OUT=ROOT/'hardware/skorupa/v31';OUT.mkdir(exist_ok=True)
plan=json.loads((CACHE.parent/'assembly-plan.json').read_text())
assert json.loads((CACHE/'index.json').read_text())['source_sha256']==plan['source_sha256']
assert hashlib.sha256((CACHE.parent/plan['cad_filename']).read_bytes()).hexdigest()==plan['source_sha256']
base=[85.5,-2,52];thickness=1.5748
holes=[(base[0]+x,base[1]+y) for x in [2.54,38.1] for y in [2.54,17.78]]
old={}
for row in plan['components']:
    if row['name']=='Pololu':continue
    s=Part.Shape();s.read(str(CACHE/(row['name']+'.brep')));old[row['name']]=s
probes={'PCBEnvelope':Part.makeBox(40.64,20.32,7.6748,A.Vector(*base))}
probes['LeftTerminalEnvelope']=Part.makeBox(7.6,10,10,A.Vector(88.04-4.2,3.2,53.5748))
probes['RightTerminalEnvelope']=Part.makeBox(7.6,10,10,A.Vector(123.6-3.4,3.2,53.5748))
probes['LeftWireReserve']=Part.makeBox(12,10,6,A.Vector(71.84,3.2,55))
probes['RightWireReserve']=Part.makeBox(12,10,6,A.Vector(127.8,3.2,55))
contacts=[]
for i,(x,y) in enumerate(holes):
    z=38.52 if i<2 else 44
    probes['Post_%d'%i]=Part.makeCylinder(3,52-z,A.Vector(x,y,z)).cut(Part.makeCylinder(1.2,52-z,A.Vector(x,y,z)))
    if i>=2:
        probes['BridgeSpacer_%d'%i]=Part.makeCylinder(3,2.48,A.Vector(x,y,38.52)).cut(Part.makeCylinder(1.2,2.48,A.Vector(x,y,38.52)))
    probes['M2x19_%d'%i]=Part.makeCylinder(1,19,A.Vector(x,y,52+thickness-19)).fuse(Part.makeCylinder(2.1,2,A.Vector(x,y,52+thickness)))
    probes['NutM2_%d'%i]=Part.makeCylinder(2.309401,1.6,A.Vector(x,y,35.42)).cut(Part.makeCylinder(1,1.6,A.Vector(x,y,35.42)))
    support=old['Part__Feature038'] if i<2 else old['TailBridge29']
    contacts.append(support.common(Part.makeCylinder(3,.05,A.Vector(x,y,z-.05))).Volume/.05)
for name in ['Part__Feature038','TailBridge29']:
    old[name]=old[name].cut(Part.makeCompound([Part.makeCylinder(1.2,18,A.Vector(x,y,36)) for x,y in holes]))
old['ShellMounted20']=old['ShellMounted20'].cut(Part.makeCompound([Part.makeCylinder(3.4,15,A.Vector(x,y,37)) for x,y in holes]))
hits=[];pairs=0
for n,a in probes.items():
    for other,b in old.items():
        if not a.BoundBox.intersect(b.BoundBox):continue
        pairs+=1;v=abs(a.common(b).Volume)
        if v>.01:hits.append(dict(probe=n,part=other,volume_mm3=v))
    print(n,'done',flush=True)
report=dict(source_checkpoint='v30',source_sha256=plan['source_sha256'],base_CAD_mm=base,
            holes_CAD_xy_mm=holes,post_base_z_mm=[38.52,38.52,44,44],support_disk_contact_mm2=contacts,
            broadphase_pairs=pairs,hits=hits,scope=__doc__,print_release=False)
(OUT/'preflight.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report,indent=2))
