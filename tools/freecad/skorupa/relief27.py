"""Prepare local PETG hip-yoke relief boxes from measured interference.

Creates candidates only; a separate MCP step applies parametric subtractive
boxes after volume, connectivity and original M3 mounting faces are checked.
"""
from pathlib import Path
import json
import math
import FreeCAD as A
import Part

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'hardware/skorupa/v27';CACHE=ROOT/'hardware/skorupa/v26/shape-cache'


def load(n):
    s=Part.Shape();s.read(str(CACHE/(n+'.brep')));return s


def main():
    OUT.mkdir(exist_ok=True)
    geometry=json.loads((ROOT/'hardware/simulation/v25/geometry.json').read_text(encoding='utf8'))
    report=[]
    for axis in geometry['axes']:
        if axis['stage']!='Hip':continue
        code=axis['code'];stage='Motion_'+code+'_Hip'
        n=next(p['name'] for p in geometry['components'] if p['stage']==stage and p['label'].startswith('WConnector'))
        yoke=load(n);centre=yoke.BoundBox.Center
        number=int(axis['horn'].replace('Part__Feature',''))
        cases={('Part__Feature%03d'%i):load('Part__Feature%03d'%i) for i in range(number-6,number-3)}
        boxes={};V=A.Vector
        for angle in range(-8,9):
            rot=A.Rotation(V(*axis['axis']),-angle);pivot=V(*axis['pivot_mm'])
            transform=A.Placement(pivot-rot.multVec(pivot),rot)
            for case,s in cases.items():
                moved=s.copy();moved.Placement=transform.multiply(moved.Placement)
                if not moved.BoundBox.intersect(yoke.BoundBox):continue
                cut=yoke.common(moved)
                for solid in cut.Solids:
                    if solid.Volume<.001:continue
                    c=solid.CenterOfMass
                    key=(case,c.x>centre.x,c.z>centre.z)
                    if key not in boxes:boxes[key]=A.BoundBox()
                    boxes[key].add(solid.BoundBox)
        tools=[];params=[]
        for key,b in boxes.items():
            pad=.35
            low=[b.XMin-pad,b.YMin-pad,b.ZMin-pad]
            size=[b.XLength+2*pad,b.YLength+2*pad,b.ZLength+2*pad]
            tools.append(Part.makeBox(*size,V(*low)))
            params.append(dict(case=key[0],low_mm=low,size_mm=size))
        assert tools,n
        candidate=yoke.cut(Part.makeCompound(tools)).removeSplitter()
        removed=yoke.cut(candidate)
        # Protect a 1.5 mm ring of material around every original M3 bore.
        lands=[]
        for f in yoke.Faces:
            if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-1.6)<1e-5:
                c=f.Surface;values=[(v.Point-c.Center).dot(c.Axis) for v in f.Vertexes]
                if not values:continue
                lands.append(Part.makeCylinder(3.1,max(values)-min(values)+.02,c.Center+c.Axis*(min(values)-.01),c.Axis))
        protected_loss=removed.common(Part.makeCompound(lands)).Volume
        m2_lands=[];m2_holes=[]
        for f in yoke.Faces:
            if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-1.)<1e-5 and f.ParameterRange[1]-f.ParameterRange[0]>6.28:
                c=f.Surface;values=[(v.Point-c.Center).dot(c.Axis) for v in f.Vertexes]
                m2_lands.append(Part.makeCylinder(2.5,max(values)-min(values)+.02,c.Center+c.Axis*(min(values)-.01),c.Axis))
                m2_holes.append(dict(center_mm=list(c.Center),axis=list(c.Axis)))
        m2_loss=removed.common(Part.makeCompound(m2_lands)).Volume
        row=dict(code=code,source_name=n,source_volume_mm3=yoke.Volume,
                 removed_mm3=removed.Volume,remaining_fraction=candidate.Volume/yoke.Volume,
                 valid=candidate.isValid(),solid_count=len(candidate.Solids),
                 protected_M3_land_removed_mm3=protected_loss,
                 protected_M2_land_removed_mm3=m2_loss,M2_holes=m2_holes,
                 approval='REJECTED if M2 land removed; do not apply to robot',
                 relief_boxes=params,range_deg=[-8,8],sampling_step_deg=1,box_padding_mm=.35,
                 scope='Candidate only. M3 land test does not establish all local wall thickness or PETG strength.')
        assert row['valid'] and row['solid_count']==1 and row['remaining_fraction']>.90 and protected_loss<1e-5,row
        candidate.exportBrep(str(OUT/(n+'-relief.brep')))
        report.append(row)
        (OUT/'hip-relief-candidates.json').write_text(json.dumps(report,indent=2),encoding='utf8')
        print(code,'removed mm3',round(removed.Volume,3),'fraction',round(row['remaining_fraction'],4),'boxes',len(params),flush=True)


if __name__=='__main__':main()
