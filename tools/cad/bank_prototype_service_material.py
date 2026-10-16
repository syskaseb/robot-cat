"""One removable four-end rail, captive-bolt seats and actual parking pockets.

All dimensions are prototype project recipes. No clip strength, tool or
continuous-wire parking acceptance is inferred from this material model.
"""
import math
import FreeCAD as A
import Part
from loom_land_port import box
from remaining_source_retention_material import saddle
from plan_remaining25_restraint_space import profile


def hexagon(x,y,z,af,h):
    r=af/math.sqrt(3);p=[A.Vector(x+r*math.cos(math.pi/6+i*math.pi/3),y+r*math.sin(math.pi/6+i*math.pi/3),z) for i in range(6)]
    return Part.Face(Part.makePolygon(p+[p[0]])).extrude(A.Vector(0,0,h))


def material(plan):
    r=plan['removable_rail'];q={row['id']:saddle(row['recipe']) for row in r['source_grip_records']}
    dz=r.get('plate_stack_raise_mm',0);bottom=r['base_bounds_mm'][2];top=r['base_bounds_mm'][5]
    pieces=[box(r['base_bounds_mm']),box([3.75,45.75,bottom,12.25,65,top]),
        box([8,61.5,bottom,19,65,top]),box([51.75,45.75,bottom,60.25,65,top]),
        box([45,61.5,bottom,56,65,top])]+[v['body'] for v in q.values()]
    rail=pieces[0].multiFuse(pieces[1:]).removeSplitter()
    parts={};bosses={};hardware={};cups={}
    for i,(x,y,z) in enumerate(r['bolt_centres_mm']):
        hole=Part.makeCylinder(1.7,5,A.Vector(x,y,152+dz));rail=rail.cut(hole).removeSplitter()
        boss=box(r['stationary_boss_bounds_mm'][i]).cut(Part.makeCylinder(1.7,6,A.Vector(x,y,149+dz))).cut(hexagon(x,y,149.4+dz,5.7,2.6)).removeSplitter()
        bosses['RailBoss'+str(i)]=boss
        shaft=Part.makeCylinder(1.5,8,A.Vector(x,y,147.9+dz))
        screw=shaft.fuse(Part.makeCylinder(2.75,3,A.Vector(x,y,155.9+dz))).removeSplitter()
        nut=hexagon(x,y,149.5+dz,5.5,2.4).cut(Part.makeCylinder(1.5,3,A.Vector(x,y,149.3+dz))).removeSplitter()
        washer=Part.makeCylinder(3.5,.5,A.Vector(x,y,155.4+dz)).cut(Part.makeCylinder(1.6,.7,A.Vector(x,y,155.3+dz))).removeSplitter()
        hardware.update({f'RailM3_{i}/Screw':screw,f'RailM3_{i}/Nut':nut,f'RailM3_{i}/Washer':washer})
        # Parked tab floor derives from the ACTUAL operating tab minimumY,
        # not the former bolt-row51.5 template. Pocket gives .3mm each side.
        floor=155.4+(45.75-50)-20
        lo,hi=r['parked_tab_y_mm']
        outer=box([x-4.75,lo-2, floor-2,x+4.75,hi+2,floor+14])
        inner=box([x-4.45,lo-.3,floor,x+4.45,hi+.3,floor+15])
        cups['RailParkingCup'+str(i)]=outer.cut(inner).removeSplitter()
    rotation=A.Rotation(A.Vector(1,0,0),90);pivot=A.Vector(0,50,155.4)
    pose=A.Placement(pivot-rotation.multVec(pivot)+A.Vector(0,-10,-20),rotation)
    parked=rail.copy();parked.Placement=pose*parked.Placement
    bands={gid:v['band'] for gid,v in q.items()}
    parked_bands={}
    for gid,s in bands.items():
        if gid=='W043_P_SYS':continue
        s=s.copy();s.Placement=pose*s.Placement;parked_bands[gid]=s
    p=plan['W043_park'];clip=profile(dict(project_radius_mm=p['radius_mm'],axis=p['free_end_axis'],
        centre_world_mm=p['parking_grip_centre_mm'],land_mm=3,foot_sign=-1),p['parking_grip_normal'],1)
    parts.update({'Rail':rail,**bosses,**cups,'W043ParkingSeat':clip['body'],**hardware})
    for name,s in parts.items():assert s.isValid() and len(s.Solids)==1 and not s.check(True),name
    for gid,b in bands.items():assert rail.common(b).Volume<1e-5,('Rail touches lacing',gid)
    for gid,b in parked_bands.items():assert parked.common(b).Volume<1e-5,('Park rail touches lacing',gid)
    return dict(parts=parts,rail=rail,parked_rail=parked,bands=bands,parked_bands=parked_bands,
        prefuse_parking_seat=clip,pose=pose,parking_cup_floor_z_mm=floor,
        stationary={**bosses,**cups,'W043ParkingSeat':clip['body']},hardware=hardware,
        root_goals=r['structural_root_goals_mm']+[[x,sum(r['parked_tab_y_mm'])/2,floor-2] for x,_,_ in r['bolt_centres_mm']],
        selected=False,physical_pass=False)
