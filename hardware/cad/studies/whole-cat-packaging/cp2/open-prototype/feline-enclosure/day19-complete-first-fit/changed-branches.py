from common import *
s=(P/'smooth-lower-lay.py').read_text().split('tr={};led={}')[0];exec(s)
from scipy.ndimage import distance_transform_edt
field=field-distance_transform_edt(field==0,sampling=step)
d=rd(H19/'whole-termination-plan.json');hp=rd(P/'shared-fuse-transfer.json');out={};endpoints={};ep=d['endpoints']
for k,v in ep.items():
 if k.startswith('P_AUX.'):
    p=v['point'];v.update(point=[-2-(p[0]+85),81-(p[1]+45.5),131.5+(p[2]-54.5)],outward_axis=[0,-1,0]);endpoints[k]=v
for w,z in [('W026',67),('W041',80)]:
 for suffix,x,sg in [('factory',-26.75,-1),('custom',8.75,1)]:
    k=w+'_Joint.'+suffix;ep[k].update(point=[x,-34,z+4.45],outward_axis=[sg,0,0]);endpoints[k]=ep[k]
for w in ['XB21','XB11','XB31','XA02','XA03','W026/factory','W026/custom','W041/factory','W041/custom']:
 row=rows[w];a,b=row['ends'];q0=ep.get(a);q1=ep.get(b)
 pp0=np.array(q0['point']);pp1=np.array(q1['point']);u=np.array(q0.get('outward_axis',[0,0,1]));v=np.array(q1.get('outward_axis',[0,0,1]));dia=2.5;target=17.3;L=[84.5]
 if w=='XB21':L=[84.5,89.5,94.5]
 if w.startswith('W'):
    dia=4.2 if 'custom' in w else 4.8;target=25.2+dia/2+.7 if 'custom' in w else 18.
    if w.endswith('factory'):u=np.array([1,0,0])
 out[w]=[]
 for stock in L:
    p,e=pp0.copy(),pp1.copy();end=8 if w.startswith('XB') or w=='XA02' else 0
    if w.startswith('XB'):
        piece=next(q for q in hp['routes'] if q['stock']==stock)['points'] if w=='XB21' else d['FHAC'][b]['minimum_lay']
        t=np.asarray(piece);v=unit(t[-1]-t[-2]);e=t[-1]-8*v
    if w=='XA02':
        t=np.asarray(d['FHAC'][a]['minimum_lay']);u=unit(t[-1]-t[-2]);p=t[-1]-8*u
    seed=np.linspace(p+21*u,e+22*v,7)[1:-1]
    if w=='XB21':seed=np.array([[0,46,132],[-12,23,125],[-46,18,108],[-65,48,101],e+17*v])
    if w=='XB31':seed[:,2]+=16*np.sin(np.linspace(.3,2.8,5))
    if w=='XB11':seed[:,0]+=23*np.sin(np.linspace(.3,2.8,5))
    if w=='W041/custom':seed=np.array([[32,-34,84],[47,-41,74],[27,-70,66],[-18,-76,58],[-43,-45,57]])
    path,_,q=fit(p,u,e,v,target,dia,seed);term_debit=11 if w.startswith('XB') else 3 if w=='XA02' else 14 if w=='XA03' else row['material'][0]['termination_project_allowance_mm']
    q.update(points=path.round(4).tolist(),diameter=dia,stock_mm=stock if end else None,planned_blank_mm=5*math.ceil((q['developed']+term_debit+25)/5),ends_outside_lay_mm=term_debit,lap_counted_in_lay=end,project_dress=25,material=(row['material'][0]['sku'] if w.startswith('W') else 'HELU23502 red 1 mm2'),actual_cut_fit_slack=None)
    out[w].append(q)
 wr('changed-branch-lays.json',dict(endpoints=endpoints,rows=out))
print([(w,round(v[0]['developed']),round(v[0]['minimum_centre_radius']-v[0]['diameter']/2,1)) for w,v in out.items()])
