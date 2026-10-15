"""Editable current receiver features; keep historical builders immutable."""
import math
import FreeCAD as A
import Part,Sketcher
from native_support_primitives import Construction as Legacy
from open_deck_p0_supports import sketch
from open_deck_p0_plate import rect
from build_front_fixed_port_clearance import placement
from low_profile_rail_pressure_bridge import build as low
from current_mixed_receiver_material import material
from current_work_guard import check


def axis_pose(frame,origin,along_N=False):
    m=A.Matrix()
    if along_N:
        m.A11=0;m.A12=0;m.A13=1
        m.A21=1;m.A22=0;m.A23=0
        m.A31=0;m.A32=1;m.A33=0
    local=A.Placement(A.Vector(*origin),A.Rotation(m))
    return placement(frame)*local


class Construction(Legacy):
    def box(self,values,name,frame=None,parameter=False):
        check();d=self.doc;x,y,z,X,Y,Z=values;b=d.addObject('PartDesign::Body',name)
        sk=sketch(b,name+'Plan',z);rect(sk,x,y,X-x,Y-y)
        if frame:sk.Placement=placement(frame)*sk.Placement
        pad=b.newObject('PartDesign::Pad',name+'Pad');pad.Profile=sk
        if parameter:pad.setExpression('Length',f'{Z-z-4} mm + ReceiverParameters.ArmThickness')
        else:pad.Length=Z-z
        pad.Refine=True;b.Tip=pad;d.recompute()
        assert sk.FullyConstrained and not pad.Shape.isNull(),name
        self.sketches+=1;sk.Visibility=False;b.Visibility=False;return b
    def cylinder(self,base,radius,height,name,frame,core=False,along_N=False):
        check();b=self.doc.addObject('PartDesign::Body',name);sk=sketch(b,name+'Circle',0)
        sk.Placement=axis_pose(frame,base,along_N)
        i=sk.addGeometry(Part.Circle(A.Vector(),A.Vector(0,0,1),radius),False)
        sk.addConstraint(Sketcher.Constraint('Coincident',i,3,-1,1))
        c=sk.addConstraint(Sketcher.Constraint('Radius',i,radius))
        if core:sk.setExpression(f'Constraints[{c}]','ReceiverParameters.CoreBoreRadius')
        pad=b.newObject('PartDesign::Pad',name+'Pad');pad.Profile=sk;pad.Length=height;pad.Refine=True;b.Tip=pad
        self.doc.recompute();assert sk.FullyConstrained and not pad.Shape.isNull(),name
        self.sketches+=1;sk.Visibility=False;b.Visibility=False;return b
    def hex_trap(self,base,radius,height,name,frame):
        check();b=self.doc.addObject('PartDesign::Body',name);sk=sketch(b,name+'Hexagon',0)
        sk.Placement=axis_pose(frame,base,True)
        points=[(radius*math.cos(i*math.pi/3+math.pi/6),radius*math.sin(i*math.pi/3+math.pi/6)) for i in range(6)]
        for i in range(6):
            a,c=points[i],points[(i+1)%6]
            sk.addGeometry(Part.LineSegment(A.Vector(*a,0),A.Vector(*c,0)),False)
        for i,(x,y) in enumerate(points):
            sk.addConstraint(Sketcher.Constraint('Coincident',i,2,(i+1)%6,1))
            sk.addConstraint(Sketcher.Constraint('DistanceX',i,1,0 if abs(x)<1e-8 else x))
            sk.addConstraint(Sketcher.Constraint('DistanceY',i,1,0 if abs(y)<1e-8 else y))
        pad=b.newObject('PartDesign::Pad',name+'Pad');pad.Profile=sk;pad.Length=height;pad.Refine=True;b.Tip=pad
        self.doc.recompute();assert sk.FullyConstrained and not pad.Shape.isNull(),name
        self.sketches+=1;sk.Visibility=False;b.Visibility=False;return b
    def triple(self,record,name,cap=False):
        profile,_=material(record);recipe=profile['recipe'];frame=recipe['local_to_world']
        # Bolted recipe's coarse main bounds are for conservative separation,
        # not exact native positive material. Get the original exact boxes.
        exact=low(record['lands'],record['normal'],record['feeds'])['recipe'] if record.get('retainer')=='M2_cap' else recipe
        boxes=[exact['cap_bounds_mm'] if cap else exact['base_bounds_mm']]
        if not cap:boxes.append(exact['entry_bounds_mm'])
        if record.get('retainer')=='M2_cap':boxes.append(recipe['cap_boss_bounds_mm' if cap else 'base_boss_bounds_mm'])
        positives=[self.box(v,name+'Positive'+str(i),frame) for i,v in enumerate(boxes)]
        positive=self.fuse(positives,name+'PositiveUnion') if len(positives)>1 else positives[0]
        tools=[self.cylinder(c['base_mm'],c['radius_mm'],c['height_mm'],name+'Bore'+str(i),frame,i<3)
               for i,c in enumerate(recipe['cylinders'])]
        if not cap:
            tools.extend(self.box(c['base'],name+'BandSlot'+str(i),frame) for i,c in enumerate(recipe['channels']) if c['base'])
        if record.get('retainer')=='M2_cap':
            y,z=recipe['bolt_centre_local_mm'];boss=recipe['base_boss_bounds_mm']
            start=exact['cap_bounds_mm'][0]-1
            tools.append(self.cylinder([start,y,z],1.1,boss[3]-start+1,name+'ScrewBore',frame,False,True))
            if not cap:
                back=exact['base_bounds_mm'][3]
                tools.append(self.hex_trap([back,y,z],recipe['nut_trap_project_radius_mm'],boss[3]-back+.1,name+'NutTrap',frame))
        tool=self.fuse(tools,name+'CuttingTools')
        return self.cut(positive,tool,name+'Precut'),profile['cap' if cap else 'body']
