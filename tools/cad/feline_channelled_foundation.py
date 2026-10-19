"""Whole channelled carrier from actual selected neighbours, not local offsets.

Preserve all bought parts and the four real clamp stacks. Only NEW planning
PETG is pocketed. Retain the complete PWM printed carrier as an explicitly
connected subshape. Bank pads come from actual bottom faces, not case bbox.
"""
import FreeCAD as A
import Part
import hashlib
import json
import zipfile
from pathlib import Path
from feline_shared_frame import build as blank_frame,box,material_connections
from feline_solid_distance import bbox_lower_bound
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json


REPLACED_BEDS={'StructureReserve:BankBed-1','StructureReserve:BankBed1'}


def housing(name):return name.startswith('Ref_Material_F_') and '_CP2_Housing_' in name


def same_relation(piece,other):
    if other in REPLACED_BEDS:return 'replaced_planning_reservation'
    if other=='ShelfPWM:carrier':return 'named_same_printed_carrier_union'
    if piece.startswith(('BankBedCurrent:','BankPad:')) and housing(other):return 'selected_bank_bearing_mate'
    if piece.startswith(('ClampSeat:','ClampNeck:')) and other in ('Ref_Material_P0_SideLeft22_0_0','Ref_Material_P0_SideRight22_0_0'):return 'selected_beam_bearing'
    if other.startswith(('Station:Anchor:Fore:','Station:Anchor:Rear:')):return 'actual_clamp_fit'
    return None


def bottom_faces(shape):
    z=shape.BoundBox.ZMin
    return [f for f in shape.Faces if type(f.Surface).__name__=='Plane' and
        abs(f.BoundBox.ZMin-z)<1e-5 and abs(f.BoundBox.ZMax-z)<1e-5 and f.normalAt(0,0).z<-.999]


def clearance_cutter(shape,gap):
    """Offset only a valid planning target; conservative box is explicit fallback.

    The final exact receiver remains authoritative if OCC's offset fails to
    represent the full gap. No purchased shape is ever changed by this tool.
    """
    b=shape.BoundBox
    if shape.isValid() and shape.Solids:
        try:
            pieces=[]
            for solid in shape.Solids:
                q=solid.makeOffsetShape(gap,1e-4,False,False,0,0,False)
                assert q.isValid() and q.Solids
                outside=solid.copy().cut(q.copy());assert outside.isNull() or outside.isValid()
                assert outside.Volume<1e-6
                pieces.extend(q.Solids)
            return Part.makeCompound(pieces),'actual_solid_offset'
        except Exception:pass
    return box([b.XMin-gap,b.YMin-gap,b.ZMin-gap],[b.XMax+gap,b.YMax+gap,b.ZMax+gap]),'conservative_box_construction_only'


def bearing_area(a,b,z):
    faces=lambda s:[f for f in s.Faces if abs(f.BoundBox.ZMin-z)<1e-5 and abs(f.BoundBox.ZMax-z)<1e-5]
    return sum(x.common(y).Area for x in faces(a) for y in faces(b))


def receive_constructed(chosen,proposal,fixed):
    """Use the saved actual candidate, not another Boolean reconstruction.

    Machining offcuts may be discarded ONLY from new unselected pier stock.
    Never remove a bearing pad, clamp seat, retained component or whole pier.
    Every required real bearing is measured again afterwards.
    """
    source=OUT/'n01-channelled-foundation-construction.json';doc=json.loads(source.read_text())
    parent=OUT/'n01-shared54-whole.json'
    assert doc['source_sha256'][parent.relative_to(ROOT).as_posix()]==sha(parent)
    archive=ROOT/doc['bundle'];assert sha(archive)==doc['bundle_sha256']
    actual={};records={}
    with zipfile.ZipFile(archive) as z:
        for r in doc['parts']:
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode());assert s.isValid() and len(s.Solids)==1
            actual[r['name']]=s;records[r['name']]=r['meta']
    dropped=[]
    try:connections=material_connections(actual)
    except AssertionError as exc:
        info=exc.args[0];assert isinstance(info,tuple) and info[0]=='Floating foundation pieces'
        names=info[1]
        for name in names:
            m=records[name];owner=m['source_piece']
            assert owner.startswith('BankPier:') and m['role']=='hollow_head_access_pier' and '/' in name
            assert any(n not in names and records[n]['source_piece']==owner for n in actual)
            s=actual[name];dropped.append(dict(name=name,volume_mm3=s.Volume,bounds_mm=[[s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin],[s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax]],
                reason='Disconnected offcut from NEW unselected pier blank; all bearing/retained parts protected and remeasured'))
        for name in names:del actual[name];del records[name]
        connections=material_connections(actual)
    _,_,oldmates=blank_frame(chosen,proposal,fixed);mates=[]
    for m in oldmates:
        i=m['clamp'];group='Anchor:Fore' if i in (1,2) else 'Anchor:Rear';prefix='Station:'+group+':'
        seat=Part.makeCompound([s for n,s in actual.items() if records[n]['source_piece']==f'ClampSeat:{i}'])
        pad=proposal[prefix+f'TopClampPad{i}'];washer=proposal[prefix+f'RailClamp{i}TopWasher']
        bottom=bearing_area(seat,pad,pad.BoundBox.ZMax);top=bearing_area(seat,washer,washer.BoundBox.ZMin)
        assert bottom>=60 and top>10,(i,bottom,top)
        mates.append(dict(m,pad_bearing_area_after_channels_mm2=bottom,washer_bearing_after_channels_mm2=top))
    pads=[]
    for name,s in actual.items():
        m=records[name]
        if m.get('role')!='actual_selected_housing_bottom_bearing':continue
        owner=fixed[m['owner']];area=bearing_area(s,owner,m['source_bottom_Z_mm'])
        common=s.copy().common(owner.copy());assert common.isNull() or common.isValid()
        assert area>5 and common.Volume<1e-7,(name,area,common.Volume)
        pads.append(dict(part=name,owner=m['owner'],actual_after_channels_bearing_mm2=area,source_bottom_Z_mm=m['source_bottom_Z_mm'],positive_common_mm3=common.Volume))
    assert len({r['owner'] for r in pads})==12
    return actual,records,mates,dict(cuts=doc['cuts'],actual_bank_bearing=pads,positive_material_connections=connections,
        discarded_new_blank_offcuts=dropped,source_candidate=source.relative_to(ROOT).as_posix(),source_candidate_sha256=sha(source),
        replaced_planning_reservations=sorted(REPLACED_BEDS),purchased_material_edited=False,retained_PWM_carrier_complete_unchanged=True,
        all_roots_case_retention_still_open=True)


def build(chosen,proposal,fixed):
    pieces,meta,oldmates=blank_frame(chosen,proposal,fixed);pads=[];cuts=[];cutters={}
    for side in (-1,1):
        old=fixed['StructureReserve:BankBed'+str(side)].BoundBox
        yy=sorted((side*39.25,side*80.))
        name='BankBedCurrent:'+str(side)
        pieces[name]=box([old.XMin,yy[0],52],[old.XMax,yy[1],55]);meta[name]=dict(role='current_bank_carrier_with_actual_housing_pads',replaced='StructureReserve:BankBed'+str(side))
    owners=[(n,s) for n,s in fixed.items() if housing(n)];assert len(owners)==12
    for owner,s in owners:
        faces=bottom_faces(s);assert faces,(owner,'No actual flat bottom face')
        for i,f in enumerate(faces):
            p=f.extrude(A.Vector(0,0,-3));assert p.isValid() and p.Solids
            name='BankPad:'+owner+':'+str(i);pieces[name]=p;meta[name]=dict(role='actual_selected_housing_bottom_bearing',owner=owner,source_face_area_mm2=f.Area,source_bottom_Z_mm=f.BoundBox.ZMin)
            pads.append(dict(part=name,owner=owner,source_face_area_mm2=f.Area,source_bottom_Z_mm=f.BoundBox.ZMin))
    targets={**fixed,**proposal}
    # Extend the actual selected head/driver channels through the NEW beds.
    for group in ('Anchor:Fore','Anchor:Rear'):
        for i in chosen[group]['recipe']['clamp_indices']:
            screw=proposal['Station:'+group+f':RailClamp{i}Screw']
            m=next(m for m in oldmates if m['clamp']==i)
            face=min((f for f in screw.Faces if type(f.Surface).__name__=='Cylinder' and abs(f.Surface.Axis.z)>.999),key=lambda f:f.Surface.Radius)
            c=face.Surface.Center;tool=Part.makeCylinder(m['tool_bore_radius_mm'],100,A.Vector(c.x,c.y,m['tool_bore_start_above_seat_mm']))
            for n in pieces:
                if n.startswith(('BankBedCurrent:','BankPad:')) and bbox_lower_bound(pieces[n].BoundBox,tool.BoundBox)<1e-7:
                    pieces[n]=pieces[n].cut(tool)
    for name,source in list(pieces.items()):
        current=source.copy()
        for other,target in targets.items():
            relation=same_relation(name,other)
            if relation:continue
            if bbox_lower_bound(current.BoundBox,target.BoundBox)>=1.251:continue
            if other not in cutters:cutters[other]=clearance_cutter(target,1.251)
            cutter,method=cutters[other]
            result=current.copy().cut(cutter.copy());assert result.isNull() or result.isValid(),(name,other)
            removed=current.Volume-result.Volume
            if removed>1e-7:cuts.append(dict(part=name,other=other,removed_new_PETG_mm3=removed,construction=method,gap_mm=1.251));current=result
            if current.isNull() or current.Volume<1e-7:break
        pieces[name]=current
        print('Whole carrier channels',name,'remaining new PETG',round(current.Volume,3),flush=True)
    # Every connected solid gets its OWN graph node: no hidden floating
    # fragments masked inside a multi-solid Part.Shape.
    actual={};records={}
    for name,s in pieces.items():
        for i,solid in enumerate(s.Solids):
            n=name if len(s.Solids)==1 else name+'/'+str(i)
            actual[n]=solid;records[n]=dict(meta[name],source_piece=name)
    retained=fixed['ShelfPWM:carrier'];assert retained.isValid() and len(retained.Solids)==1
    actual['RetainedPWMCarrier']=retained;records['RetainedPWMCarrier']=dict(role='unchanged_named_printed_carrier',unchanged_from='ShelfPWM:carrier',source_piece='RetainedPWMCarrier')
    try:connections=material_connections(actual)
    except Exception:
        archive=OUT/'n01-channelled-foundation-construction.breps.zip';geometry=[]
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for n,s in actual.items():
                raw=s.exportBrepToString().encode();entry=str(len(geometry))+'.brep';z.writestr(entry,raw)
                geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),meta=records[n]))
        save_json(OUT/'n01-channelled-foundation-construction.json',dict(status='MATERIAL_CONNECTION_REJECTED_NOT_N01',cuts=cuts,parts=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),source_sha256={Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),(OUT/'n01-shared54-whole.json').relative_to(ROOT).as_posix():sha(OUT/'n01-shared54-whole.json')}))
        raise
    # Recheck REAL bearing interfaces AFTER every global channel/pocket.
    mates=[]
    for m in oldmates:
        i=m['clamp'];group='Anchor:Fore' if i in (1,2) else 'Anchor:Rear';prefix='Station:'+group+':'
        seat=Part.makeCompound([s for n,s in actual.items() if records[n]['source_piece']==f'ClampSeat:{i}'])
        pad=proposal[prefix+f'TopClampPad{i}'];washer=proposal[prefix+f'RailClamp{i}TopWasher']
        bottom=bearing_area(seat,pad,pad.BoundBox.ZMax);top=bearing_area(seat,washer,washer.BoundBox.ZMin)
        assert bottom>=60 and top>10,(i,bottom,top)
        mates.append(dict(m,pad_bearing_area_after_channels_mm2=bottom,washer_bearing_after_channels_mm2=top))
    for p in pads:
        bearing=Part.makeCompound([s for n,s in actual.items() if records[n]['source_piece']==p['part']])
        owner=fixed[p['owner']];area=bearing_area(bearing,owner,p['source_bottom_Z_mm'])
        common=bearing.copy().common(owner.copy());assert common.isNull() or common.isValid()
        assert area>5 and common.Volume<1e-7,(p['part'],area,common.Volume)
        p.update(actual_after_channels_bearing_mm2=area,positive_common_mm3=common.Volume)
    return actual,records,mates,dict(cuts=cuts,actual_bank_bearing=pads,positive_material_connections=connections,
        replaced_planning_reservations=sorted(REPLACED_BEDS),purchased_material_edited=False,
        retained_PWM_carrier_complete_unchanged=True,all_roots_case_retention_still_open=True)
