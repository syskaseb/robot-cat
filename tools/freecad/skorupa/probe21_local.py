"""Test a central inward reinforcement without occupying end interfaces."""
from probe21 import *

doc=A.openDocument(str(SOURCE)); vis=visible_names(SOURCE)
objects={o.Name:(o.Label,world(o)) for o in doc.Objects
         if o.isDerivedFrom('Part::Feature') and not o.Shape.isNull()
         and o.Name in vis and not o.Name.startswith('Axis_')}
rows=[]
for name in ('SideLeft20','SideRight20'):
    s=objects[name][1]
    # Free central span; last 25 mm at each end remain exactly unchanged.
    region=Part.makeBox(162,200,100,V(-60,-100,-30))
    for idx in (6,9,21):
        f=s.Faces[idx-1]
        layer=f.extrude(f.normalAt(0,0)*1.5).common(region)
        hits=[]; gaps=[]
        for other,(label,t) in objects.items():
            if other==name: continue
            if layer.BoundBox.intersect(t.BoundBox):
                v=layer.common(t).Volume
                if v>.001: hits.append([other,label,v])
            # Known nearby enclosure and central electronics.
            if other in ('BellyPod','Battery','BatteryTray','Part__Feature038'):
                gaps.append([other,layer.distToShape(t)[0]])
        row=dict(name=name,face=idx,hits=hits,gaps=gaps)
        rows.append(row); print(json.dumps(row),flush=True)
for name in ('FrameFront20','FrameRear20','SideLeft20','SideRight20'):
    overlap=objects[name][1].common(objects['BellyPod'][1]).Volume
    row=dict(baseline_pair=[name,'BellyPod'],overlap_mm3=overlap)
    rows.append(row); print(json.dumps(row),flush=True)
(OUT/'local-candidate-audit.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
