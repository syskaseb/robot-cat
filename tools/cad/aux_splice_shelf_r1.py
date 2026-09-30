"""Native removable fuse/splice shelf, then only changed E6 occupancy checks."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import FreeCAD as A
import Mesh
import MeshPart
import Part
from fuse_aux_cradle_r1 import sketch,rect,pad,pocket

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/aux-splice-shelf-r1'
MODEL=OUT/'AuxSpliceShelf.FCStd'
STL=OUT/'AuxSpliceShelf_candidate_x1.stl'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
def overlaps(a,b):return a.XMax>b.XMin and b.XMax>a.XMin and a.YMax>b.YMin and b.YMax>a.YMin and a.ZMax>b.ZMin and b.ZMax>a.ZMin

def main():
    plan=json.loads((OUT/'plan.json').read_text(encoding='utf-8'))
    assert not MODEL.exists() and not STL.exists(),'Saved revision immutable'
    d=A.newDocument('AuxSpliceShelf')
    try:
        body=d.addObject('PartDesign::Body','Shelf')
        b=plan['plate_world_bbox_mm']
        sk=sketch(body,'PlateOutline',b[2]);rect(sk,b[0],b[1],b[3],b[4])
        base=pad(body,'PlateThickness',sk,plan['thickness_mm'],d)
        slots=sketch(body,'IndependentTieSlots',b[5])
        for key,size in (('holder_slots_world_xy_mm','holder_slot_xy_mm'),('connector_slots_world_xy_mm','connector_slot_xy_mm')):
            sx,sy=plan[size]
            for x,y in plan[key]:rect(slots,x-sx/2,y-sy/2,x+sx/2,y+sy/2)
        if 'wire_window_world_xyxy_mm' in plan:
            rect(slots,*plan['wire_window_world_xyxy_mm'])
        final=pocket(body,'TieSlotsThrough',slots,plan['thickness_mm'],d)
        d.recompute();d.saveAs(str(MODEL)) # saved native source before BOP/exports
        shape=body.Shape.copy()
        assert sk.FullyConstrained and slots.FullyConstrained
        assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
        before=shape.Volume
        thickness=plan['thickness_mm']
        base.Length=thickness+.2;final.Length=thickness+.2;slots.Placement.Base.z=b[5]+.2;d.recompute()
        trial=body.Shape.Volume
        assert trial>before and abs(trial/before-(thickness+.2)/thickness)<1e-6
        base.Length=thickness;final.Length=thickness;slots.Placement.Base.z=b[5];d.recompute()
        assert abs(body.Shape.Volume-before)<1e-6
        d.save()
        meshshape=body.Shape.copy();meshshape.translate(A.Vector(-b[0],-b[1],-b[2]))
        MeshPart.meshFromShape(Shape=meshshape,LinearDeflection=.05,AngularDeflection=.15,Relative=False).write(str(STL))
        mesh=Mesh.Mesh(str(STL));assert mesh.isSolid() and mesh.countComponents()==1
        result={'status':'CONDITIONAL_SHELF_GEOMETRY_NOT_ROUTE_PASS','plan_sha256':sha(OUT/'plan.json'),
                'valid_single_solid':True,'strict_bop_errors':0,'fully_constrained_sketches':2,
                'volume_mm3':before,'thickness_probe_volume_mm3':trial,'new_stls':1,
                'print_bbox_mm':[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength],
                'quantity':1,'physical_pass':False,'phase1_complete':False}
        assert result['print_bbox_mm'][0]+10<256 and result['print_bbox_mm'][1]+10<256
    finally:A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-splice-') as tmp:
        p=Path(tmp)/MODEL.name;shutil.copy2(MODEL,p);d=A.openDocument(str(p))
        try:
            d.recompute();assert abs(d.getObject('Shelf').Shape.Volume-before)<1e-5
        finally:A.closeDocument(d.Name)
    result['relocated_reopen_ok']=True
    deckpath=ROOT/'hardware/cad/studies/deck-aux-wago-r5/DeckAuxWagoR5.FCStd'
    d=A.openDocument(str(deckpath))
    try:
        deck=d.getObject('Deck').Shape
        result['deck_intersection_mm3']=shape.common(deck).Volume
        result['deck_contact_area_mm2']=shape.common(deck).Area
        result['deck_slot_void_samples']=[]
        for x,y in plan['holder_slots_world_xy_mm']:
            result['deck_slot_void_samples'].append(not deck.isInside(A.Vector(x,y,107),1e-7,False))
        assert result['deck_intersection_mm3']<1e-6 and all(result['deck_slot_void_samples'])
    finally:A.closeDocument(d.Name)
    # Save geometry evidence before the comparatively slow immutable E6 read.
    (OUT/'geometry.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    targets={'shelf':shape,'shifted_F_HY':box(plan['shifted_F_HY_bbox_mm']),
             'WAGO_closed':box(plan['connector_closed_bbox_mm']),
             'WAGO_lever_design':box(plan['connector_lever_design_bbox_mm']),
             'WAGO_mouth_design':box(plan['connector_mouth_design_bbox_mm'])}
    assembly=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd'
    d=A.openDocument(str(assembly))
    try:
        hits={}
        for name,probe in targets.items():
            hits[name]=[]
            for o in d.Objects:
                if not hasattr(o,'Shape') or o.Shape.isNull() or not overlaps(o.Shape.BoundBox,probe.BoundBox):continue
                for i,s in enumerate(o.Shape.Solids):
                    if not overlaps(s.BoundBox,probe.BoundBox):continue
                    v=sum(p.Volume for p in s.common(probe).Solids)
                    if v>1e-5:hits[name].append({'object':o.Name,'solid':i,'mm3':v})
            print(name,len(hits[name]),flush=True)
            (OUT/'progress.json').write_text(json.dumps(hits,indent=2)+'\n',encoding='utf-8')
        result['e6_positive_hits']=hits
        result['e6_sha256']=sha(assembly)
    finally:A.closeDocument(d.Name)
    result['nominal_clear']=all(not v for v in hits.values())
    result['status']='NOMINAL_SHELF_SCREEN_CLEAR_NOT_FULL_ROUTE' if result['nominal_clear'] else 'SHELF_REJECTED_E6_COLLISION'
    result['model_sha256']=sha(MODEL);result['stl_sha256']=sha(STL)
    (OUT/'geometry.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'nominal_clear':result['nominal_clear'],'volume':before,'bbox':result['print_bbox_mm']}))

if __name__=='__main__':main()
