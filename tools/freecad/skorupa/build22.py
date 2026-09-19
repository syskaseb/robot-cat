"""Removable PETG belly with four captive-nut rail connections.

Works from a saved v21 copy; geometry generation never edits the source.
All measurements and generated shapes use assembly/world coordinates.
"""
from pathlib import Path
import json,math,hashlib
import FreeCAD as A
import Part,Sketcher
from probe21 import world,visible_names

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'hardware/skorupa/v21/Kot_v21_BOKI_PETG.FCStd'
OUT=ROOT/'hardware/skorupa/v22'
V=A.Vector
ANCHORS=[(x,side*40,end+tag) for x,end in [(-35,'Front'),(80,'Rear')] for side,tag in [(1,'L'),(-1,'R')]]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def box(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cyl(r,h,p,n=V(0,0,1)): return Part.makeCylinder(r,h,p,n)
def hexagon(af,h,p):
    r=af/math.sqrt(3)
    ps=[p+V(r*math.cos(i*math.pi/3),r*math.sin(i*math.pi/3),0) for i in range(6)]
    return Part.Face(Part.makePolygon(ps+[ps[0]])).extrude(V(0,0,h))
def union(ss): return ss[0].multiFuse(ss[1:]).removeSplitter() if len(ss)>1 else ss[0]
def rounded(x0,x1,y0,y1,z0,z1,r,bottom_fillet=0):
    s=box(x0,x1,y0,y1,z0,z1)
    s=s.makeFillet(r,[e for e in s.Edges if e.BoundBox.ZLength>z1-z0-.001])
    if bottom_fillet:
        s=s.makeFillet(bottom_fillet,[e for e in s.Edges if abs(e.BoundBox.ZMin-z0)<1e-6 and e.BoundBox.ZLength<1e-6])
    assert s.isValid() and len(s.Solids)==1
    return s

def through_holes(d,name,shape,centers):
    body=d.addObject('PartDesign::Body',name+'Design')
    base=body.newObject('PartDesign::Feature',name+'Blank'); base.Shape=shape
    sk=body.newObject('Sketcher::SketchObject',name+'M3Sketch')
    # Start on the actual seating-pad/boss top, not above the entire rail:
    # the upper rail skin must not receive an unrelated second hole.
    zface=-2 if name=='Belly22' else 9
    sk.Placement=A.Placement(V(0,0,zface),A.Rotation())
    for x,y in centers:
        i=sk.addGeometry(Part.Circle(V(x,y,0),V(0,0,1),1.7),False)
        sk.addConstraint(Sketcher.Constraint('Block',i))
    d.recompute()
    p=body.newObject('PartDesign::Pocket',name+'M3Through'); p.Profile=sk; p.Type=1
    d.recompute(); assert p.Shape.isValid() and len(p.Shape.Solids)==1,name
    base.Visibility=False; sk.Visibility=False
    return p.Shape.copy()

def main():
    OUT.mkdir(exist_ok=True)
    if (OUT/'Kot_v22_BRZUCH_PETG.FCStd').exists(): raise RuntimeError('Preserve completed v22')
    source=A.openDocument(str(SOURCE)); vis=visible_names(SOURCE)
    objects={o.Name:(o.Label,world(o)) for o in source.Objects
        if o.isDerivedFrom('Part::Feature') and not o.Shape.isNull()
        and o.Name in vis and not o.Name.startswith('Axis_')}
    design=A.newDocument('BellyMountDesign22')
    report=dict(source_sha256=sha(SOURCE),parts=[],hardware=[],collisions=[],
        connections=[],clearances=[],replacements={'Belly22':'BellyPod','SideLeft22':'SideLeft21','SideRight22':'SideRight21'},
        scope='Static prototype; not a complete print release, load certification or leg motion check')
    print('build rounded belly',flush=True)
    outer=rounded(-64,106,-53,53,-6.5,34.5,8,3)
    inner=rounded(-61,103,-50,50,-3.5,36,5)
    belly=outer.cut(inner)
    # Open-top passages at both ends let the tray move straight down off
    # the continuous side rails. No enclosed tunnels trap it in the frame.
    passages=[]
    for x0,x1 in [(-65,-54),(96,107)]:
        passages.append(box(x0,x1,-50,50,-2,36))
    belly=belly.cut(Part.makeCompound(passages)).removeSplitter()
    seats=[cyl(5.5,1.6,V(x,y,-3.6)) for x,y,key in ANCHORS]
    belly=union([belly]+seats)
    parts={}; additions={}; hardware={}
    parts['Belly22']=through_holes(design,'Belly22',belly,[(x,y) for x,y,k in ANCHORS])
    for old,side in [('SideLeft21',1),('SideRight21',-1)]:
        name=old.replace('21','22'); original=objects[old][1]
        print('build rail anchors',name,flush=True)
        bosses=[cyl(6,11,V(x,y,-2)) for x,y,k in ANCHORS if y*side>0]
        raw=union([original]+bosses)
        raw=through_holes(design,name,raw,[(x,y) for x,y,k in ANCHORS if y*side>0])
        # Entry continues above the boss through the inclined legacy rail;
        # stopping at the boss top would leave an overhang blocking the nut.
        pockets=[hexagon(5.8,14,V(x,y,6.3)) for x,y,k in ANCHORS if y*side>0]
        parts[name]=raw.cut(Part.makeCompound(pockets)).removeSplitter()
        # Small positive additions only for collision testing; avoids
        # boolean subtraction of nearly identical imported full rails.
        additions[name]=union(bosses).cut(original).cut(Part.makeCompound(pockets+
            [cyl(1.7,20,V(x,y,-3)) for x,y,k in ANCHORS if y*side>0])).removeSplitter()
    for x,y,key in ANCHORS:
        hardware['BellyScrew'+key]=union([cyl(1.5,16,V(x,y,-6.5)),cyl(3,3,V(x,y,-9.5))])
        hardware['BellyNut'+key]=hexagon(5.5,2.4,V(x,y,6.3)).cut(cyl(1.5,3,V(x,y,6.2)))
        report['connections'].append(dict(name=key,axis_mm=[x,y],axis_direction=[0,0,1],
            screw='M3x16',screw_head_seat_z_mm=-6.5,nut_floor_z_mm=6.3,
            tip_z_mm=9.5,tip_protrusion_mm=.8,printed_bearing_plane_z_mm=-2,
            bore_mm=3.4,nut_pocket_af_mm=5.8,nut_nominal_af_mm=5.5))
    for name,s in parts.items():
        assert s.isValid() and len(s.Solids)==1 and s.Volume>0,(name,'invalid')
        s.check(True); path=OUT/(name+'.brep'); s.exportBrep(str(path))
        report['parts'].append(dict(name=name,volume_mm3=s.Volume,sha256=sha(path),valid=True,solids=1))
    for name,s in hardware.items():
        assert s.isValid() and len(s.Solids)==1 and s.Volume>0,name
        path=OUT/(name+'.brep'); s.exportBrep(str(path))
        report['hardware'].append(dict(name=name,sha256=sha(path)))
    replaced=set(report['replacements'].values())
    targets={n:s for n,(label,s) in objects.items() if n not in replaced}
    checks={'Belly22':parts['Belly22']}|additions|hardware
    for name,s in checks.items():
        print('collision check',name,flush=True)
        for other,t in targets.items():
            if not s.BoundBox.intersect(t.BoundBox): continue
            v=s.common(t).Volume
            if v>.001: report['collisions'].append([name,other,v])
    # Full revised rails vs belly and hardware, and each hardware pair.
    new=list(parts.items())+list(hardware.items())
    for i,(name,s) in enumerate(new):
        for other,t in new[i+1:]:
            if not s.BoundBox.intersect(t.BoundBox): continue
            v=s.common(t).Volume
            if v>.001: report['collisions'].append([name,other,v])
    for other in ['FrameFront20','FrameRear20','Battery','BatteryTray','Part__Feature038','Part__Feature005']:
        gap=parts['Belly22'].distToShape(objects[other][1])[0]
        report['clearances'].append(dict(part='Belly22',neighbor=other,gap_mm=gap))
    design.recompute(); design.saveAs(str(OUT/'BellyMountDesign22.FCStd'))
    (OUT/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(dict(collisions=report['collisions'],clearances=report['clearances'])),flush=True)
    assert not report['collisions'],report['collisions']

if __name__=='__main__': main()
