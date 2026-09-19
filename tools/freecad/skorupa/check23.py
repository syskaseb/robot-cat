"""Independent carrier checks: bearing material, access and inherited belly path."""
from build23 import OUT,SOURCE,ANCHORS,STRAPS,sha,V,box,cyl,hexagon,world,visible_names
import FreeCAD as A
import Part,json

r=json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
assert not r['collisions']
shapes={}
for row in r['parts']+r['hardware']:
    p=OUT/(row['name']+'.brep'); assert sha(p)==row['sha256']
    s=Part.Shape(); s.read(str(p)); shapes[row['name']]=s
d=A.openDocument(str(SOURCE)); vis=visible_names(SOURCE)
retained={o.Name:world(o) for o in d.Objects if o.isDerivedFrom('Part::Feature') and not o.Shape.isNull()
          and o.Name in vis and not o.Name.startswith('Axis_') and o.Name!='BatteryTray'}
allparts=retained|shapes
report=dict(source_breps={row['name']:row['sha256'] for row in r['parts']+r['hardware']},
    bearings=[],nut_insertion=[],tool_collisions=[],belly_removal_samples=[],floor_thickness_mm=[],contacts=[])

def ring(ro,ri,z,x,y): return cyl(ro,.1,V(x,y,z)).cut(cyl(ri,.1,V(x,y,z)))
def bearing(label,name,test):
    fraction=allparts[name].common(test).Volume/test.Volume
    report['bearings'].append(dict(check=label,part=name,material_fraction=fraction))
    assert fraction>=.99,(label,fraction)

for x,y,key in ANCHORS:
    bearing(key+' head underside plate','Part__Feature005',ring(2.35,1.3,-1.5,x,y))
    bearing(key+' plate upper seat','Part__Feature005',ring(2.25,1.45,-.1,x,y))
    bearing(key+' carrier foot','BatteryCarrier23',ring(2.25,1.45,0,x,y))
    bearing(key+' nut floor','BatteryCarrier23',hexagon(5,.1,V(x,y,3.1)).cut(cyl(1.45,.1,V(x,y,3.1))))
    # Nuts installed in carrier BEFORE the carrier is placed in the chassis.
    # Check translated real nut envelopes, rather than a false solid box
    # filling the hexagon's non-existent corners.
    for distance in [0,.5,1,2,4,6,10,15]:
        nut=shapes['BatteryNut'+key].copy(); nut.translate(V(0,distance*(1 if y>0 else -1),0))
        overlap=nut.common(shapes['BatteryCarrier23']).Volume
        report['nut_insertion'].append(dict(anchor=key,outward_mm=distance,overlap_mm3=overlap))
        assert overlap<.001,(key,distance,overlap)
    tool=cyl(2,30,V(x,y,-33))
    for other,t in allparts.items():
        if other=='Belly22' or other.startswith('BatteryScrew'): continue
        if tool.BoundBox.intersect(t.BoundBox):
            v=tool.common(t).Volume
            if v>.001: report['tool_collisions'].append([key,other,v])

for x in STRAPS:
    line=Part.makeLine(V(x,0,0),V(x,0,7))
    thickness=sum(e.Length for e in shapes['BatteryCarrier23'].common(line).Edges)
    report['floor_thickness_mm'].append([x,thickness]); assert abs(thickness-3)<.001
    n='BatteryStrap'+str(STRAPS.index(x)+1)+'23'
    # A loaded textile loop must touch both the underside of the carrier
    # and the top of the battery; it must not float above either surface.
    for target,z in [('BatteryCarrier23',2.2),('Battery',25.2)]:
        region=box(x-7.5,x+7.5,-21,21,z-.05,z+.05)
        a=shapes[n].common(region); b=allparts[target].common(region)
        gap=a.distToShape(b)[0]
        # Coincident faces can yield an empty OCC common. Check material
        # immediately on BOTH sides of the zero-gap interface instead.
        lower=box(x-7.4,x+7.4,-21,21,z-.05,z)
        upper=box(x-7.4,x+7.4,-21,21,z,z+.05)
        strap_test,target_test=(lower,upper) if target=='BatteryCarrier23' else (upper,lower)
        sf=shapes[n].common(strap_test).Volume/strap_test.Volume
        tf=allparts[target].common(target_test).Volume/target_test.Volume
        report['contacts'].append(dict(part=n,target=target,gap_mm=gap,tested_contact_area_mm2=14.8*42,
                                      strap_material_fraction=sf,target_material_fraction=tf))
        assert gap<1e-6 and min(sf,tf)>=.99,(n,target,gap,sf,tf)

old=json.loads((SOURCE.parent/'assembly-validation.json').read_text(encoding='utf-8'))
for row in old['removal_samples']:
    b=retained['Belly22'].copy(); b.translate(V(row['toward_tail_mm'],0,-row['down_mm']))
    hits=[]
    for other,t in shapes.items():
        if b.BoundBox.intersect(t.BoundBox):
            v=b.common(t).Volume
            if v>.001: hits.append([other,v])
    report['belly_removal_samples'].append(dict(toward_tail_mm=row['toward_tail_mm'],down_mm=row['down_mm'],new_part_collisions=hits))
    assert not hits,hits

assert not report['tool_collisions'],report['tool_collisions']
report['scope']='Static contacts, 32 sampled nut positions and 19 inherited belly poses. Nuts/straps preinstalled off chassis. Battery extraction path and cables NOT validated.'
(OUT/'assembly-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report),flush=True)
