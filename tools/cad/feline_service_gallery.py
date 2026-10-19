"""One constraint-derived upper gallery, not another single-part offset.

Pi/S0 + populated USB bays + bank service + H5/DG + real four mounting
axes are allocated together. Planning geometry only; no nativeN03 or PASS.
"""
import json,math
import numpy as np
import FreeCAD as A
import Part
from scipy.interpolate import make_interp_spline
from receive_feline_positive_service_deck import pipe,circle_arc,open_grip
from feline_cubic_curvature import extrema
from feline_shared_fore_outline import contour
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT


def usb_recipe():
    q=np.array([110.,28.85810963471377,98.7]);first=q+[15,0,0];R=31.5;drop=9.7
    at=lambda u:first+np.array([R*math.sin(math.pi*u),R*(1-math.cos(math.pi*u)),-drop*(3*u*u-2*u*u*u)])
    deriv=lambda u:np.array([R*math.pi*math.cos(math.pi*u),R*math.pi*math.sin(math.pi*u),-6*drop*u*(1-u)])
    v=np.linspace(0,1,241);spline=make_interp_spline(v,np.array([at(u) for u in v]),k=3,bc_type=([(1,deriv(0))],[(1,deriv(1))]))
    k=extrema(spline.t,spline.c);assert k['regular'] and k['minimum_radius_mm']>=30
    knots,mults=np.unique(spline.t,return_counts=True);c=Part.BSplineCurve()
    c.buildFromPolesMultsKnots([A.Vector(*p) for p in spline.c],mults.tolist(),knots.tolist(),False,3);edge=c.toShape()
    # Separate the return from populated USB-A by its complete Y footprint,
    # not by passing through it at a lower height that blocks ATO service.
    target=np.array([86.,46.,89.]);angle=math.acos(1-(target[1]-q[1])/60)
    dx=60*math.sin(angle)
    main=(452-(15+edge.Length+math.pi*R+60*angle+target[0]-first[0]-dx))/2
    a=at(1);b=a+[-main,0,0];start=b+[0,-2*R,0]
    mid=start+[30*math.sin(angle),30*(1-math.cos(angle)),0]
    t=np.array([math.cos(angle),math.sin(angle),0]);n=np.array([math.sin(angle),-math.cos(angle),0])
    end=start+[dx,target[1]-q[1],0];final=target[0]-end[0];assert final>=12
    edges=[Part.makeLine(A.Vector(*q),A.Vector(*first)),edge,Part.makeLine(A.Vector(*a),A.Vector(*b)),
        circle_arc(b,[-1,0,0],[0,-1,0],R,math.pi),circle_arc(start,[1,0,0],[0,1,0],30,angle),
        circle_arc(mid,t,n,30,angle),Part.makeLine(A.Vector(*end),A.Vector(*target))]
    wire,path=pipe(edges,2.5);assert abs(path.Length-452)<1e-5
    return wire,dict(Pi_mouth_mm=q.tolist(),Pi_full9_mm=[(q+[3,0,0]).tolist(),(q+[12,0,0]).tolist()],
        BUS_mouth_mm=target.tolist(),BUS_full9_mm=[(target-[3,0,0]).tolist(),(target-[12,0,0]).tolist()],
        USB_length_mm=path.Length,minimum_R_mm=min(30,k['minimum_radius_mm']),main_straight_mm=main,
        final_exact_straight_mm=final,fixed_return_plane_Z_mm=89.,return_Y_mm=46.,ATO_tool_top_Z_mm=82.,
        first_turn_R_mm=R,first_turn_minimum_R_mm=k['minimum_radius_mm'],S_escape_angle_rad=angle)


def build():
    from plan_feline_long_return import build as old_build
    world,parts,meta,pins,actors,roles,rows,inverse,outer,baseline,old=old_build()
    wire,recipe=usb_recipe();dp=A.Vector(30,-4,0);db=A.Vector(*np.array(recipe['BUS_mouth_mm'])-old['BUS_mouth_mm'])
    for n,s in actors.items():
        if roles[n] in ('PiRigid','PiWire'):s.translate(dp)
        elif roles[n]=='BUS':s.translate(db)
    baseline={n:s.copy() for n,s in actors.items() if roles[n] in ('PiRigid','PiWire')}
    newends=[]
    for e in old['new_Pi_full_ends']:
        n=e['name'];q=np.array(e['point_mm'])+list(dp);t=np.array(e['axis']);power=n.startswith('PiPower:')
        if power:
            first=q+t*(96.5-q[0]);b=np.array([0.,1,0]);end=first+e['R_mm']*(t+b)
            extra=12. if n.endswith('W080') else 0.;land=end+extra*b;tip=land+9*b
            edges=[Part.makeLine(A.Vector(*q),A.Vector(*first)),circle_arc(first,t,b,e['R_mm'],math.pi/2),Part.makeLine(A.Vector(*end),A.Vector(*tip))]
            actors[n],path=pipe(edges,1.55)
            newends.append(dict(name=n,point_mm=q.tolist(),axis=t.tolist(),full9_mm=[land.tolist(),tip.tolist()],R_mm=e['R_mm'],length_mm=path.Length))
        else:
            land=np.array(e['full9_mm'][0])+list(dp);tip=np.array(e['full9_mm'][1])+list(dp)
            newends.append(dict(e,point_mm=q.tolist(),full9_mm=[land.tolist(),tip.tolist()]))
    for n in list(actors):
        if n.startswith('USBGrip:'):del actors[n];del roles[n];del rows[n]
    actors['USB500:whole']=wire
    for tag,land,side in [('Pi',recipe['Pi_full9_mm'],[0,0,1]),('BUS',recipe['BUS_full9_mm'],[0,1,0])]:
        t=np.array(land[1])-land[0];t/=np.linalg.norm(t)
        for suffix,s in open_grip(land[0],t,side,4.5).items():
            n='USBGrip:'+tag+':'+suffix;actors[n]=s;roles[n]='Grip:'+tag;rows[n]={'kind':'proposal_material'}
    # Two full edge rails on all four ACTUAL standoff axes. They are exact
    # subsets of the previous slab; no notch through bought electronics.
    plate=actors.pop('CurrentBUS:BUS_Backplate');roles.pop('CurrentBUS:BUS_Backplate');rows.pop('CurrentBUS:BUS_Backplate')
    bb=plate.BoundBox;centres=[];railparts=[]
    for group,ids in [('front',(0,1)),('rear',(2,3))]:
        y=np.mean([actors[f'CurrentBUS:BUS_Standoff{i}'].BoundBox.Center.y for i in ids]);centres.append(float(y))
        # Intersect the old PRINTED plate, not its bounding box: retain all
        # actual bolt holes/chamfers. A box would accidentally fill four holes.
        rail=Part.makeBox(bb.XLength,6,bb.ZLength,A.Vector(bb.XMin,y-3,bb.ZMin)).common(plate.copy())
        assert rail.isValid() and len(rail.Solids)==1
        assert rail.cut(plate).Volume<1e-5
        n='CurrentBUS:CarrierRail:'+group;actors[n]=rail;roles[n]='BUS';rows[n]={'kind':'proposal_material'};railparts.append(n)
    # Read source caps from the actual current wire solids, not an old
    # coordinate-frame estimate. D/G turn away from one another, preserving
    # R10 and both full9s, without a collinear overlapping two-wire fan.
    dgends=[]
    for role,sign in [('D',-1),('G',1)]:
        n='CurrentBUS:BUS.'+role;s=actors[n]
        caps=[f for f in s.Faces if isinstance(f.Surface,Part.Plane) and abs(f.Area-math.pi*1.55**2)<1e-4]
        assert len(caps)==2,n;cap=max(caps,key=lambda f:f.CenterOfMass.z);q=np.array(list(cap.CenterOfMass))
        t=np.array([0.,0,-1]);b=np.array([0.,float(sign),0]);end=q+10*(t+b);tip=end+9*b
        actors[n],path=pipe([circle_arc(q,t,b,10,math.pi/2),Part.makeLine(A.Vector(*end),A.Vector(*tip))],1.55)
        roles[n]='BUSWireNew';rows[n]={'kind':'wire'};dgends.append(dict(name=n,point_mm=q.tolist(),full9_mm=[end.tolist(),tip.tolist()],R_mm=10,length_mm=path.Length))
    actors.pop('CurrentBUS:DGSharedRelief');roles.pop('CurrentBUS:DGSharedRelief');rows.pop('CurrentBUS:DGSharedRelief')
    # Delay the torso taper while preserving325x200x160/max200, not enlarging
    # the robot or using a box as the future cosmetic shell.
    stations=[(-141.5,160),(-128,200),(-65,200),(55,200),(145,200),(168,140),(183.5,40)]
    outerfile=OUT/'n01-service-gallery.outer.brep'
    if outerfile.exists():
        # File and string BRep writers do not guarantee identical encoding.
        # Reuse the EXACT pinned file, not a newly reserialized boundary.
        outer=Part.Shape();outer.read(str(outerfile));assert outer.isValid() and len(outer.Solids)==1
        priorfile=OUT/'n01-service-gallery-core-received.json'
        if priorfile.exists():
            prior=json.loads(priorfile.read_text())
            assert prior['recipe']['outer_stations_X_width_mm']==[list(p) for p in stations]
            assert prior['source_sha256'][outerfile.relative_to(ROOT).as_posix()]==sha(outerfile)
        else:
            expected=contour(stations);assert outer.cut(expected).Volume+expected.cut(outer).Volume<1e-5
    else:
        outer=contour(stations);outer.exportBrep(str(outerfile))
    pose=old['BUS_relative_placement'];bustf=A.Placement(A.Vector(*pose['base_mm'])+db,A.Rotation(*pose['quaternion']));inverse=world.bus['inverse']*bustf.inverse()
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'tools/cad/feline_service_gallery.py',OUT/'n01-shared-upper-constraints.json',outerfile)})
    recipe.update(Pi_PCB_centre_mm=[38.5,9.46810963471377,104],new_Pi_full_ends=newends,new_BUS_DG_full_ends=dgends,
        BUS_relative_placement=dict(base_mm=list(bustf.Base),quaternion=list(bustf.Rotation.Q)),
        BUS_carrier_edge_rails=railparts,BUS_carrier_rail_centre_Y_mm=centres,outer_file=outerfile.relative_to(ROOT).as_posix(),outer_stations_X_width_mm=stations,
        all21_station_relocations=[],Pi_cut_capacity_allocation_mm=350,Pi_cut_allocation_not_final_cut=True,
        same_K1474_1m_red_input210_black_input220_remaining_if_Pi350_mm=[440,430],
        seven_Pi_grips_two_DG_grips_complete_roots_tools_capacity_OPEN=True)
    return world,parts,meta,pins,actors,roles,rows,inverse,outer,baseline,recipe
