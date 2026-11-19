from common import *
s=(G/'named-check.py').read_text().split('tr=json.loads')[0].replace('whole-cat19G.FCStd','whole-cat19I.FCStd');exec(s)
r=rd(P/'remote-pulldown-lay.json');w=rd(F/'service-lay.json')
hard=rd(H19/'space-map.json')['members']+[n for n in D.members if n.startswith('I19_FuseBand_')]
yaw=['E19_UpperYawCover','D19D_YawSaddle','BR_FLANK_HP_PAIR','MG92B_Head_pitch'];pitch=['D19D_PitchBack','D19D_OpticsCarrier','D19D_Face'];parts={'fixed':[n for n in hard if n not in yaw+pitch],'yaw':yaw,'pitch':pitch}
for n in ('yaw','tail','pitch'):
 for q in (r['pitch'] if n=='pitch' else [w['fixed']['JR_'+n]]):
    y=q.get('yaw',0);p=np.asarray(q['points']);ss=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))];ds=np.diff(ss,prepend=-1);p=p[ds>.00005];ss=ss[ds>.00005]
    norm=np.array([-math.sin(math.radians(y)),math.cos(math.radians(y)),0]) if n=='pitch' else np.array([0,0,-1])
    t=np.gradient(p,axis=0);t=t/np.maximum(np.linalg.norm(t,axis=1)[:,None],.0001)
    h=np.cross(t,norm);hn=np.linalg.norm(h,axis=1);h[hn<.001]=np.cross(t[hn<.001],[1,0,0]);h=h/np.maximum(np.linalg.norm(h,axis=1)[:,None],.00001);v=np.cross(h,t)
    b=(ss>.02)&(ss<50.01);points=[p[b]+a*h[b]+c*v[b] for a in (-1.75,0,1.75) for c in (-.9,0,.9)]
    screen(n+' clocked ribbon incl grip',y,0,np.concatenate(points))
    b=(ss>6.8)&(ss<43.2);screen(n+' inner insulated window allowance',y,0,circle(p[b],3.35))
    if n=='pitch':screen(n+' free return',y,0,profile(p[ss>=49.8],3.5,1.8))
wr('tap-sections.json',dict(rows=rows,grips='local N and tangent of two installed lands; full jacket after physical mate plane. Window overmold provisional 6.7, s=6.8..43.2',physical=None));print([(q['field'],q['yaw'],q['hits']) for q in rows if q['hits']])
