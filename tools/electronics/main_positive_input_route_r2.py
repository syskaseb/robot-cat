"""One changed packing corridor based on R1 named obstructions.

Preserve DATA/PWM/GND parts. Shift F_PI west, label the first still-unrouted
P_SYS cage .2, pass factory wire diagonally up/outside PWM straps, and enter
MAIN below the retained GND strap with two exact R6 arcs.
"""
import math
import main_positive_input_route_common_r2 as R
R.OUT=R.ROOT/'hardware/electronics/full-cat/main-positive-input-route-r2'
R.SOURCE=[-84,-11,113.5]
R.HOLDER=[-73,-29.85,109,-22,-12.15,131]
R.PREF=[[-84,-13,113.5],[-84,-17.4182779986,113.5],[-80.4182779986,-21,115],[-76,-21,115]]
R.LIMITS={'W043':40,'W077':80,'W078':210}

def s_bend(start, shift, direction_radius):
    import FreeCAD as A
    import Part
    h=math.sqrt(sum(v*v for v in shift));radius=direction_radius
    up=A.Vector(*shift)/h;axis=A.Vector(1,0,0);begin=A.Vector(*start)
    angle=math.acos(1-h/(2*radius));run=2*radius*math.sin(angle)
    def p(t):
        if t<=angle:return begin+axis*(radius*math.sin(t))+up*(radius*(1-math.cos(t)))
        q=t-angle
        return begin+axis*(radius*math.sin(angle)+radius*(math.sin(angle)-math.sin(angle-q)))+up*(radius*(1-math.cos(angle))+radius*(math.cos(angle-q)-math.cos(angle)))
    return [Part.Arc(p(0),p(angle/2),p(angle)).toShape(),Part.Arc(p(angle),p(1.5*angle),p(2*angle)).toShape()],list(begin+axis*run+A.Vector(*shift))

def geometry():
    import FreeCAD as A
    import Part
    from xb11_upstream_route import rounded
    def line(a,b):return Part.makeLine(A.Vector(*a),A.Vector(*b))
    def bez(p):
        c=Part.BezierCurve();c.setPoles([A.Vector(*q) for q in p]);return c.toShape()
    rise,end=s_bend([-19,-21,115],[0,-9,15],10)
    start=A.Vector(129,-5.9,78);finish=A.Vector(*R.FAN[-1]);u=A.Vector(finish.x-start.x,finish.y-start.y,0);length=u.Length;u.normalize()
    rad=6;down=A.Vector(0,0,-1)
    def first(t):return start+down*(rad*math.sin(t))+u*(rad*(1-math.cos(t)))
    a=first(math.pi/2);b=a+u*(length-2*rad)
    def second(t):return b+u*(rad*math.sin(t))+down*(rad*(1-math.cos(t)))
    tail=second(math.pi/2)
    neck=[Part.Arc(start,first(math.pi/4),a).toShape(),line(list(a),list(b)),Part.Arc(b,second(math.pi/4),tail).toShape(),line(list(tail),list(finish)),line(list(finish),R.PAD)]
    return {
        'W043':[line(R.SOURCE,R.PREF[0]),bez(R.PREF),line(R.PREF[-1],[-73,-21,115])],
        'W077':[line([-22,-21,115],[-19,-21,115])]+rise+[line(end,[40,-30,130])],
        'W078':list(rounded([A.Vector(*p) for p in [[40,-30,130],[129,-30,130],[129,-5.9,130],[129,-5.9,78]]],6).Edges)+neck}

if __name__=='__main__':
    R.geometry=geometry
    R.main()
    import body_ground_routes_r1 as M
    p=R.OUT/'checks.json';c=__import__('json').loads(p.read_text(encoding='utf-8'))
    c.update(datum_script_sha256=M.sha(__import__('pathlib').Path(__file__)),
        P_SYS_labels_plus_X=['.2','.1','.3','.4','.5'],nominal_blanks_mm=R.LIMITS,
        factory_and_final_MAIN_exact_arc_radius_mm=[10,6],red_extra_allowance_mm=60,
        total_input_blanks_mm=330,no_extra_K1474=True,
        change_reason='Named R1 DATA/PWM strap hits; no repeated unchanged corridor. Exact late R6 approach avoids rigid MAIN GND strap. First two P_SYS physical labels exchanged, unchanged single electrical potential, neither old wire yet selected.')
    M.save(p,c)
