"""One common support skeleton, not translated obsolete per-wire towers.

Planning BReps only. Existing clamp axes and3mm washer stack govern the
seats. The larger head/tool bore starts ABOVE the seat; it must never remove
the washer bearing annulus. Full world/skin/motion/case/root checks pending.
"""
import numpy as np
import FreeCAD as A
import Part
from feline_solid_distance import bbox_lower_bound


def box(lo,hi):
    lo=np.asarray(lo,float);hi=np.asarray(hi,float)
    assert np.all(hi>lo),(lo,hi)
    return Part.makeBox(*(hi-lo),A.Vector(*lo))


def material_connections(parts):
    """Positive material joints, never a floating edge-touch load path."""
    rows=[]
    for i,(name,s) in enumerate(parts.items()):
        for other,t in list(parts.items())[i+1:]:
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>1e-7:continue
            common=s.copy().common(t.copy());assert common.isNull() or common.isValid()
            if common.Volume>1e-7:rows.append(dict(a=name,b=other,common_mm3=common.Volume))
    attached={n for n in parts if n.startswith('ClampSeat:')}
    for _ in range(len(parts)):
        before=len(attached)
        for r in rows:
            if r['a'] in attached or r['b'] in attached:attached.update((r['a'],r['b']))
        if len(attached)==before:break
    assert attached==set(parts),('Floating foundation pieces',sorted(set(parts)-attached))
    return rows


def build(chosen,proposal,fixed):
    pieces={};meta={};mates=[];fasteners=[]
    def put(name,shape,role,**extra):
        assert name not in pieces and shape.isValid() and shape.Solids,name
        pieces[name]=shape;meta[name]=dict(role=role,**extra)
    # Negative fore extent ends beyond the COMPLETE S1 control, not its body.
    for side in (-1,1):
        x0=-51.75 if side<0 else -126.
        yy=sorted((side*50.6,side*60.))
        put('FoundationRail:'+str(side),box([x0,yy[0],38.52],[127,yy[1],40.52]),'P0_common_side_rail')
        yy=sorted((side*54,side*56))
        put('FoundationFlange:'+str(side),box([x0,yy[0],30.52],[127,yy[1],40.52]),'common_down_flange_NOT_through_grips')
    for group in ('Anchor:Fore','Anchor:Rear'):
        recipe=chosen[group]['recipe']
        for index in recipe['clamp_indices']:
            prefix='Station:'+group+':'
            pad=proposal[prefix+f'TopClampPad{index}'];b=pad.BoundBox
            screw=proposal[prefix+f'RailClamp{index}Screw']
            top=proposal[prefix+f'RailClamp{index}TopWasher'].BoundBox.ZMin
            assert abs(top-b.ZMax-3)<1e-6,'Retain the ACTUAL3mm stack'
            cylinders=[f for f in screw.Faces
                       if type(f.Surface).__name__=='Cylinder' and abs(f.Surface.Axis.z)>.999
                       and f.BoundBox.ZMin<top-1 and f.BoundBox.ZMax>b.ZMax+1]
            assert cylinders,'Read actual shaft, not head diameter'
            shaft_face=min(cylinders,key=lambda f:f.Surface.Radius)
            shaft=shaft_face.Surface.Radius;x,y=shaft_face.Surface.Center.x,shaft_face.Surface.Center.y
            side=1 if y>0 else -1
            head=max(f.Surface.Radius for f in screw.Faces
                if type(f.Surface).__name__=='Cylinder' and abs(f.Surface.Axis.z)>.999)
            hole=Part.makeCylinder(shaft+.2,100,A.Vector(x,y,0))
            tool_radius=max(4.25,head+1.25)
            head_hole=Part.makeCylinder(tool_radius,100,A.Vector(x,y,top))
            fasteners.append(dict(index=index,x=x,y=y,shaft_hole=hole,head_hole=head_hole,
                                  pad=pad,seat_top_mm=top,tool_radius_mm=tool_radius))
            put(f'ClampSeat:{index}',box([b.XMin,b.YMin,b.ZMax],[b.XMax,b.YMax,top]),
                'full3mm_actual_clamp_seat',anchor=group,clamp=index)
            yy=sorted((side*31,side*60))
            put(f'ClampNeck:{index}',box([x-3,yy[0],38.52],[x+3,yy[1],40.52]),'common_cross_neck',clamp=index)
            put(f'BankPier:{index}',box([x-8,y-8,40.02],[x+8,y+8,52.5]),'hollow_head_access_pier',clamp=index)
            bed=fixed['StructureReserve:BankBed'+str(side)];bb=bed.BoundBox
            xx=[x-3,x+3]
            if xx[1]<bb.XMin+3:xx[1]=bb.XMin+3
            if xx[0]>bb.XMax-3:xx[0]=bb.XMax-3
            # Forward negative ledge never extends into the S1 control X<=-53.
            if side<0:xx[0]=max(xx[0],-51.75)
            yy=sorted((side*30,side*45.25))
            put(f'BankLedge:{index}',box([xx[0],yy[0],52],[xx[1],yy[1],55]),
                'bank_bed_extension_same_proposed_frame',clamp=index,bed_owner='StructureReserve:BankBed'+str(side))
    # Finish only NEW printed material, never trim P0/hardware to hide contact.
    for name,shape in list(pieces.items()):
        for f in fasteners:
            for cutter in (f['pad'],f['shaft_hole'],f['head_hole']):
                if bbox_lower_bound(shape.BoundBox,cutter.BoundBox)<=1e-7:
                    shape=shape.cut(cutter)
        assert shape.isValid() and shape.Solids,name
        pieces[name]=shape
    for f in fasteners:
        index=f['index'];seat=pieces[f'ClampSeat:{index}'];pad=f['pad']
        common=seat.copy().common(pad.copy());assert common.isNull() or common.isValid()
        assert common.Volume<1e-7
        # The selected pad's full top face remains a real bearing interface.
        faces=lambda s,z:[p for p in s.Faces if abs(p.BoundBox.ZMin-z)<1e-6 and abs(p.BoundBox.ZMax-z)<1e-6]
        area=sum(a.common(b).Area for a in faces(seat,pad.BoundBox.ZMax) for b in faces(pad,pad.BoundBox.ZMax))
        assert area>=60,(index,area)
        group='Anchor:Fore' if index in (1,2) else 'Anchor:Rear'
        washer=proposal['Station:'+group+f':RailClamp{index}TopWasher']
        washer_gap=seat.distToShape(washer)[0]
        washer_area=sum(a.common(b).Area for a in faces(seat,f['seat_top_mm']) for b in faces(washer,f['seat_top_mm']))
        assert washer_gap<1e-6 and washer_area>10,(index,washer_gap,washer_area)
        mates.append(dict(clamp=index,positive_common_mm3=common.Volume,pad_bearing_area_mm2=area,
                          washer_gap_mm=washer_gap,washer_planar_bearing_area_mm2=washer_area,
                          shaft_clearance_radius_mm=f['shaft_hole'].BoundBox.XLength/2,
                          tool_bore_radius_mm=f['tool_radius_mm'],tool_bore_start_above_seat_mm=f['seat_top_mm']))
    return pieces,meta,mates
