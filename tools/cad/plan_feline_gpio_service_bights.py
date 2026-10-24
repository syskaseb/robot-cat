"""One constant-length five-lead service-loop hypothesis, not selected routing."""
import math
import FreeCAD as A
import Part


def bight(point, direction, lift, radius=10., leg=20.):
    """Downward rolling U: moving inlet, fixed outlet, both horizontal.

    Top quarters consume2R of width, bottom semicircle2R. Bottom centre
    rises lift/2: incoming straight grows lift/2, outgoing shrinks lift/2.
    This preserves centreline length, not a claim about available stock.
    """
    assert 0 <= lift <= 10 and leg > lift/2
    p=A.Vector(*point); d=A.Vector(*direction); d.normalize()
    z=A.Vector(0,0,1); r=radius
    def v(x,h): return p+d*x+z*h
    q=math.sqrt(.5)
    inlet=v(0,lift); a=v(r,lift-r)
    b=v(r,-r-leg+lift/2); c=v(3*r,-r-leg+lift/2)
    e=v(3*r,-r); outlet=v(4*r,0)
    edges=[Part.Arc(inlet,v(r*q,lift-r+r*q),a).toShape(),
           Part.makeLine(a,b),
           Part.Arc(b,v(2*r,-2*r-leg+lift/2),c).toShape(),
           Part.makeLine(c,e),
           Part.Arc(e,v(4*r-r*q,-r+r*q),outlet).toShape()]
    path=Part.Wire(edges)
    ring=Part.Wire([Part.makeCircle(.7,inlet,d)])
    solid=path.makePipeShell([ring],True,False)
    assert solid.isValid() and solid.Solids and not solid.check(True)
    assert abs(path.Length-(2*leg+2*math.pi*r)) < 1e-5
    return solid, dict(length_mm=path.Length, inlet_mm=list(inlet),
                       outlet_mm=list(outlet), radius_mm=r, lift_mm=lift)


def build(rows,lift):
    parts={};info={}
    for row in rows:
        if row['endpoint'].startswith('PI.H'):
            name='ServiceBight:'+row['wire']
            parts[name],info[name]=bight(row['routing_exit_mm'],
                                        row['routing_exit_axis'],lift)
    assert len(parts)==5
    return parts,info


def outboard(rows,lift):
    """Move flexure outside the dense bank; horizontal bridge moves with Pi.

    One left bridge and four right bridges, not offsets of rejected lower U.
    X100 is a layout hypothesis within the325mm torso, not qualified space.
    """
    parts={};info={}
    for row in rows:
        if not row['endpoint'].startswith('PI.H'): continue
        name='ServiceBight:'+row['wire']
        p=A.Vector(*row['routing_exit_mm'])+A.Vector(0,0,lift)
        d=A.Vector(*row['routing_exit_axis']);d.normalize()
        sign=1 if d.x>0 else -1
        end_angle=0 if sign>0 else math.pi
        theta=math.atan2(d.y,d.x); delta=end_angle-theta
        turn=1 if delta>0 else -1
        center=p+A.Vector(-d.y,d.x,0)*10*turn
        radial=p-center
        def rot(angle):
            return center+A.Vector(radial.x*math.cos(angle)-radial.y*math.sin(angle),
                                   radial.x*math.sin(angle)+radial.y*math.cos(angle),0)
        end=rot(delta)
        bridge_end=A.Vector(sign*100,end.y,p.z)
        assert (bridge_end.x-end.x)*sign>0
        path=Part.Wire([Part.Arc(p,rot(delta/2),end).toShape(),Part.makeLine(end,bridge_end)])
        ring=Part.Wire([Part.makeCircle(.7,p,d)])
        bridge=path.makePipeShell([ring],True,False)
        base=bridge_end-A.Vector(0,0,lift)
        loop,record=bight(list(base),[sign,0,0],lift)
        assert bridge.isValid() and bridge.Solids and not bridge.check(True)
        parts[name]=Part.makeCompound([bridge,loop])
        record.update(bridge_length_mm=path.Length,total_length_mm=path.Length+record['length_mm'])
        info[name]=record
    assert len(parts)==5
    return parts,info
