"""One loose bundle layout. Stock is debited per physical unit, in mm."""
from pathlib import Path
import json, math, numpy as np
P=Path(__file__).parent;prev=P.parent/'day19-whole-appearance-and-moving-neck-correction'
lay=json.loads((prev/'whole-lay.json').read_bytes());T=json.loads((P/'tail-root.json').read_bytes())
X,Y,Z=np.eye(3)
def vec(p):return np.array(p,dtype=float)
def chain(parts):
    pts=[parts[0][0]]
    for a in parts:
        for v in a:
            if np.linalg.norm(v-pts[-1])>.00001:pts.append(v)
    return np.array(pts)
def arc(p,t,n,r,phi):
    a=np.linspace(0,phi,math.ceil(phi*25)+1)
    return p+r*(np.sin(a)[:,None]*t+(1-np.cos(a))[:,None]*n)
def line(a,b):
    return np.linspace(a,b,2+int(np.linalg.norm(b-a)/2.4))
def unit(a):return a/np.linalg.norm(a)
def turn(S,E,t,L):
    d=E-S;dx=d@t;v=d-dx*t;r=np.linalg.norm(v)/2
    f=(L-math.pi*r+dx)/2;back=f-dx
    assert min(f,back)>0
    a=line(S,S+f*t);b=arc(a[-1],t,unit(v),r,math.pi)
    return chain([a,b,line(b[-1],E)]),[f,math.pi*r,back],r
def double(S,E,t,L,r,sign):
    d=E-S;dx=d@t;v=d-dx*t;v0=unit(v);k=unit(np.cross(t,v0));h=np.linalg.norm(v)/(4*r)
    n1=h*v0+sign*(1-h*h)**.5*k;n2=h*v0-sign*(1-h*h)**.5*k
    f=(L-2*math.pi*r+dx)/2;back=f-dx;assert min(f,back)>0
    p=line(S,S+.55*f*t);a=arc(p[-1],t,n1,r,math.pi);b=line(a[-1],a[-1]-back*t);c=arc(b[-1],-t,n2,r,math.pi)
    return chain([p,a,b,c,line(c[-1],E)]),[.55*f,math.pi*r,back,math.pi*r,.45*f],r
rows=[]
def row(key,path,raw,debit,sections,rad,kind,**kwargs):
    rows.append(dict(unit=key,stock=raw,segments=debit,path_mm=round(sum(sections),5),analytic_sections=sections,centreline=np.asarray(path).round(4).tolist(),centre_R=rad,kind=kind,qualified=False,**kwargs))
for role,S,E,fn in [('yaw',[-119.5,0,53.2],[-49,-33,115],lambda s,e:turn(s,e,X,223.55)),('tail',[129.5,-63.8,130],[145,-89,66.2],lambda s,e:double(s,e,-X,223.55,24,1))]:
    p,ds,r=fn(vec(S),vec(E));row('MG250_'+role,p,250,[11.45,223.55,15],ds,r,'static factory: fixed case on base',inner_R=r-math.hypot(1.75,.9),datum='tail source geometry is the same MG rotation/translation as yaw; case stub is a project exit')
# JR tail already starts at X115, ends at X154, exact stock and orientation.
S=vec([115,-89,66.2]);E=vec([154,-41,66.2]);p,ds,r=turn(S,E,-X,246)
row('JR300_tail',p,300,[12,246,25,9,8],ds,r,'from the separate mated housing to three proper lap branches',inner_R=22.25,fan_direction=[1,0,0],nets=['F_TY.out','G_TAIL.5','R3.2'])
for role,st,n in [('yaw',[-79,-33,115],Z),('pitch',[-111,-51,80.5],Z)]:
    s=vec(st);r=24 if role=='yaw' else 23.8;b=arc(s,-X,n,r,math.pi);tail=246-math.pi*r
    p=chain([b,line(b[-1],b[-1]+X*tail)])
    row('JR300_'+role,p,300,[12,246,25,9,8],[math.pi*r,tail],r,'moving loop is before the stationary mating station; JR is laid openly',inner_R=r-1.75,fan_direction=[1,0,0],nets=[f['net'] for f in next(q for q in lay['jr'] if q['role']==role)['fans']])
pitches=json.loads((P.parent/'day18-body-reception-and-closed-fit/yaw-laid-factory.json').read_bytes())['rows']
for q in pitches:
    row('MG250_pitch',q['centreline'],250,[11.45,223.55,15],[223.55],None,'yaw-flexed assembly alternative',yaw=q['yaw'],inner_R=q['minimum_inner_R'],risk='changed neck, fixed rear of moving helmet; old path requires test')
# The data boots both face +X. Three rolling returns in the closed box lead
# from the back of the Pi boot to the back of BUS-C. Every straight is positive.
s=vec([6,-.66,104.1]);end=vec([92.804,78.11,133.77]);d=end-s;d[0]=0
v1=vec([0,64,27]);v2=vec([0,-64,22]);v3=d-v1-v2
turns=[v1,v2,v3];rr=[np.linalg.norm(v)/2 for v in turns];free=448-math.pi*sum(rr);dx=end[0]-s[0]
pos=(free+dx)/2;neg=pos-dx;assert neg>0 and min(rr)>=33.4
spans=[pos*.68,neg*.35,pos*.32,neg*.65];p=s.copy();seq=[]
for i,v in enumerate(turns):
    t=X*(-1)**i;a=line(p,p+t*spans[i]);b=arc(a[-1],t,unit(v),rr[i],math.pi);seq.extend([a,b]);p=b[-1]
seq.append(line(p,end));data=chain(seq);ds=[spans[0],rr[0]*math.pi,spans[1],rr[1]*math.pi,spans[2],rr[2]*math.pi,spans[3]]
row('DATA500',data,500,[26,448,26],ds,min(rr),'two actual port approaches with full project boots',OD=6.8,inner_R=min(rr)-3.4,spans=spans)
# Combine as connected occupancies. Only three flex samples of the original 5 pitch shapes
# are needed on the drawing. Actual wire/strip/cut/tie/slack remain an assembly check.
out=dict(rows=rows,ToF=dict(motion_source='../'+prev.name+'/whole-lay.json',fixed_receiver=lay['fixed_receiver'],debits=lay['debits'],jacket=2.1,minimum_moving=31.5,minimum_fixed=12.6,ends='VIN/GND/SDA/SCL to JP3 2/6/3/4',stock_available=None),FFC=dict(stock=200,free=190,both_ends=10,source='../day18-open-front-assembly/occupied-layout.json',gripping='do not count slack beyond a fixed clip'),physical_PASS=False,actual_fit_cut_slack=None)
(P/'unit-layout.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
print([(q['unit'],q.get('inner_R'),q['path_mm']) for q in rows])
