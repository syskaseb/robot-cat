"""Small editable sketch/boolean primitives; no imported print-part BReps."""
import FreeCAD as A
from build_axial_moving_supports_native import check_time
from build_front_fixed_port_clearance import placement
from open_deck_p0_supports import sketch
from open_deck_p0_plate import rect


class Construction:
    def __init__(self,doc):self.doc=doc;self.sketches=0
    def box(self,values,name,frame=None,parameter=False):
        check_time();d=self.doc;x,y,z,X,Y,Z=values;b=d.addObject('PartDesign::Body',name)
        sk=sketch(b,name+'Plan',z);rect(sk,x,y,X-x,Y-y)
        if frame:sk.Placement=placement(frame)*sk.Placement
        pad=b.newObject('PartDesign::Pad',name+'Pad');pad.Profile=sk
        if parameter:pad.setExpression('Length',f'{Z-z-4} mm + ReceiverParameters.ArmThickness')
        else:pad.Length=Z-z
        pad.Refine=True;b.Tip=pad;d.recompute();assert sk.FullyConstrained and not pad.Shape.isNull(),name
        self.sketches+=1;sk.Visibility=False;b.Visibility=False;return b
    def fuse(self,objects,name):
        d=self.doc;q=d.addObject('Part::MultiFuse',name);q.Shapes=objects;q.Refine=True;d.recompute();q.Visibility=False;return q
    def cut(self,base,tool,name):
        d=self.doc;q=d.addObject('Part::Cut',name);q.Base=base;q.Tool=tool;q.Refine=True;d.recompute();q.Visibility=False;return q
    def seat(self,recipe,name):
        frame=recipe['local_to_world']
        pads=[self.box(row['bounds_mm'],name+'Pad'+str(i),frame) for i,row in enumerate(recipe['pads'])]
        positive=self.fuse(pads,name+'Positive')
        r=recipe['ring_cut'];outer=self.box(r['outer'],name+'RingOuter',frame);inner=self.box(r['inner'],name+'RingInner',frame)
        ring=self.cut(outer,inner,name+'Ring')
        cuts=[self.box(v,name+'Slot'+str(i),frame) for i,v in enumerate(recipe.get('cuts',[]))]
        tool=self.fuse([ring,*cuts],name+'Tools') if cuts else ring
        return self.cut(positive,tool,name+'Precut')
    def arm(self,shape,name):
        b=shape.BoundBox
        return self.box([b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],name,parameter=True)
