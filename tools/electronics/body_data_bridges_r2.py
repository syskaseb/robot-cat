"""Current data routes avoid selected Pi/AUX return; preserve failed R1.

The right-hand connector's logical cage1 moves to its middle physical cage,
with cage3 to leftmost: all five cages share one DATA potential, no net change.
"""
import math
import body_data_bridges_r1 as M

M.OUT=M.ROOT/"hardware/electronics/full-cat/body-data-bridges-r2"
M.CAD=M.ROOT/"hardware/cad/studies/body-data-bridges-r2"
M.ROUTES={
    "W007": [[16.5,30.5,113.5],[16.5,17.5,113.5],[-10.5,17.5,113.5],
             [-10.5,17.5,126],[-10.5,-17.5,126],[-10.5,-17.5,113.5],[-10.5,-30.5,113.5]],
    "W011": [[16.5,-30.5,113.5],[16.5,-17.5,113.5],[111,-17.5,113.5],[111,-30.5,113.5]],
    "W012": [[124.5,-30.5,113.5],[124.5,-17.5,113.5],[135,-17.5,113.5],
             [135,-17.5,126],[135,17.5,126],[97.5,17.5,126],[97.5,17.5,113.5],[97.5,30.5,113.5]],
}
M.ANCHORS=[(n,e,p[0],math.copysign(26.3,p[1]))
           for n,pp in M.ROUTES.items() for e,p in enumerate((pp[0],pp[-1]))]
M.ANCHORS=[(n,e,x,(-23.8 if n=="W011" and e==1 else -29 if n=="W012" and e==0 else y))
           for n,e,x,y in M.ANCHORS]
M.DATUM_OVERRIDES=dict(port_pitch_assumption_mm=6.75,
    nominal_outer_port_offsets_mm=[-13.5,13.5],
    D_RR_physical_cages_left_to_right=["D_RR.3","D_RR.2","D_RR.1","D_RR.4","D_RR.5"],
    nominal_pitch_is_NOT_manufacturer_data=True,
    W011_crossing="Two matching-tangent S-bends R5.2, rise5mm before XA05 atX90 and return after it; below the unchanged cassette shelfZ122.",
    retired_cache="xb11 obstacle_001 is the old Speaker per checks.json; not installed in the approved hobby scope. No obstacle_* cache used as current owner.",
    R1_hits="W007 versus XL05; W011 versus XA05. These drive the new paths, not a repeated identical test.")


def path(name, points):
    import FreeCAD as A
    import Part
    from xb11_upstream_route import rounded
    if name!="W011":return rounded([A.Vector(*p) for p in points],M.RADIUS)
    low,high=113.5,118.5;r=M.RADIUS;theta=math.acos(1-(high-low)/(2*r));run=2*r*math.sin(theta)
    def s_bend(x,z,up):
        direction=1 if up else -1
        a=A.Vector(x,-17.5,z)
        b=A.Vector(x+r*math.sin(theta),-17.5,z+direction*r*(1-math.cos(theta)))
        c=A.Vector(x+run,-17.5,z+direction*(high-low))
        m1=A.Vector(x+r*math.sin(theta/2),-17.5,z+direction*r*(1-math.cos(theta/2)))
        m2=A.Vector(c.x-r*math.sin(theta/2),-17.5,c.z-direction*r*(1-math.cos(theta/2)))
        return [Part.Arc(a,m1,b).toShape(),Part.Arc(b,m2,c).toShape()]
    before=rounded([A.Vector(*points[0]),A.Vector(*points[1]),A.Vector(66,-17.5,low)],r)
    after=rounded([A.Vector(93+run,-17.5,low),A.Vector(*points[2]),A.Vector(*points[3])],r)
    return Part.Wire(list(before.Edges)+s_bend(66,low,True)+
        [Part.makeLine(A.Vector(66+run,-17.5,high),A.Vector(93,-17.5,high))]+
        s_bend(93,high,False)+list(after.Edges))


M.PATH_BUILDER=path
if __name__=="__main__":M.main()
