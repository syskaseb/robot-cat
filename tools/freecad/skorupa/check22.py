"""Bearing, assembly access and sampled removal tests for the v22 belly."""
from build22 import ROOT,SOURCE,OUT,ANCHORS,world,visible_names,V,cyl,hexagon,box,sha
import FreeCAD as A
import Part,json

r=json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
assert not r['collisions']
shapes={}
for p in r['parts']+r['hardware']:
    path=OUT/(p['name']+'.brep'); assert sha(path)==p['sha256']
    s=Part.Shape(); s.read(str(path)); shapes[p['name']]=s
d=A.openDocument(str(SOURCE)); vis=visible_names(SOURCE)
targets={o.Name:world(o) for o in d.Objects if o.isDerivedFrom('Part::Feature')
    and not o.Shape.isNull() and o.Name in vis and not o.Name.startswith('Axis_')
    and o.Name not in r['replacements'].values()}
targets.update({n:s for n,s in shapes.items() if n!='Belly22' and not n.startswith('BellyScrew')})
report=dict(source_breps={p['name']:p['sha256'] for p in r['parts']+r['hardware']},
    bearings=[],nut_insertion_collisions=[],tool_collisions=[],removal_samples=[],
    rejected_straight_down=[],
    preserved_rail_end_checks=[],wall_thickness_mm=[],scope='Static assembly and sampled removal; no dynamic/load approval')

def ring(ro,ri,z,x,y): return cyl(ro,.1,V(x,y,z)).cut(cyl(ri,.1,V(x,y,z)))
def bearing(label,name,test):
    fraction=shapes[name].common(test).Volume/test.Volume
    report['bearings'].append(dict(check=label,part=name,material_fraction=fraction))
    assert fraction>=.99,(label,fraction)

for x,y,key in ANCHORS:
    rail='SideLeft22' if y>0 else 'SideRight22'
    bearing(key+' screw head','Belly22',ring(3,1.7,-6.5,x,y))
    bearing(key+' belly seating pad','Belly22',ring(5.5,1.7,-2.1,x,y))
    bearing(key+' rail seating pad',rail,ring(5.5,1.7,-2,x,y))
    bearing(key+' nut floor',rail,hexagon(5.5,.1,V(x,y,6.2)).cut(cyl(1.7,.1,V(x,y,6.2))))
    # Nut is fitted before screw, from the chassis interior, then down into
    # its pocket. These solid envelopes cover each straight segment fully.
    vertical=hexagon(5.5,14.4,V(x,y,6.3))
    horizontal=box(x-3.18,x+3.18,min(y,y/2)-2.76,max(y,y/2)+2.76,18.3,20.7)
    for title,test in [('vertical',vertical),('horizontal',horizontal)]:
        for other,t in targets.items():
            if other.startswith('BellyNut'): continue
            if test.BoundBox.intersect(t.BoundBox):
                v=test.common(t).Volume
                if v>.001: report['nut_insertion_collisions'].append([key,title,other,v])
    # Screwdriver shaft below the screw head, excluding the screw itself.
    tool=cyl(2.5,30,V(x,y,-39.5))
    for other,t in targets.items():
        if tool.BoundBox.intersect(t.BoundBox):
            v=tool.common(t).Volume
            if v>.001: report['tool_collisions'].append([key,other,v])
    print('bearing and access',key,flush=True)

poses=[(0,dz) for dz in (.1,.5,1,2,5,10,20,40,60)]+[(dx,20) for dx in (5,10,15,20)]+[(20,dz) for dz in (25,30,35,40)]+[(dx,40) for dx in (25,30)]+[(30,dz) for dz in (50,60)]
for dx,dz in poses:
    b=shapes['Belly22'].copy(); b.translate(V(dx,0,-dz)); hits=[]
    for other,t in targets.items():
        if not b.BoundBox.intersect(t.BoundBox): continue
        v=b.common(t).Volume
        if v>.001: hits.append([other,v])
    key='rejected_straight_down' if dx==0 and dz>20 else 'removal_samples'
    report[key].append(dict(toward_tail_mm=dx,down_mm=dz,collisions=hits))
    print('tail',dx,'down',dz,'hits',hits,flush=True)

for new,old in [('SideLeft22','SideLeft21'),('SideRight22','SideRight21')]:
    base=world(d.getObject(old)); updated=shapes[new]
    for side,mask in [('front',box(-86,-60,-60,60,-5,40)),('rear',box(102,128,-60,60,-5,40)),
                      ('upper_skin',box(-86,128,-60,60,20.4,40))]:
        a=base.common(mask); b=updated.common(mask)
        # Exact coincident imported BReps are unreliable boolean operands.
        # Prove localization of every additive/subtractive operation, and
        # independently compare the resulting end-section volumes.
        sign=1 if new=='SideLeft22' else -1
        masks=[cyl(6,11,V(x,y,-2)) for x,y,k in ANCHORS if y*sign>0]
        masks += [cyl(1.7,19,V(x,y,-10)) for x,y,k in ANCHORS if y*sign>0]
        masks += [hexagon(5.8,14,V(x,y,6.3)) for x,y,k in ANCHORS if y*sign>0]
        overlap=sum(m.common(mask).Volume for m in masks)
        delta=abs(a.Volume-b.Volume)
        report['preserved_rail_end_checks'].append(dict(part=new,end=side,operation_overlap_mm3=overlap,section_volume_delta_mm3=delta))
        assert abs(overlap)<.001 and delta<.001,(new,side,overlap,delta)
for label,a,b in [('floor',V(21,0,-10),V(21,0,0)),
                  ('left wall',V(21,47,18),V(21,57,18)),
                  ('right wall',V(21,-47,18),V(21,-57,18))]:
    length=sum(e.Length for e in shapes['Belly22'].common(Part.makeLine(a,b)).Edges)
    report['wall_thickness_mm'].append([label,length]); assert abs(length-3)<.001
(OUT/'assembly-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert not report['nut_insertion_collisions'],report['nut_insertion_collisions']
assert not report['tool_collisions'],report['tool_collisions']
assert all(not row['collisions'] for row in report['removal_samples'])
print('PASS: 16 bearing tests, nut/tool access, staged removal samples and unchanged end interfaces',flush=True)
