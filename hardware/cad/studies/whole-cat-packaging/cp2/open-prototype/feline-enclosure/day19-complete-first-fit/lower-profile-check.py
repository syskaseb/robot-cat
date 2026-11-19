from common import *
s=(G/'named-check.py').read_text().split('tr=json.loads')[0].replace('whole-cat19G.FCStd','whole-cat19I.FCStd');exec(s)
tr=rd(P/'lower-approaches.json');plan=rd(H19/'whole-termination-plan.json');wires={q['wire']:q for q in plan['wires']}
hard=rd(H19/'space-map.json')['members']+[n for n in D.members if n.startswith('I19_FuseBand_')];parts={'fixed':hard,'yaw':[],'pitch':[]}
for n,q in tr.items():
 p=np.asarray(q['points']);od=q['diameter'];kind='jacket'
 # Stop insulation at a WAGO mouth; next stage is the specified strip inside the cavity.
 # At the two gross pack/boot departure surfaces the first exposed section is already outside.
 if n=='W060':
    distance=np.linalg.norm(p-p[-1],axis=1);screen(n+' bare solder approach',0,0,circle(np.linspace(p[-1]+[0,0,1.95],p[-1]+[0,0,.22],10),.38));p=p[distance>=2]
 screen(n,0,0,circle(p[1:-1],od/2))
wr('lower-profile-fit.json',dict(rows=rows,source=sha(native)));print([(k['field'],[(h['part'],h['point']) for h in k['hits']]) for k in rows if k['hits']])
