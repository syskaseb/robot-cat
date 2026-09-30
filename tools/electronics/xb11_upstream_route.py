"""One new full XB11 design route; no previous shelf/pipe matrix repeated."""
import hashlib, json, math
from pathlib import Path
import FreeCAD as A
import Part

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics/full-cat/xb11-upstream-route-r1'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def volume(s): return sum(x.Volume for x in s.Solids)
def box(b): return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
def overlap(a,b): return all((getattr(a,k+'Max')>getattr(b,k+'Min') and getattr(b,k+'Max')>getattr(a,k+'Min')) for k in 'XYZ')
def rounded(points,r):
    edges=[]; current=points[0]
    for i in range(1,len(points)-1):
        p=points[i];incoming=p-points[i-1];outgoing=points[i+1]-p
        incoming.normalize();outgoing.normalize()
        theta=math.acos(max(-1,min(1,incoming.dot(outgoing))))
        assert abs(theta-math.pi/2)<1e-8
        cut=r*math.tan(theta/2)
        before=p-incoming*cut;after=p+outgoing*cut
        assert (before-current).dot(incoming)>-1e-7, 'overlapping fillets'
        if (before-current).Length>1e-7:edges.append(Part.makeLine(current,before))
        center=before+outgoing*r
        mid=center+((before-center)+(after-center)).normalize()*r
        edges.append(Part.Arc(before,mid,after).toShape());current=after
    if (points[-1]-current).Length>1e-7:edges.append(Part.makeLine(current,points[-1]))
    return Part.Wire(edges)
def main():
    OUT.mkdir(exist_ok=True)
    plan={'status':'SOURCE_BEFORE_ONE_BOUNDED_NEW_ROUTE', 'from':'P_AUX.2 assumed -X mouth', 'to':'WAGO221-412 XB11 cageA assumed -X mouth',
          'wire':'HELU23502 1mm2 OD2.5', 'fixed_radius_mm':15, 'waypoints_mm':[[0.5,72,113.5],[-20,72,113.5],[-20,72,65],[-20,-71.75,65],[35,-71.75,65],[35,-71.75,109.15],[50,-71.75,109.15]],
          'routing':'Round every90deg corner R15; pass outside front deck notch, below deck, rise through new shelf window. No actual port or anchor assumed qualified.',
          'new_stls':0,'physical_pass':False,'anchors_complete':False,'selected':False}
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    points=[A.Vector(*p) for p in plan['waypoints_mm']];path=rounded(points,15)
    tube=path.makePipeShell([Part.Wire([Part.makeCircle(1.25,points[0],A.Vector(-1,0,0))])],True,False)
    assert tube.isValid() and len(tube.Solids)==1
    tube.exportBrep(str(OUT/'XB11_DESIGN.brep'))
    hits=[];sources={};tests=0
    for file,obj in [('hardware/cad/studies/deck-aux-wago-r5/DeckAuxWagoR5.FCStd','Deck'),('hardware/cad/studies/aux-splice-shelf-r2/AuxSpliceShelfR2.FCStd','Shelf')]:
        p=ROOT/file;d=A.openDocument(str(p));sources[file]=sha(p)
        try:
            for i,s in enumerate(d.getObject(obj).Shape.Solids):
                tests+=1;v=volume(s.common(tube))
                if v>1e-5:hits.append({'object':obj,'solid':i,'positive_mm3':v})
        finally:A.closeDocument(d.Name)
    cases={'F_HY_design':[0,-85.6,90,20,-64.4,102], 'WAGO221412_design':[50,-81.5,105,68.3,-68.5,113.15],
           'P_AUX_design':[0.5,57,109,19.5,87,118], 'F_TY_design':[0,64.4,93,20,85.6,105],
           'G_TAIL_design':[0.5,-87,109,19.5,-57,118], 'G_AUX_design':[110.5,-84,109,129.5,-54,118]}
    for name,b in cases.items():
        tests+=1;v=volume(box(b).common(tube))
        if v>1e-5:hits.append({'object':name,'positive_mm3':v,'bbox_conservative':True})
    p=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd';sources[p.relative_to(ROOT).as_posix()]=sha(p)
    d=A.openDocument(str(p))
    try:
        for o in d.Objects:
            if not hasattr(o,'Shape') or o.Shape.isNull() or not overlap(o.Shape.BoundBox,tube.BoundBox):continue
            for i,s in enumerate(o.Shape.Solids):
                if not overlap(s.BoundBox,tube.BoundBox):continue
                tests+=1;v=volume(s.common(tube))
                if v>1e-5:hits.append({'object':o.Name,'solid':i,'positive_mm3':v,'source':'E6'})
    finally:A.closeDocument(d.Name)
    result={'source_sha256':sources,'script_sha256':sha(Path(__file__)),'plan_sha256':sha(OUT/'plan.json'),
            'path_length_mm':path.Length,'tube_valid':True,'tube_single_solid':True,'tests':tests,'hits':hits,
            'geometry_nominal_clear':not hits,'anchors_complete':False,'selected':False,'physical_pass':False,
            'scope':'One full geometric design route, hypothetical port centers; no whole harness or actual anchor qualification'}
    (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)
if __name__=='__main__':main()
