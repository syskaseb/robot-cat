"""RR single-feed bridge: NC-side M2 cap screw instead of a wrapping tie.

Nominal M2x14/socket-head/nut reservations are project assumptions pending
stock identification and unpowered fit/torque/insulation trials. PETG nut trap,
not a threaded plastic hole. This does not qualify a purchased screw SKU.
"""
import math
import FreeCAD as A
import Part
from loom_land_port import box
from build_front_fixed_port_clearance import placement
from low_profile_rail_pressure_bridge import build as low


def build(lands,normal,feeds):
    original=low(lands,normal,feeds);r=original['recipe'];assert len(r['feed_slots'])==1
    nc=-r['feed_slots'][0][0];y=nc*9.5;z=-1.5
    base_bounds=r['base_bounds_mm'];cap_bounds=r['cap_bounds_mm'];entry=r['entry_bounds_mm']
    boss=[.7,y-3.7,z-3.7,8.6,y+3.7,z+3.7]
    capboss=[-5,y-3.7,z-3.7,0,y+3.7,z+3.7]
    base=box(base_bounds).fuse(box(entry)).fuse(box(boss)).removeSplitter()
    cap=box(cap_bounds).fuse(box(capboss)).removeSplitter()
    for cylinder in r['cylinders']:
        tool=Part.makeCylinder(cylinder['radius_mm'],cylinder['height_mm'],A.Vector(*cylinder['base_mm']))
        base=base.cut(tool).removeSplitter();cap=cap.cut(tool).removeSplitter()
    bore=Part.makeCylinder(1.1,16,A.Vector(-6,y,z),A.Vector(1,0,0))
    base=base.cut(bore).removeSplitter();cap=cap.cut(bore).removeSplitter()
    def hexagon(x,radius,length):
        points=[A.Vector(x,y+radius*math.cos(i*math.pi/3),z+radius*math.sin(i*math.pi/3)) for i in range(6)]
        return Part.Face(Part.Wire(Part.makePolygon(points+[points[0]]).Edges)).extrude(A.Vector(length,0,0))
    trap=hexagon(5.5,2.5,3.2);base=base.cut(trap).removeSplitter()
    screw=Part.makeCylinder(1,14,A.Vector(-5,y,z),A.Vector(1,0,0)).fuse(
        Part.makeCylinder(1.9,2,A.Vector(-7,y,z),A.Vector(1,0,0))).removeSplitter()
    nut=hexagon(5.5,4/math.sqrt(3),1.6).cut(
        Part.makeCylinder(1,1.8,A.Vector(5.4,y,z),A.Vector(1,0,0))).removeSplitter()
    tool=Part.makeCylinder(1.2,18,A.Vector(-25,y,z),A.Vector(1,0,0))
    for s in (base,cap,screw,nut,tool):assert s.isValid() and len(s.Solids)==1 and not s.check(True)
    for a,b in ((base,cap),(base,screw),(cap,screw),(base,nut),(cap,nut)):
        assert a.common(b).Volume<1e-6
    frame=placement(r['local_to_world'])
    for s in (base,cap,screw,nut,tool):s.Placement=frame*s.Placement
    # The extra NC boss is included in the conservative positive CSG bounds.
    main=[min(base_bounds[i],boss[i]) if i<3 else max(base_bounds[i],boss[i]) for i in range(6)]
    capmain=[min(cap_bounds[i],capboss[i]) if i<3 else max(cap_bounds[i],capboss[i]) for i in range(6)]
    recipe=dict(r,base_bounds_mm=main,cap_bounds_mm=capmain,channels=[],T18I_quantity=0,
        base_boss_bounds_mm=boss,cap_boss_bounds_mm=capboss,bolt_centre_local_mm=[y,z],
        M2x14_quantity=1,M2_nut_quantity=1,nut_trap_project_radius_mm=2.5,
        screw_and_nut_nominal_reservations_not_supplier_geometry=True,
        hardware_SKU_and_tightening_gate_open=True)
    return dict(body=base,cap=cap,screw=screw,nut=nut,access_tool=tool,bands=[],recipe=recipe,
        arrival_world_mm=original['arrival_world_mm'])
