"""Lay a common accessible transfer across the deck split. Branches use available interior near real mouths."""
from common import *
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from scipy.spatial import cKDTree
from scipy.ndimage import map_coordinates
m=np.load(P/'clearance-cache.npz');D=m['dist'];o=m['origin'];step=float(m['step']);d=rd(G/'whole-termination-plan.json');old=rd(G/'named-approaches.json');rows={w['wire']:w for w in d['wires']}
def arr(p):return np.asarray(p,dtype=float)
def length(p):return float(np.linalg.norm(np.diff(p,axis=0),axis=1).sum())
def clear(p):return map_coordinates(D,((arr(p)-o)/step).T,order=1,mode='constant',cval=0)
def samples(a,b,ds=1):return np.linspace(a,b,max(2,1+math.ceil(np.linalg.norm(b-a)/ds)))
def sight(a,b,r):return min(clear(samples(a,b,1.5)))>=r
# Four-mm routing lattice for selecting a connected corridor. Actual jacket profiles use submillimetre BRep tests.
grid=D[::2,::2,::2];good=grid>=3.4;coords=np.argwhere(good);world=o+coords*4;tree=cKDTree(world)
ids=np.full(grid.shape,-1,dtype='i4');ids[tuple(coords.T)]=np.arange(len(coords));ar=[];ac=[];av=[]
import itertools
for delta in itertools.product([-1,0,1],repeat=3):
 if delta<=(0,0,0):continue
 dt=np.array(delta);other=coords+dt;ok=((other>=0)&(other<np.array(grid.shape))).all(axis=1);src=np.flatnonzero(ok);dst=ids[tuple(other[ok].T)];ok=dst>=0;src=src[ok];dst=dst[ok];c=np.minimum(grid[tuple(coords[src].T)],grid[tuple(coords[dst].T)]);w=4*np.linalg.norm(dt)*(1+3/c**1.1)
 ar.extend([src,dst]);ac.extend([dst,src]);av.extend([w,w])
graph=coo_matrix((np.concatenate(av),(np.concatenate(ar),np.concatenate(ac))),shape=(len(coords),)*2).tocsr()
def node(p):
 _,ix=tree.query(p,k=24);return next((i for i in ix if sight(p,world[i],2.25)),ix[0])
def travel(a,b,r=3):
 a,b=arr(a),arr(b)
 if sight(a,b,r):return [a,b]
 ia,ib=node(a),node(b);dist,pred=dijkstra(graph,indices=ia,return_predecessors=True)
 if not np.isfinite(dist[ib]):raise ValueError(('unreachable',a,b))
 chain=[ib]
 while chain[-1]!=ia:chain.append(pred[chain[-1]])
 points=[a,*world[chain[::-1]],b];out=[a];i=0
 while i<len(points)-1:
    j=next((k for k in range(len(points)-1,i+1,-1) if sight(arr(points[i]),arr(points[k]),r)),i+1);out.append(arr(points[j]));i=j
 return out
def rounded(points,r=12):
 ps=[arr(points[0])]
 for a in points[1:]:
    if np.linalg.norm(arr(a)-ps[-1])>.1:ps.append(arr(a))
 out=[ps[0]];rads=[]
 for a,b,c in zip(ps,ps[1:],ps[2:]):
    u=(b-a)/np.linalg.norm(b-a);v=(c-b)/np.linalg.norm(c-b);angle=math.acos(np.clip(u@v,-1,1))
    if angle<.015:continue
    if angle>3.1:out.append(b);continue
    tang=min(r*math.tan(angle/2),.47*np.linalg.norm(b-a),.47*np.linalg.norm(c-b));rad=tang/math.tan(angle/2);n=v-u*(u@v);n/=np.linalg.norm(n);q=b-u*tang
    arc=[q+rad*(math.sin(t)*u+(1-math.cos(t))*n) for t in np.linspace(0,angle,max(5,math.ceil(rad*angle)))]
    out.extend(arc);rads.append(rad)
 out.append(ps[-1]);fn=[]
 for a,b in zip(out,out[1:]):fn.extend(samples(a,b,1.25)[:-1])
 return arr(fn+[out[-1]]),min(rads,default=None)
tracks={};ledger={}
for key,v in d['endpoints'].items():
 if key.startswith('D_FL.'):
    x,y,z=v['point'];v['point']=[274-x,-139-y,z];v['outward_axis']=[0,-1,0]

def route(w,entry,via,end,od=2.1,r=12):
 ps=list(map(arr,entry));markers=[*via,end[0]]
 for b in markers:ps.extend(travel(ps[-1],b)[1:])
 ps.extend(map(arr,end[1:]));pts,rad=rounded(ps,r)
 tracks[w]=dict(points=np.round(pts,4).tolist(),diameter=od);ledger[w]=dict(stations=np.round(ps,3).tolist(),transport_mm=round(length(pts),3),min_constructed_bend_mm=rad,section_mm=od,actual_cut_fit_slack=None)
# Common nine-lead drop at the split, in three columns by three. Along the side of the tail,
# PWM takes the outside wall at x=190 before returning to the component face.
for i in range(3):
 for j in range(3):
    w=(['XB','XB','XS'][j])+str(i+1)+['2','3','3'][j];q=rows[w];net=q['from_JR_to'];branch=d['JR'][['yaw','pitch','tail'][i]]['branches'][j];s=arr(branch['points'][-1]);u=s-arr(branch['points'][-2]);u/=np.linalg.norm(u)
    y=-47.6+(j-1)*3.2;xx=12+(i-1)*3.2;z=155+(i-1)*2.8
    via=[[xx,y,184],[xx,y,168],[xx+10,y,z]]
    if j==0:
        end=arr(d['FHAC'][net]['end_or_overlap']);h=arr(d['FHAC'][net]['minimum_lay'][-2]);v=(end-h)/np.linalg.norm(end-h);stop=[end+8*v,end]
    elif j==1:
        end=arr(d['endpoints'][net]['point']);v=arr(d['endpoints'][net]['outward_axis']);via+=[[end[0]-12,y,z]];stop=[end+12*v,end+3*v,end]
    else:
        end=arr(d['endpoints'][net]['point']);via+=[[153,y,z],[187+(i-1)*2.8,-33,152],[189+(i-1)*2.8,23,151]];stop=[end+[0,-9,0],end+[0,-2,0],end]
    route(w,[s,s+8*u],via,stop)
    t=ledger[w];t.update(net=net,project_bulk_blank_mm=5*math.ceil((t['transport_mm']+8+q['other_termination_mm']+30)/5),JR_lap_on_body=8,terminal_debit=q['other_termination_mm'],dress_and_trim=30,material=q['material_role'])
# Source H3 plug and common 900 mm cable stay keyed. Separate D and G at the back of the bank.
for i,(w,net) in enumerate([('W002','D_FL.1'),('W003','G2.4')]):
 end=arr(d['endpoints'][net]['point']);v=arr(d['endpoints'][net]['outward_axis']);h=np.array(d['units']['BUS900']['common_stations'][:8]);h[3:6,0]=202.;h[4,2]=161.;h[5,1]=29.;h[:,0]+=(i-.5)*1.7
 route(w,h,[[end[0],-89 if w=="W002" else -52,149]],[end+12*v,end+3*v,end],2.4,14)
 ledger[w]['one_900_keep_incl_16_11_35']=math.ceil(ledger[w]['transport_mm']+62)
# 210 mm input and uncut paired USB-C output parent. Last 2 mm are bare solder-land approaches.
for i,w in enumerate(['W079','W080']):
 s=arr(rows[w]['shared_approach'][0]);end=arr(rows[w]['shared_approach'][-1])
 route(w,[s,s+[7,0,0]],[[5,-51-i*3.3,109],[48,-51-i*3.3,109],[85,-24-i*3.3,110]],[end+[0,0,11],end+[0,0,2],end],3.,16)
 ledger[w]['output_keep_incl_25_5_20']=math.ceil(ledger[w]['transport_mm']+50)
s=arr(d['FHAC']['F_PI.out']['end_or_overlap']);end=arr(d['endpoints']['MAIN.VIN']['point'])
route('W078',[s,s+[0,-5,1]],[],[end+[0,0,13],end+[0,0,2],end],3,14);ledger['W078']['required_incl_8_5_15']=math.ceil(ledger['W078']['transport_mm']+28)
# PCB 3006's two real plated holes are 12.70 mm apart in X on the installed full-steel axes.
# Eagle X1 has a 3.5 mm pitch and 180-degree turn. Its wire side faces the nearest board edge (+Y).
# Keep the full installed gross block as a population reserve, using its outer face as the handoff.
for w,x,sy in [('EXT023',94.2,75),('EXT024',90.7,79)]:
 mouth=arr([x,-28.431,133.6]);outside=arr([x,-25.8,133.6]);sp=arr([128,sy,150.4]);route(w,[outside,outside+[0,6,0]],[[113,30,144]],[sp-[0,0,8],sp-[0,0,2],sp],2.1,12)
 ledger[w].update(terminal_screw_pad=[x,-32.031,129.6],terminal_side_project_mouth=mouth.tolist(),external_field_start=outside.tolist(),speaker='outside underside terminal area; delivered terminal location unknown',inside_module_to_outer_field_mm=2.631)
wr('named-approaches.json',tracks);wr('shared-lay.json',dict(allocations=ledger,channel='9 x 2.1 through split; 3x3 at pitch 3.2, then divide to fuse, bank and outer return. Power pair on separate lower level. H3 two cores of same keyed housing.',core_count=9,occupied_JR_envelope=[8.5,8.5],actual=None));print([(k,round(v['transport_mm'])) for k,v in ledger.items()])
