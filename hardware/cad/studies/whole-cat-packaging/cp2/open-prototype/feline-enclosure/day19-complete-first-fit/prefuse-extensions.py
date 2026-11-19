from common import *
s=(P/'smooth-lower-lay.py').read_text();exec(s[:s.index('tr={};led={}')]);d=rd(H19/'whole-termination-plan.json');hp=rd(P/'shared-fuse-transfer.json')
from scipy.ndimage import distance_transform_edt
field=field-distance_transform_edt(field==0,sampling=step)
data={}
# Both continuations are dedicated red 1 mm2 HELU 23502 per the selected AUX
# harness recipes. The two source ends share one overlap at their physical joint.
# Lay at the short and long delivered limits before choosing the actual blank.
for w in ['XB21','XA02']:
 data[w]=[]
 records=hp['routes'] if w=='XB21' else [d['FHAC']['F_AUX.out']]
 for rec in records:
    path=np.array(rec.get('points',rec.get('minimum_lay')));v=unit(path[-1]-path[-2]);t=path[-1]
    if w=='XB21':
        start=np.array(d['endpoints']['P_AUX.3']['point']);u=np.array([0.,1,0]);q=t-8*v;ea=v
        rr=17.3;ang=math.radians(38);zz=np.array([0.,0,-1])
        a=np.linspace(0,ang,43);b=start+rr*(np.sin(a)[:,None]*u+(1-np.cos(a))[:,None]*zz)
        uv=math.cos(ang)*u+math.sin(ang)*zz;nn=math.sin(ang)*u-math.cos(ang)*zz
        c=b[-1]+rr*(np.sin(a)[:,None]*uv+(1-np.cos(a))[:,None]*nn)
        prefix=np.vstack([b[:-1],c[:-1]]);p=c[-1]
        seed=np.array([[-85,1,47],[-90,22,49],[-90,51,61],[-82,60,92],q+18*ea])
    else:
        p=t-8*v;u=v;q=np.array(d['endpoints']['AUX.VIN']['point']);ea=np.array([0.,0.,1.])
        seed=np.linspace(p+18*u,q+19*ea,7)[1:-1]
    pp,vv,r=fit(p,u,q,ea,17.0,2.5,seed)
    if w=='XB21':
        pp=np.vstack([prefix,pp]);r['developed']=length(pp);r['start_underpass']=dict(centre_radius=rr,angle_degrees=38,entry=start.tolist(),exit=p.tolist())
    r.update(source='HELU 23502 red 1 mm2 OD2.5; source fixed R15',factory_stock_mm=rec.get('stock',84.5),dedicated_blank_mm=5*math.ceil((r['developed']+(11 if w=='XB21' else 3)+25)/5),external_termination_debit=11 if w=='XB21' else 3,lap_included_in_developed_mm=8,loose_dress_mm=25,points=pp.round(4).tolist(),actual=None)
    data[w].append(r)
wr('prefuse-extensions.json',data);print([(w,[(round(q['developed'],1),round(q['minimum_centre_radius']-1.25,1)) for q in vv]) for w,vv in data.items()])
