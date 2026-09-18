"""Inward central reinforcement of two native PETG side rails.

Neither the legacy end frames nor the inherited belly are silently changed.
Loft sections blend into the original wall over 10 mm at each end.
Dimensions come from the actual planar faces of the v20 saved rails.
"""
from probe21 import ROOT, SOURCE, OUT, V, world, visible_names
import FreeCAD as A
import Part
import math, json, hashlib

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def box(x0,x1,y0,y1,z0,z1):
    return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))

def reinforcement(s, side):
    # Inner slants and vertical band, selected by geometry, not face index.
    planes=[f for f in s.Faces if isinstance(f.Surface,Part.Plane)]
    top=next(f for f in planes if f.Area>3000 and f.normalAt(0,0).y*side<-.7 and f.normalAt(0,0).z<-.7)
    bottom=next(f for f in planes if f.Area>3000 and f.normalAt(0,0).y*side<-.7 and f.normalAt(0,0).z>.7)
    vertical=next(f for f in planes if f.Area>2000 and f.normalAt(0,0).y*side<-.99)
    u=side*top.CenterOfMass.y+top.CenterOfMass.z
    l=side*bottom.CenterOfMass.y-bottom.CenterOfMass.z
    y=side*vertical.CenterOfMass.y
    overlap=.6; add=1.5; root=35.5
    outer_u=u+overlap*math.sqrt(2); outer_l=l+overlap*math.sqrt(2); outer_y=y+overlap
    outer=[(root,outer_u-root),(outer_y,outer_u-outer_y),
           (outer_y,outer_y-outer_l),(root,root-outer_l)]
    wires=[]
    for x,factor in [(-60,-.1),(-50,1),(92,1),(102,-.1)]:
        inner_u=u-add*factor*math.sqrt(2); inner_l=l-add*factor*math.sqrt(2)
        inner_y=y-add*factor
        inner=[(root,inner_u-root),(inner_y,inner_u-inner_y),
               (inner_y,inner_y-inner_l),(root,root-inner_l)]
        ps=[V(x,side*a,b) for a,b in outer+list(reversed(inner))]
        wires.append(Part.makePolygon(ps+[ps[0]]))
    # Separate ruled end transitions from the prismatic middle. A single
    # four-section loft can produce unreliable OCC booleans on these imports.
    middle=Part.Face(wires[1]).extrude(V(142,0,0))
    result=middle.fuse(Part.makeLoft(wires[:2],True,True)).fuse(
        Part.makeLoft(wires[2:],True,True)).removeSplitter()
    assert result.isValid() and len(result.Solids)==1
    return result,dict(additional_normal_thickness_mm=add,central_wall_mm=3,
        full_thickness_x_mm=[-50,92],blend_x_mm=[[-60,-50],[92,102]],
        unchanged_end_spans_mm=[[-85,-60],[102,127]],
        inner_planes=dict(upper_y_plus_z=u,lower_y_minus_z=l,vertical_y=y))

def main():
    OUT.mkdir(exist_ok=True)
    assert not (OUT/'Kot_v21_BOKI_PETG.FCStd').exists(),'Preserve completed v21'
    doc=A.openDocument(str(SOURCE)); vis=visible_names(SOURCE)
    objects={o.Name:(o.Label,world(o)) for o in doc.Objects
             if o.isDerivedFrom('Part::Feature') and not o.Shape.isNull()
             and o.Name in vis and not o.Name.startswith('Axis_')}
    report=dict(source_sha256=sha(SOURCE),parts=[],collisions=[],clearances=[],
        inherited_interferences=[],scope='Two central side rails only; no load or complete assembly approval')
    pending=[]
    for old,side in [('SideLeft20',1),('SideRight20',-1)]:
        name=old.replace('20','21'); original=objects[old][1]
        print('build',name,flush=True)
        layer,params=reinforcement(original,side)
        final=original.fuse(layer).removeSplitter()
        assert final.isValid() and len(final.Solids)==1 and final.Volume>original.Volume,name
        final.check(True)
        # Explicit new material avoids expensive near-identical shell tests.
        added=layer.cut(original).removeSplitter()
        removed=original.cut(final).Volume
        assert abs(removed)<.001,(name,'original material lost',removed)
        assert abs(final.Volume-original.Volume-added.Volume)<.001,(name,final.Volume-original.Volume-added.Volume)
        for other,(label,t) in objects.items():
            if other==old: continue
            if added.BoundBox.intersect(t.BoundBox):
                vol=added.common(t).Volume
                if vol>.001: report['collisions'].append([name,other,label,vol])
        for near in ('BellyPod','Battery','BatteryTray','FrameFront20','FrameRear20',
                     'NutShoeFrontL','NutShoeFrontR','NutShoeRearL','NutShoeRearR'):
            gap=added.distToShape(objects[near][1])[0]
            report['clearances'].append(dict(part=name,neighbor=near,gap_mm=gap))
        # Preserve both mounting ends and the original top/bottom flange seats.
        masks={'front_end':box(-100,-60,-100,100,-20,60),
               'rear_end':box(102,140,-100,100,-20,60),
               'top_seat':box(-100,140,-35.45,35.45,38.52,39),
               'bottom_seat':box(-100,140,-35.45,35.45,-2,-1.2116613)}
        interface_checks={key:added.common(mask).Volume for key,mask in masks.items()}
        assert all(abs(v)<.001 for v in interface_checks.values()),interface_checks
        # Numerical section lines independently confirm normal thickness.
        thickness=[]
        for p,n in [(V(21,side*42,72.49792536613834-42),V(0,side,1)),
                    (V(21,side*47.8396138458,18.65),V(0,side,0)),
                    (V(21,side*42,42-35.18958659671),V(0,side,-1))]:
            n.normalize(); section=final.common(Part.makeLine(p-n*5,p+n*5))
            value=sum(e.Length for e in section.Edges)
            assert abs(value-3)<.001,(name,'wall thickness',value)
            thickness.append(value)
        final.exportBrep(str(OUT/(name+'.brep')))
        added.exportBrep(str(OUT/(name+'Added.brep')))
        row=dict(name=name,replaces=old,volume_mm3=final.Volume,
            added_volume_mm3=added.Volume,removed_volume_mm3=removed,
            valid=True,solids=1,measured_middle_wall_mm=thickness,
            preserved_interface_added_volumes_mm3=interface_checks,
            sha256=sha(OUT/(name+'.brep')),parameters=params)
        report['parts'].append(row); pending.append((name,added))
        print(json.dumps(row),flush=True)
    for name in ('FrameFront20','FrameRear20','SideLeft20','SideRight20'):
        v=objects[name][1].common(objects['BellyPod'][1]).Volume
        if v>.001: report['inherited_interferences'].append(dict(pair=[name,'BellyPod'],volume_mm3=v))
    (OUT/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    assert not report['collisions'],report['collisions']
    assert all(c['gap_mm']>=.5 for c in report['clearances'])
    print('PASS: two reinforced rails, unchanged mounting ends, no new static collisions',flush=True)

if __name__=='__main__': main()
