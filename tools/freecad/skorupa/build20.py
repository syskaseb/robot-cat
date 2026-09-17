"""Prototype four removable PETG shell mounts with metal captive nuts.

All coordinates are world coordinates. Original files are never edited.
The two original frames and side panels receive clearance holes only in
their upper flanges; their servo locations and lower flanges are unchanged.
"""
from pathlib import Path
import json,math,hashlib
import FreeCAD as A
import Part,Sketcher

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'hardware/skorupa/v20'; OUT.mkdir(exist_ok=True)
SOURCE=ROOT/'hardware/skorupa/v19/Kot_v19_SKORUPA_PETG_256.FCStd'
V=A.Vector

def box(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cyl(r,h,p,n=V(0,0,1)): return Part.makeCylinder(r,h,p,n)
def hexagon(af,height,p):
    r=af/math.sqrt(3)
    ps=[p+V(r*math.cos(i*math.pi/3),r*math.sin(i*math.pi/3),0) for i in range(6)]
    return Part.Face(Part.makePolygon(ps+[ps[0]])).extrude(V(0,0,height))
def union(parts): return parts[0].multiFuse(parts[1:]).removeSplitter() if len(parts)>1 else parts[0]
def world(o):
    s=o.Shape.copy(); s.Placement=o.getGlobalPlacement().multiply(o.Placement.inverse()).multiply(s.Placement); return s
def reflect(s,side):
    t=s.copy()
    if side<0:
        m=A.Matrix(); m.A22=-1
        t=t.transformGeometry(m)
    return t

def sketched_holes(doc,name,shape,centers,radius,origin,normal,depth):
    """Pocket from a datum plane, with a fixed sketch for each bore centre."""
    body=doc.addObject('PartDesign::Body',name)
    base=body.newObject('PartDesign::Feature',name+'Blank'); base.Shape=shape
    sketch=body.newObject('Sketcher::SketchObject',name+'HoleSketch')
    sketch.Placement=A.Placement(origin,A.Rotation(V(0,0,1),normal))
    inv=sketch.Placement.inverse()
    for center in centers:
        p=inv.multVec(center); p.z=0
        i=sketch.addGeometry(Part.Circle(p,V(0,0,1),radius),False)
        sketch.addConstraint(Sketcher.Constraint('Block',i))
    doc.recompute()
    cut=body.newObject('PartDesign::Pocket',name+'Bores'); cut.Profile=sketch; cut.Length=depth
    doc.recompute()
    assert cut.Shape.isValid() and len(cut.Shape.Solids)==1,(name,'hole pocket invalid')
    base.Visibility=False; sketch.Visibility=False
    return cut.Shape.copy()

def main():
    source=A.openDocument(str(SOURCE))
    design=A.newDocument('MountDesign20')
    originals={o.Name:(o,world(o)) for o in source.Objects if o.isDerivedFrom('Part::Feature') and not o.Shape.isNull()}
    shell=originals['BackCover18'][1]
    parts={}; hardware={}; keepouts=[]; bosses=[]; bores=[]; access=[]; connections=[]
    report=dict(stage='v20 static mounting prototype, not a complete PETG robot release',
                source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),parts=[],hardware=[],checks={},collisions=[],connections=connections)
    for end,anchor,index,upper,contact in [('Front',-70,-80,-63.5,37.8),('Rear',112,122,124,40.0)]:
        for side,tag in [(1,'L'),(-1,'R')]:
            key=end+tag
            print('build mount',key,flush=True)
            if end=='Front':
                raw_boxes=[(-84,-57.5,27.5,35.5,38.52,42.52),(-69.5,-57.5,31.8,37.8,41.52,61)]
            else:
                raw_boxes=[(107,130,27.5,35.5,38.52,42.52),(118,130,33,40,41.52,61)]
            raw=union([box(*b) for b in raw_boxes]+[cyl(1.2,3.0,V(index,31.5,35.92))])
            inner=raw_boxes[-1][2]
            root_edges=[e for e in raw.Edges if len(e.Vertexes)==2 and all(abs(v.Point.y-inner)<1e-6 and abs(v.Point.z-42.52)<1e-6 for v in e.Vertexes)]
            assert len(root_edges)==1,(key,'unique concave root edge missing')
            raw=raw.makeFillet(1.2,root_edges)
            assert raw.isValid() and len(raw.Solids)==1
            # Two bore orientations are generated with explicit sketch/Pocket.
            bracket=sketched_holes(design,'Mount'+key,raw,[V(anchor,31.5,42.6)],1.45,V(0,0,42.6),V(0,0,1),5)
            # One millimetre head recess retains 3 mm PETG under the head.
            # Wider entry only up to the head, then a slender driver channel.
            bracket=sketched_holes(design,'Mount'+key+'Cap',bracket,[V(anchor,31.5,45.3)],2.6,V(0,0,45.3),V(0,0,1),3.78)
            bracket=bracket.cut(cyl(1.5,25,V(anchor,31.5,45.3)))
            bracket=sketched_holes(design,'Mount'+key+'Side',bracket,[V(upper,contact+0.1,56)],1.7,V(0,contact+0.1,0),V(0,1,0),20)
            # Captive M3 nut enters from the inside before installing shell.
            inset=.1 if end=='Front' else 1.3
            nutpl=A.Placement(V(upper,inner+inset,56),A.Rotation(V(0,0,1),V(0,1,0)))
            pocket=hexagon(5.8,inset+2.6,V())
            pocket.Placement=A.Placement(V(upper,inner-.1,56),A.Rotation(V(0,0,1),V(0,1,0)))
            bracket=bracket.cut(pocket).removeSplitter()
            parts['Mount'+key]=reflect(bracket,side)
            # Separate backing shoe spreads clamp pressure under the frame.
            shoe=cyl(4.5,4.52,V(anchor,31.5,31))
            shoe=shoe.cut(hexagon(5.3,2.5,V(anchor,31.5,30.9))).cut(cyl(1.45,5,V(anchor,31.5,30.9))).removeSplitter()
            parts['NutShoe'+key]=reflect(shoe,side)
            # Shell can be lifted vertically after removing its side screws:
            # remove the complete downward extrusion of mount envelopes.
            for b in raw_boxes:
                x0,x1,y0,y1,z0,z1=b
                keepouts.append(reflect(box(x0-.35,x1+.35,y0-.35,y1+.35,0,z1+.35),side))
            keepouts.append(reflect(box(upper-6.35,upper+6.35,inner-1.55,inner+.35,0,44.07),side))
            keepouts.append(reflect(cyl(2.6,44.37,V(anchor,31.5,0)),side))
            ray=shell.common(Part.makeLine(V(upper,0,56),V(upper,80,56)))
            outer=max(v.Point.y for v in ray.Vertexes)
            head_seat=outer+0.7
            bosses.append(reflect(cyl(5.5,head_seat-contact-.45,V(upper,contact+.45,56),V(0,1,0)),side))
            bores.append(reflect(cyl(1.7,head_seat-contact+2,V(upper,contact-.5,56),V(0,1,0)),side))
            # Clear the curved skin outside the flat screw bearing seat.
            bores.append(reflect(cyl(3.25,20,V(upper,head_seat,56),V(0,1,0)),side))
            nut_back=inner+inset
            length=next(n for n in (12,16,20,25) if n>=head_seat-nut_back+0.5)
            screw=union([cyl(1.5,length,V(upper,head_seat-length,56),V(0,1,0)),cyl(3,3,V(upper,head_seat,56),V(0,1,0))])
            nut=hexagon(5.5,2.4,V()).cut(cyl(1.5,3,V(0,0,-.1)))
            nut.Placement=nutpl
            hardware['ShellScrew'+key]=reflect(screw,side)
            hardware['ShellNut'+key]=reflect(nut,side)
            base_screw=union([cyl(1.25,12,V(anchor,31.5,29.52)),cyl(2.25,2.5,V(anchor,31.5,41.52))])
            base_nut=hexagon(5,2,V(anchor,31.5,31.1)).cut(cyl(1.25,2.4,V(anchor,31.5,31)))
            hardware['FrameScrew'+key]=reflect(base_screw,side)
            hardware['FrameNut'+key]=reflect(base_nut,side)
            access.append(('Tool'+key,reflect(cyl(2.5,35,V(upper,head_seat+3.1,56),V(0,1,0)),side)))
            connections.append(dict(mount='Mount'+key,anchor_mm=[anchor,side*31.5,38.52],index_pin_mm=[index,side*31.5,35.92],
                side_axis=[0,side,0],side_center_mm=[upper,side*contact,56],side_screw='M3x'+str(length),
                side_tip_protrusion_mm=length-(head_seat-nut_back),frame_screw='M2.5x12',frame_tip_protrusion_mm=1.58,
                side_nut='M3 AF5.5 x2.4',frame_nut='M2.5 AF5 x2',assembly_gap_mm=.45,
                stem_width_mm=12,stem_thickness_mm=contact-inner,root_fillet_mm=1.2,
                foot_thickness_under_head_mm=3))
    print('shell bosses and extraction pockets',flush=True)
    modified=shell.multiFuse(bosses).cut(Part.makeCompound(keepouts+bores)).removeSplitter()
    parts['ShellMounted20']=modified
    # Upper flange holes only: no leg/servo axis moves and no lower flange cuts.
    replacements={'FrameFront20':'Part__Feature002','FrameRear20':'Part__Feature111','SideRight20':'Part__Feature003','SideLeft20':'Part__Feature112'}
    for name,old in replacements.items():
        xvalues=(-80,-70) if name=='FrameFront20' else ((112,122) if name=='FrameRear20' else (-80,-70,112,122))
        yvalues=(-31.5,31.5) if name.startswith('Frame') else ((-31.5,) if name=='SideRight20' else (31.5,))
        centers=[V(x,y,43) for x in xvalues for y in yvalues]
        parts[name]=sketched_holes(design,name,originals[old][1],centers,1.45,V(0,0,43),V(0,0,1),7.6)
    report['replacements']=dict(replacements,ShellMounted20='BackCover18')
    for name,s in parts.items():
        print('validate',name,flush=True)
        assert s.isValid() and len(s.Solids)==1 and s.Volume>0,(name,len(s.Solids))
        s.exportBrep(str(OUT/(name+'.brep')))
        report['parts'].append(dict(name=name,volume_mm3=s.Volume,valid=True,solids=1,
            sha256=hashlib.sha256((OUT/(name+'.brep')).read_bytes()).hexdigest()))
    for name,s in hardware.items():
        assert s.isValid() and len(s.Solids)==1,name
        s.exportBrep(str(OUT/(name+'.brep')))
        report['hardware'].append(dict(name=name,sha256=hashlib.sha256((OUT/(name+'.brep')).read_bytes()).hexdigest()))
    print('static collision checks',flush=True)
    replaced=set(report['replacements'].values())|{'BackCover','ComputerDeck'}
    new_small={n:s for n,s in parts.items() if n.startswith(('Mount','NutShoe'))}|hardware
    # New mounts/hardware against every retained native feature, modified
    # chassis, and actual shell. No compound assembly objects are compared.
    targets=[(n,s) for n,(o,s) in originals.items() if n not in replaced and not n.startswith('Axis_')]
    targets += [(n,s) for n,s in parts.items() if n not in new_small]
    for name,s in new_small.items():
        print('check',name,flush=True)
        for other,t in targets:
            if s.BoundBox.intersect(t.BoundBox):
                vol=s.common(t).Volume
                if vol>0.001: report['collisions'].append([name,other,vol])
    items=list(new_small.items())
    for i,(name,s) in enumerate(items):
        for other,t in items[i+1:]:
            if s.BoundBox.intersect(t.BoundBox):
                vol=s.common(t).Volume
                if vol>0.001: report['collisions'].append([name,other,vol])
    # Only added bosses must be checked for new shell-vs-original collisions.
    for i,s in enumerate(bosses):
        for n,t in targets:
            if n=='ShellMounted20': continue
            if s.BoundBox.intersect(t.BoundBox):
                vol=s.common(t).Volume
                if vol>0.001: report['collisions'].append(['shell_boss'+str(i),n,vol])
    report['tool_collisions']=[]
    for name,s in access:
        for n,t in targets+list(new_small.items()):
            if s.BoundBox.intersect(t.BoundBox):
                vol=s.common(t).Volume
                if vol>0.001: report['tool_collisions'].append([name,n,vol])
    # Deterministic early lift samples; full robot removal also depends on
    # head/tail/cabling and remains outside this mounting-only check.
    report['mount_extraction_checks']=[]
    for dz in (0.5,5,30):
        print('check mount extraction',dz,flush=True)
        moved=modified.copy(); moved.translate(V(0,0,dz))
        for name,s in parts.items():
            if not name.startswith('Mount'): continue
            v=moved.common(s).Volume
            report['mount_extraction_checks'].append([dz,name,v])
    for o in design.Objects:
        if o.TypeId=='Sketcher::SketchObject': o.Visibility=False
    design.recompute()
    design.saveAs(str(OUT/'MountBoreDesign20.FCStd'))
    (OUT/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(dict(collisions=report['collisions'],tool_collisions=report['tool_collisions'])),flush=True)
    assert not report['collisions'] and not report['tool_collisions']
    assert all(v<.001 for dz,n,v in report['mount_extraction_checks'])

if __name__=='__main__': main()
