"""PETG battery carrier: measured WAVEGO plate axes, soft liner and straps.

All geometry in world coordinates. Preserve source and completed checkpoint.
Hardware and textile shapes are nominal envelopes, not supplier CAD.
"""
from pathlib import Path
import json, math
import FreeCAD as A
import Part, Sketcher
from build22 import box, cyl, union, rounded, sha
from probe21 import world, visible_names

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'hardware/skorupa/v22/Kot_v22_BRZUCH_PETG.FCStd'
OUT=ROOT/'hardware/skorupa/v23'
V=A.Vector
ANCHORS=[(x,y,end+side) for x,end in [(1,'Front'),(59,'Rear')] for y,side in [(24.5,'L'),(-24.5,'R')]]
STRAPS=[14,44]

def hexagon(af,h,p):
    r=af/math.sqrt(3)
    pts=[p+V(r*math.cos(math.pi/6+i*math.pi/3),r*math.sin(math.pi/6+i*math.pi/3),0) for i in range(6)]
    return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,h))

def strap(x):
    def profile(y,z0,z1,r,x0,x1):
        s=box(x0,x1,-y,y,z0,z1)
        return s.makeFillet(r,[e for e in s.Edges if e.BoundBox.XLength>x1-x0-.001])
    loop=profile(32,1.2,26.2,2,x-7.5,x+7.5).cut(profile(31,2.2,25.2,1,x-8,x+8))
    return union([loop,box(x-7.5,x+7.5,-20,20,26.19,27.2)])

def main():
    OUT.mkdir(exist_ok=True)
    if (OUT/'Kot_v23_AKUMULATOR_PETG.FCStd').exists(): raise RuntimeError('Preserve completed v23')
    d=A.openDocument(str(SOURCE)); vis=visible_names(SOURCE)
    targets={o.Name:world(o) for o in d.Objects if o.isDerivedFrom('Part::Feature') and not o.Shape.isNull()
             and o.Name in vis and not o.Name.startswith('Axis_') and o.Name!='BatteryTray'}
    # Existing plate is retained without drilling; nominal M2.5 shaft in its
    # measured 2.6-mm bores is a close fit, to be checked physically.
    carrier=rounded(-23,77,-29.5,29.5,0,9.2,3)
    carrier=carrier.cut(rounded(-19,73,-22.5,22.5,5.2,10,1.5))
    carrier=carrier.makeFillet(.6,[e for e in carrier.Edges if abs(e.BoundBox.ZMin-9.2)<1e-6 and e.BoundBox.ZLength<1e-6])
    # Clearance above the two lower side-rail flanges, leaving contact to
    # the lower plate at Z=0 in the centre. No floating support feet.
    carrier=carrier.cut(Part.makeCompound([box(-24,78,26.8,31,-.1,.7),box(-24,78,-31,-26.8,-.1,.7)]))
    # Underside channels are closed by the chassis plate during assembly.
    # 3 mm of carrier floor remains above each 16-mm strap passage.
    for x in STRAPS: carrier=carrier.cut(box(x-8,x+8,-31,31,-.1,2.2))
    design=A.newDocument('BatteryCarrierDesign23')
    body=design.addObject('PartDesign::Body','CarrierBody')
    blank=body.newObject('PartDesign::Feature','CarrierBlank'); blank.Shape=carrier.removeSplitter()
    sketch=body.newObject('Sketcher::SketchObject','M25ClearanceSketch')
    sketch.Placement=A.Placement(V(0,0,7),A.Rotation())
    for x,y,key in ANCHORS:
        i=sketch.addGeometry(Part.Circle(V(x,y,0),V(0,0,1),1.45),False)
        sketch.addConstraint(Sketcher.Constraint('Block',i))
    design.recompute()
    pocket=body.newObject('PartDesign::Pocket','M25ThroughBelowRoof'); pocket.Profile=sketch; pocket.Type=1
    design.recompute(); assert pocket.Shape.isValid() and len(pocket.Shape.Solids)==1
    carrier=pocket.Shape.copy()
    # Side-loaded captive nuts sit on 3.2-mm PETG floors. The blind screw
    # channels stop at Z=7, leaving a closed top above the screw tip Z=6.5.
    for x,y,key in ANCHORS:
        channel=box(x-2.65,x+2.65,min(y,y/abs(y)*31),max(y,y/abs(y)*31),3.2,5.5)
        carrier=carrier.cut(union([hexagon(5.3,2.3,V(x,y,3.2)),channel]))
    carrier=carrier.removeSplitter()
    final=body.newObject('PartDesign::Feature','CarrierNutChannels'); final.Shape=carrier
    for o in (blank,sketch,pocket): o.Visibility=False
    parts={'BatteryCarrier23':carrier}; bought={}
    for x,y,key in ANCHORS:
        bought['BatteryScrew'+key]=union([cyl(1.25,8,V(x,y,-1.5)),cyl(2.35,1.5,V(x,y,-3))])
        bought['BatteryNut'+key]=hexagon(5,2,V(x,y,3.2)).cut(cyl(1.25,2.2,V(x,y,3.1)))
    bought['BatteryLiner23']=rounded(-18,72,-21.5,21.5,5.2,6.2,.5)
    for i,x in enumerate(STRAPS,1): bought['BatteryStrap'+str(i)+'23']=strap(x)
    report=dict(source_sha256=sha(SOURCE),replacements={'BatteryCarrier23':'BatteryTray'},parts=[],hardware=[],collisions=[],clearances=[],
        anchors_mm=[[x,y] for x,y,k in ANCHORS],strap_centres_x_mm=STRAPS,
        battery_supplier='https://gensace.de/de/collections/test-new/products/gea223s60x6sgt',
        battery_nominal_mm=[90,43,19],purchased_pack_confirmed=False,
        scope='Static mounting prototype only; cables, pack tolerance, load, PETG creep and physical assembly remain unverified')
    for group,shapes in [('parts',parts),('hardware',bought)]:
        for n,s in shapes.items():
            assert s.isValid() and len(s.Solids)==1 and s.Volume>0,n
            s.check(True); p=OUT/(n+'.brep'); s.exportBrep(str(p))
            report[group].append(dict(name=n,sha256=sha(p),volume_mm3=s.Volume,valid=True,solids=1))
    allnew=parts|bought
    for n,s in allnew.items():
        print('check',n,flush=True)
        for other,t in targets.items():
            if not s.BoundBox.intersect(t.BoundBox): continue
            volume=s.common(t).Volume
            if volume>.001: report['collisions'].append([n,other,volume])
    items=list(allnew.items())
    for i,(n,s) in enumerate(items):
        for other,t in items[i+1:]:
            if s.BoundBox.intersect(t.BoundBox):
                volume=s.common(t).Volume
                if volume>.001: report['collisions'].append([n,other,volume])
    for n in allnew:
        for other in ['Battery','Belly22','SideLeft22','SideRight22']:
            report['clearances'].append(dict(part=n,neighbor=other,gap_mm=allnew[n].distToShape(targets[other])[0]))
    design.recompute(); design.saveAs(str(OUT/'BatteryCarrierDesign23.FCStd'))
    (OUT/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report['collisions']),flush=True)
    assert not report['collisions'],report['collisions']

if __name__=='__main__': main()
