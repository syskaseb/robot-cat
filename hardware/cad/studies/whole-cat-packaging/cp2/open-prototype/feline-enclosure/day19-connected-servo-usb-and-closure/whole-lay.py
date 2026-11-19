"""Physical unit lengths and shared lay planes in the removable upper gallery, mm."""
from pathlib import Path
import json, math, numpy as np
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
src=(E/'unit-layout.py').read_text()
exec(src[src.index('X,Y,Z='):src.index('for role,S,E,fn')])
def out(path):return np.asarray(path).round(5).tolist()
def wr(n,data):(P/n).write_bytes((json.dumps(data,indent=1)+'\n').encode())
fixed={};moving=[];pairs={}
def record(name,parts,ds,rad,owner,**kw):
    path=chain(parts);free=sum(ds);stock=500 if name=='DATA500' else 300 if name.startswith('JR') else 250
    debit=[26,448,26] if stock==500 else [12,246,25,9,8] if stock==300 else [11.45,223.55,15]
    assert abs(free-debit[1])<.003,(name,free)
    r=dict(unit=name,owner=owner,free=free,stock=stock,ends_and_free=debit,analytic_lengths=ds,centre_radius=rad,points=out(path),**kw)
    if 'yaw' in kw:moving.append(r)
    else:fixed[name]=r
    return path
# BUS moves onto the opposite side of the tray. Both approach legs rise in one
# open central chimney before a single horizontal U in the accessible upper deck.
S=vec([6,-.66,104.1]);r=34.;L=21;h=184-S[2]-2*r
a=line(S,S+L*X);b=arc(a[-1],X,Z,r,math.pi/2);c=line(b[-1],b[-1]+h*Z);d=arc(c[-1],Z,-X,r,math.pi/2)
K=vec([140,67.5,184]);p,ds,ru=turn(d[-1],K,-X,448-L-h-math.pi*r)
record('DATA500',[a,b,c,d,p],[L,math.pi*r/2,h,math.pi*r/2]+ds,min(r,ru),'body',inner_R=min(r,ru)-3.4,end_axis=out(X),boot_end=out(K))
# Move the matched tail pair and JR branch UP together. The MG exits -X,
# rolls over the fixed bank and mates along +X clear of S1 and the battery.
s=vec([129.5,-63.8,130]);e=vec([147,-63.8,182]);p,ds,r=turn(s,e,-X,223.55)
record('MG_tail',[p],ds,r,'body',inner_R=r-math.hypot(1.75,.9))
pairs['tail']=dict(inlet=out(e),outlet=out(e+30*X),owner='body')
# Fixed yaw exit and the fixed body connector stay outside the Pi plane.
# Exit diagonal is on the outboard side of Pi prior to ascending to the deck.
s=vec([-119.5,0,53.2]);n=unit(-.84*Y+.54*Z);r=24.5
a=arc(s,X,n,r,math.pi/2);b=line(a[-1],a[-1]+34*n)
angle=math.acos(n@Z);c=arc(b[-1],n,unit(Z-n*(n@Z)),r,angle)
h=185-r-c[-1,2];d=line(c[-1],c[-1]+h*Z);g=arc(d[-1],Z,X,r,math.pi/2)
ds=[r*math.pi/2,34,r*angle,h,r*math.pi/2];rem=223.55-sum(ds);assert rem>0
last=line(g[-1],g[-1]+rem*X);record('MG_yaw',[a,b,c,d,g,last],ds+[rem],r,'body',inner_R=r-math.hypot(1.75,.9))
pairs['yaw']=dict(inlet=out(last[-1]),outlet=out(last[-1]+30*X),owner='body')
# Pitch servo is fixed to the yaw saddle. Store its whole factory lead and
# mated pair on that member. A one-turn rising-pitch helix separates its own strands.
s=vec([-159,-43.8,131.5]);a=line(s,s-9*Y);b=arc(a[-1],-Y,X,25,math.pi/2)
r=24.5;dy=-6.;theta=np.linspace(0,math.tau,241)
# Smooth axial lift with zero slope at start/end: both tangents are +X.
c=b[-1]+r*(np.sin(theta)[:,None]*X+(1-np.cos(theta))[:,None]*Z)+(dy*(theta-np.sin(theta))/math.tau)[:,None]*Y
helix_len=float(np.trapezoid(np.sqrt(r*r+(dy*(1-np.cos(theta))/math.tau)**2),theta))
ds=[9,25*math.pi/2,helix_len];rem=223.55-sum(ds);last=line(c[-1],c[-1]+rem*X)
record('MG_pitch',[a,b,c,last],ds+[rem],24.45,'yaw',inner_R=22.47)
pairs['pitch']=dict(inlet=out(last[-1]),outlet=out(last[-1]+30*X),owner='yaw')
for role,n,first in [('yaw',Y,58),('tail',Y,3)]:
    s=vec(pairs[role]['outlet']);a=line(s,s+first*X);r=24.3;b=arc(a[-1],X,n,r,math.pi);remain=246-first-r*math.pi
    c=line(b[-1],b[-1]-remain*X)
    record('JR_'+role,[a,b,c],[first,r*math.pi,remain],r,'body',fan=out(c[-1]),fan_axis=out(-X),inner_R=r-1.75)
# A moving start, two compliant direction changes and a stationary FAN on
# the upper shelf. No fixed tie between the moving inlet and the turn.
yc=vec([-130,0,127]);K=vec([-57,-5,183]);s=vec(pairs['pitch']['outlet'])
for deg in [-20,-10,0,10,20]:
    a=math.radians(deg);R=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
    start=(s-yc)@R.T+yc;t=R@X;r=24.2
    b=arc(start,t,Z,r,math.pi/2);h=K[2]-2*r-start[2]
    c=line(b[-1],b[-1]+h*Z);d=arc(c[-1],Z,X,r,math.pi/2)
    p,ds,ru=turn(d[-1],K,X,246-h-math.pi*r)
    record('JR_pitch',[b,c,d,p],[r*math.pi/2,h,r*math.pi/2]+ds,min(r,ru),'flex yaw/body',yaw=deg,fan=out(K),fan_axis=out(-X),inner_R=min(r,ru)-1.75)
for q in list(fixed.values())+moving:
    if 'fan' not in q:continue
    end=vec(q['fan']);q['branches']=[]
    for k in [-1,0,1]:
        u=vec(q['fan_axis'])*math.cos(.125*k)+Y*math.sin(.125*k)
        q['branches'].append(out([end,end+25*u,end+34*u,end+42*u]))
old=json.loads((E/'installed-looms.json').read_bytes())
wr('whole-lay.json',dict(fixed=fixed,pitch_transfer=moving,pairs=pairs,E2=old['E2'],FFC=old['FFC'],ToF=old['ToF'],actual_fit_cut_slack=None))
print(pairs,[(q['yaw'],round(q['inner_R'],2)) for q in moving])
