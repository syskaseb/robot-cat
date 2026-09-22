"""Evaluate a replaceable front cover with narrower outer wings.

Does not cut servo cases, yokes or mounting-hole lands. Not installed in v27.
"""
from pathlib import Path
import json
import FreeCAD as A
import Part

ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'hardware/skorupa/v27'
CACHE=ROOT/'hardware/skorupa/v26/shape-cache'


def load(name):
    s=Part.Shape();s.read(str(CACHE/(name+'.brep')));return s


def main():
    cover=load('Part__Feature');b=cover.BoundBox
    params=[dict(low_mm=[b.XMin-1,y, b.ZMin-1],size_mm=[b.XLength+2,14,b.ZLength+2]) for y in [-45,31]]
    cutters=[Part.makeBox(*p['size_mm'],A.Vector(*p['low_mm'])) for p in params]
    cut=cover.cut(Part.makeCompound(cutters)).removeSplitter()
    assert cut.isValid() and len(cut.Solids)==1
    removed=cover.cut(cut);lands=[]
    for face in cover.Faces:
        if isinstance(face.Surface,Part.Cylinder) and abs(face.Surface.Radius-1.6)<1e-4:
            c=face.Surface;lands.append(Part.makeCylinder(4.1,5,c.Center-c.Axis,c.Axis))
    assert len(lands)==8
    land_loss=removed.common(Part.makeCompound(lands)).Volume
    assert land_loss<1e-6
    axes=json.loads((OUT/'assembly-plan.json').read_text(encoding='utf8'))['axes']
    rows=[]
    for name,code in [('Part__Feature008','RR'),('Part__Feature016','RL')]:
        a=next(a for a in axes if a['stage']=='Hip' and a['code']==code)
        for degrees in range(-10,11):
            s=load(name);s.rotate(A.Vector(*a['pivot_mm']),A.Vector(*a['axis']),degrees)
            v=cut.common(s).Volume
            distance=cut.distToShape(s)[0]
            rows.append(dict(case=name,angle_deg=degrees,overlap_mm3=v,distance_mm=distance))
            assert v<1e-5,(name,degrees,v)
    cut.exportBrep(str(OUT/'front-cover-clearance.brep'))
    report=dict(installed=False,source_part='Part__Feature',valid=True,solid_count=1,
                source_volume_mm3=cover.Volume,removed_mm3=removed.Volume,
                lost_PETG_g=removed.Volume*1.27e-3,protected_M3_land_loss_mm3=land_loss,
                protected_radial_land_mm=2.5,boxes=params,samples=rows,
                scope='Candidate outer-wing trim only. Sampled +/-10 degrees at 1 degree; not full assembly, continuous collision, strength or print approval.')
    (OUT/'front-cover-clearance.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print('Cover candidate: removed',removed.Volume,'mm3; min case clearance',min(r['distance_mm'] for r in rows),'mm',flush=True)


if __name__=='__main__':main()
