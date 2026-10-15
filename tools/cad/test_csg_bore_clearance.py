import math,unittest
import FreeCAD as A
import Part
from occupied_rail_pressure_bridge import build
from csg_bore_clearance import prove,lower_bound


class BoreSeparation(unittest.TestCase):
    def test_rotated_actual_core_and_feed_lines_are_certified(self):
        lands=[dict(id=str(x),centre_world_mm=[x,0,0],axis=[0,0,1],length_mm=9) for x in (-4.75,0,4.75)]
        for normal in ([0,1,0],[0,-1,0]):
            r=build(lands,normal,[9.5,0,-4.5])['recipe']
            for x in (-4.75,0,4.75,9.5):
                wire=Part.makeLine(A.Vector(x,0,-30),A.Vector(x,0,30))
                for kind in ('body','cap'):self.assertTrue(prove(r,kind,wire,2.1+.25 if x==9.5 else 1.25),(normal,x,kind))
    def test_wire_through_real_material_is_never_certified(self):
        lands=[dict(id=str(x),centre_world_mm=[x,0,0],axis=[0,0,1],length_mm=9) for x in (-4.75,0,4.75)]
        r=build(lands,[0,1,0],[9.5,0,-4.5])['recipe']
        self.assertFalse(prove(r,'body',Part.makeLine(A.Vector(0,3,-10),A.Vector(0,3,10)),1.25))
        self.assertFalse(prove(r,'cap',Part.makeLine(A.Vector(0,-3,-10),A.Vector(0,-3,10)),1.25))
    def test_curved_feed_exit_uses_certified_subdivision(self):
        lands=[dict(id=str(x),centre_world_mm=[x,0,0],axis=[0,0,1],length_mm=9) for x in (-4.75,0,4.75)]
        r=build(lands,[0,1,0],[9.5,0,-4.5])['recipe'];R=5.2
        a=A.Vector(9.5,0,4.5);m=A.Vector(9.5+R*(1-math.cos(math.pi/4)),0,4.5+R*math.sin(math.pi/4));b=A.Vector(9.5+R,0,4.5+R)
        wire=Part.Wire([Part.makeLine(A.Vector(9.5,0,-20),a),Part.Arc(a,m,b).toShape()])
        for kind in ('body','cap'):self.assertTrue(prove(r,kind,wire,2.35),kind)
    def test_radial_and_axial_bounds_combine_without_false_contact_claim(self):
        p=[.7,-10,-4.5,5.5,10,4.5];c=[dict(radius_mm=1.3,height_mm=9.2,base_mm=[0,0,-4.6])]
        self.assertGreater(lower_bound([.05,-.01,5,.06,.01,5.1],p,c),1.25)


if __name__=='__main__':unittest.main()
