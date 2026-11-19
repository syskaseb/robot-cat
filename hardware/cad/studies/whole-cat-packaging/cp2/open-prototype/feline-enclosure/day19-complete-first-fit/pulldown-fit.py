from common import *
s=(G/'named-check.py').read_text().split('tr=json.loads')[0].replace('whole-cat19G.FCStd','whole-cat19I.FCStd');exec(s)
r=rd(P/'remote-pulldown-lay.json');w=rd(F/'service-lay.json')
hard=rd(H19/'space-map.json')['members']+[n for n in D.members if n.startswith('I19_FuseBand_')]
yaw=['E19_UpperYawCover','D19D_YawSaddle','BR_FLANK_HP_PAIR','MG92B_Head_pitch'];pitch=['D19D_PitchBack','D19D_OpticsCarrier','D19D_Face'];parts={'fixed':[n for n in hard if n not in yaw+pitch],'yaw':yaw,'pitch':pitch}
for n in ['yaw','tail','pitch']:
 qs=r['pitch'] if n=='pitch' else [w['fixed']['JR_'+n]]
 for q in qs:
    y=q.get('yaw',0);p=np.asarray(q['points']);ss=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
    # Test complete re-clocked pitch lead. Gross hard cross section of the
    # insulated tap is reserved only over its static 50 mm, clear of the mated port.
    if n=='pitch':screen(n+'246',y,0,profile(p,3.5,1.8))
    pp=p[(ss>=4)&(ss<=48)]
    screen(n+' insulated taps',y,0,circle(pp,3.35))
wr('pulldown-fit.json',dict(rows=rows,provisional_external_diameter=6.7,measured=None));print([(v['field'],v['yaw'],[(a['part'],a['point']) for a in v['hits']]) for v in rows if v['hits']])
