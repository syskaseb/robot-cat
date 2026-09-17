"""Verify bearing material, nearby clearances and stationary fastener lift."""
from pathlib import Path
import json,math,hashlib
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[3]; OUT=ROOT/'hardware/skorupa/v20'
V=A.Vector
report=json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
assert not report['collisions'] and not report['tool_collisions']
shapes={}
for p in report['parts']+report['hardware']:
    path=OUT/(p['name']+'.brep')
    assert hashlib.sha256(path.read_bytes()).hexdigest()==p['sha256']
    s=Part.Shape(); s.read(str(path)); shapes[p['name']]=s

def annulus(ro,ri,height,base,axis):
    return Part.makeCylinder(ro,height,base,axis).cut(Part.makeCylinder(ri,height,base,axis))
def hexring(af,ri,base,axis):
    r=af/math.sqrt(3)
    ps=[V(r*math.cos(i*math.pi/3),r*math.sin(i*math.pi/3),0) for i in range(6)]
    s=Part.Face(Part.makePolygon(ps+[ps[0]])).extrude(V(0,0,.1)).cut(Part.makeCylinder(ri,.1,V()))
    s.Placement=A.Placement(base,A.Rotation(V(0,0,1),axis)); return s
checks=[]
def bearing(label,part,test):
    volume=shapes[part].common(test).Volume
    ratio=volume/test.Volume
    checks.append(dict(check=label,part=part,bearing_material_fraction=ratio))
    assert ratio>=.99,(label,ratio)

for c in report['connections']:
    key=c['mount'][5:]; x,y,z=c['anchor_mm']; side=1 if y>0 else -1
    upper,contact,zz=c['side_center_mm']; contact=abs(contact)
    normal=V(0,side,0)
    screw=shapes['ShellScrew'+key]
    # Cap head is three millimetres tall; derive its inner seat from its
    # exact placed vertices (not loose spline bounding boxes after mirroring).
    head_seat=max(side*p.y for p in screw.tessellate(.03)[0])-3
    bearing(key+' frame head','Mount'+key,annulus(2.25,1.45,.1,V(x,y,41.42),V(0,0,1)))
    bearing(key+' shell head','ShellMounted20',annulus(3,1.7,.1,V(upper,side*(head_seat-.1),zz),normal))
    bearing(key+' frame nut','NutShoe'+key,hexring(5,1.45,V(x,y,33.4),V(0,0,1)))
    inner=contact-c['stem_thickness_mm']
    inset=.1 if key.startswith('Front') else 1.3
    bearing(key+' shell nut','Mount'+key,hexring(5.5,1.7,V(upper,side*(inner+inset+2.5),zz),normal))
    frame='FrameFront20' if key.startswith('Front') else 'FrameRear20'
    bearing(key+' shoe to frame',frame,annulus(4.5,1.45,.1,V(x,y,35.52),V(0,0,1)))
    print('Bearing checks',key,'passed',flush=True)

doc=A.openDocument(str(ROOT/'hardware/skorupa/v19/Kot_v19_SKORUPA_PETG_256.FCStd'))
clearances=[]
for c in report['connections']:
    key=c['mount'][5:]
    targets=['NeckColumn','BusAdapter'] if key.startswith('Front') else ['TailBase','AuxBuck','Pololu']
    for target in targets:
        o=doc.getObject(target); s=o.Shape.copy(); s.Placement=o.getGlobalPlacement().multiply(o.Placement.inverse()).multiply(s.Placement)
        for name in (c['mount'],'FrameScrew'+key,'ShellScrew'+key):
            gap=shapes[name].distToShape(s)[0]
            clearances.append(dict(part=name,target=target,gap_mm=gap))
            assert gap>=.3,(name,target,gap)
stationary=[(n,s) for n,s in shapes.items() if n.startswith(('FrameScrew','FrameNut','ShellNut','NutShoe'))]
lift=[]
for dz in (.5,5,30):
    shell=shapes['ShellMounted20'].copy(); shell.translate(V(0,0,dz))
    for n,s in stationary:
        if not shell.BoundBox.intersect(s.BoundBox): continue
        volume=shell.common(s).Volume
        lift.append([dz,n,volume]); assert volume<.001,(dz,n,volume)
result=dict(bearings=checks,nearby_clearances=clearances,stationary_hardware_lift_samples=lift,
            scope='Local mounting checks only; not whole-shell removal with neck, tail and wires',
            source_breps={p['name']:p['sha256'] for p in report['parts']+report['hardware']})
(OUT/'contact-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print('Bearing, neighbouring-part clearance and stationary-hardware lift checks passed',flush=True)
