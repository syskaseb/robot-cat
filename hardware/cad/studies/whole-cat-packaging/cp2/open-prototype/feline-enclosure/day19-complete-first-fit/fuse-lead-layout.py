from common import *
s=(G/'named-check.py').read_text().split('tr=json.loads')[0].replace('whole-cat19G.FCStd','whole-cat19I.FCStd');exec(s)
parts={'fixed':rd(H19/'space-map.json')['members']+[n for n in D.members if n.startswith('I19_FuseBand_')],'yaw':[],'pitch':[]}
f=rd(H19/'whole-termination-plan.json')['FHAC']['F_HP.in'];origin=np.array(f['case_exit']);u=np.array([-1.,0,0]);r=18
def path(straight,n,length):
 n=np.array(n,float);n/=np.linalg.norm(n);a=origin+straight*u;tail=length-straight-math.pi*r/2
 b=a+r*(u+n);return np.vstack([np.linspace(origin,a,45)[:-1],*[a+r*(math.sin(t)*u+(1-math.cos(t))*n) for t in np.linspace(0,math.pi/2,36)[:-1]],np.linspace(b,b+tail*n,max(3,math.ceil(tail)+1))])
proposals=[('outboard of upper holder',43,[0,.8,.6]),('outboard of upper holder, service from forward edge',46,[0,-.3,.954]),('low axial transfer to front bay',47,[0,.954,.3])]
candidates=[]
for tag,first,n in proposals:
 results=[];routes=[]
 for L in [84.5,94.5]:
    p=path(first,n,L);bare=4.35
    d=np.linalg.norm(p-p[-1],axis=1)
    screen(tag+str(L),0,0,circle(p[(d>=bare)][1:],2.1))
    screen(tag+' bare at '+str(L),0,0,circle(p[(d<bare)],.75))
    results.extend(rows[-2:]);routes.append(dict(stock=L,points=p.tolist(),bare_min=4.35,raw_bare_range=[4.35,8.35],end_or_overlap=p[-1].tolist()))
 candidates.append(dict(tag=tag,first_straight=first,bend_radius=r,direction=n,results=results,routes=routes))
 if not any(q['hits'] for q in results):break
wr('fuse-lead-layout.json',dict(candidates=candidates,selected=next((i for i,q in enumerate(candidates) if not any(t['hits'] for t in q['results'])),None)));print([(q['tag'],[(x['field'],x['hits']) for x in q['results'] if x['hits']]) for q in candidates])
