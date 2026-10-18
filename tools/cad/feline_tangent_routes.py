"""Pure tangent-continuous cable curves. Geometry only, never clearance.

Equal/unequal tangent-distance biarcs join two prescribed endpoint tangents.
No hidden polyline corner or chord is counted as a bend-radius-qualified path.
"""
import math


def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def mul(a,s): return tuple(x*s for x in a)
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def norm(a): return math.sqrt(dot(a,a))
def unit(a):
    n=norm(a)
    if n<1e-10: raise ValueError('Undefined direction')
    return mul(a,1/n)


def line(p,q):
    return dict(kind='line',start=list(p),end=list(q),length=norm(sub(q,p)))


def arc(p,t,q):
    """Circle from endpoint/tangent/endpoint; reject loops >180 degrees."""
    t=unit(t);v=sub(q,p);along=dot(v,t);perp=sub(v,mul(t,along));h=norm(perp)
    if h<1e-8:
        if along<=0: raise ValueError('Backward straight')
        return line(p,q)
    b=mul(perp,1/h);R=dot(v,v)/(2*h);angle=2*math.atan2(h,along)
    if angle>math.pi+1e-8: raise ValueError('Loop arc is not this routing family')
    end_t=add(mul(t,math.cos(angle)),mul(b,math.sin(angle)))
    return dict(kind='arc',start=list(p),end=list(q),tangent=list(t),bend=list(b),
                radius=R,angle=angle,length=R*angle,end_tangent=list(end_t))


def reverse(s):
    if s['kind']=='line': return line(s['end'],s['start'])
    return arc(s['end'],mul(s['end_tangent'],-1),s['start'])


def biarc(p,t0,q,t1,ratio=1):
    """Two circular arcs with a common tangent; ratio=d1/d2 >0."""
    if ratio<=0: raise ValueError('Positive tangent ratio required')
    t0=unit(t0);t1=unit(t1);v=sub(q,p)
    a=2*ratio*(1-dot(t0,t1));b=2*dot(v,add(mul(t0,ratio),t1));c=-dot(v,v)
    if abs(a)<1e-12:
        if b<=0: raise ValueError('No forward tangent solution')
        d2=-c/b
    else:
        disc=b*b-4*a*c
        if disc<0: raise ValueError('No real tangent solution')
        # Stable positive quadratic root, including negative b.
        d2=(-2*c/(b+math.sqrt(disc))) if b>=0 else (-b+math.sqrt(disc))/(2*a)
    d1=ratio*d2
    m=mul(add(mul(add(p,mul(t0,d1)),d2),mul(sub(q,mul(t1,d2)),d1)),1/(d1+d2))
    s0=arc(p,t0,m);s1=reverse(arc(q,mul(t1,-1),m))
    end0=unit(sub(s0['end'],s0['start'])) if s0['kind']=='line' else s0['end_tangent']
    start1=unit(sub(s1['end'],s1['start'])) if s1['kind']=='line' else s1['tangent']
    if norm(sub(end0,start1))>1e-6: raise ValueError('Non-tangent biarc')
    return [s0,s1]


def quarter_prefix(p,d,b,R=30,first=3,grip=9):
    d=unit(d);b=unit(b)
    if abs(dot(d,b))>1e-8: raise ValueError('Nonperpendicular bend')
    a=add(p,mul(d,first));q=add(add(a,mul(d,R)),mul(b,R));tip=add(q,mul(b,grip))
    return [line(p,a),arc(a,d,q),line(q,tip)]


def samples(s,step=3):
    n=max(1,math.ceil(s['length']/step));p=s['start']
    for i in range(n+1):
        f=i/n
        if s['kind']=='line': yield add(p,mul(sub(s['end'],p),f))
        else:
            a=s['angle']*f
            yield add(p,add(mul(s['tangent'],s['radius']*math.sin(a)),
                            mul(s['bend'],s['radius']*(1-math.cos(a)))))


def length(parts): return sum(s['length'] for s in parts)


def min_radius(parts):
    return min((s['radius'] for s in parts if s['kind']=='arc'),default=math.inf)
