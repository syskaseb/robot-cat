"""Native editable primitives for the single operating bank/source layout.

All primitives compare against the frozen allocation before a parent union.
No historical source is changed and no imported Part feature stands in for a
new printable part. Hardware/lacing/adhesive may be reference features only.
"""
import math
import FreeCAD as A
import Part,Sketcher
from open_deck_p0_supports import sketch
from current_work_guard import check
from build_current_receiver_supports import editable_feed
from remaining_source_retention_material import saddle
from bank_prototype_service_material import material


IDENTITY=list(A.Matrix().A)


def equal(a,b,name):
    assert max(a.copy().cut(b.copy()).Volume,b.copy().cut(a.copy()).Volume)<1e-4,name


def hex_tool(ops,x,y,z,af,height,name):
    check();d=ops.doc;b=d.addObject('PartDesign::Body',name);s=sketch(b,name+'Plan',z)
    r=af/math.sqrt(3);points=[(x+r*math.cos(math.pi/6+i*math.pi/3),y+r*math.sin(math.pi/6+i*math.pi/3)) for i in range(6)]
    for i in range(6):
        a,c=points[i],points[(i+1)%6];s.addGeometry(Part.LineSegment(A.Vector(*a,0),A.Vector(*c,0)),False)
    for i,(a,c) in enumerate(points):
        s.addConstraint(Sketcher.Constraint('Coincident',i,2,(i+1)%6,1))
        s.addConstraint(Sketcher.Constraint('DistanceX',i,1,a));s.addConstraint(Sketcher.Constraint('DistanceY',i,1,c))
    pad=b.newObject('PartDesign::Pad',name+'Pad');pad.Profile=s;pad.Length=height;pad.Refine=True;b.Tip=pad
    d.recompute();assert s.FullyConstrained and not pad.Shape.isNull(),name
    ops.sketches+=1;s.Visibility=False;b.Visibility=False;return b


def rail_parts(ops,plan):
    q=material(plan);r=plan['removable_rail'];assert not r['in_robot_park_enabled']
    bottom=r['base_bounds_mm'][2];top=r['base_bounds_mm'][5];dz=r['plate_stack_raise_mm']
    positives=[ops.box(v,'SourceRailPlate'+str(i)) for i,v in enumerate([
        r['base_bounds_mm'],[3.75,45.75,bottom,12.25,65,top],[8,61.5,bottom,19,65,top],
        [51.75,45.75,bottom,60.25,65,top],[45,61.5,bottom,56,65,top]])]
    for row in r['source_grip_records']:
        rec=saddle(row['recipe'])['recipe'];positives.append(editable_feed(ops,rec,'SourceRailGrip'+row['id']))
    rail=ops.fuse(positives,'SourceRailPositive');bosses={}
    for i,(x,y,z) in enumerate(r['bolt_centres_mm']):
        tool=ops.cylinder([x,y,152+dz],1.7,5,'SourceRailHole'+str(i),IDENTITY)
        rail=ops.cut(rail,tool,'SourceRailDrilled'+str(i))
        boss=ops.box(r['stationary_boss_bounds_mm'][i],'SourceRailBoss'+str(i))
        bore=ops.cylinder([x,y,149+dz],1.7,6,'SourceRailBossBore'+str(i),IDENTITY)
        trap=hex_tool(ops,x,y,149.4+dz,5.7,2.6,'SourceRailNutTrap'+str(i))
        boss=ops.cut(boss,ops.fuse([bore,trap],'SourceRailBossTools'+str(i)),'SourceRailBossCurrent'+str(i))
        equal(boss.Shape,q['stationary']['RailBoss'+str(i)],'Native rail boss'+str(i));bosses['RailBoss'+str(i)]=boss
    equal(rail.Shape,q['rail'],'Native complete removable rail')
    return rail,bosses,q


def bank_seat(ops,recipe,name):
    x,y,z=recipe['centre_mm'];base=ops.box([x-14,y-7.5,z-4,x+14,y+7.5,z-2],name+'Panel')
    tool=ops.box([x-11.1,y-5.8,z-5,x+11.1,y+5.8,z-1],name+'Cutout')
    seat=ops.cut(base,tool,name+'Open')
    if 'lower_corner_relief' in recipe:seat=ops.cut(seat,ops.box(recipe['lower_corner_relief']['bounds_mm'],name+'CornerTool'),name+'Current')
    return seat


def case_backer(ops,recipe,name):
    items=[ops.box(recipe['floor_mm'],name+'Bearing')]
    items.extend(ops.box(v,name+'Key'+str(i)) for i,v in enumerate(recipe['keys_mm']))
    return ops.fuse(items,name+'Current') if len(items)>1 else items[0]
