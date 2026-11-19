from common import *
s=(G/'named-check.py').read_text().split('tr=json.loads')[0].replace('whole-cat19G.FCStd','whole-cat19I.FCStd');exec(s)
parts={'fixed':rd(H19/'space-map.json')['members']+[n for n in D.members if n.startswith('I19_FuseBand_')],'pitch':[],'yaw':[]};b=rd(H19/'battery-leads.json');l=rd(P/'lower-approaches.json')
positive=rd(P/'W075-seated.json');units={'W075':positive,'W001':l['W001'],'pack plus':l['pack1'],'pack minus':l['pack-1']}
for n,q in units.items():
 p=np.array(q['points']);screen(n,0,0,circle(p[1:-1],q['diameter']/2))
wr('battery-lower-fit.json',dict(rows=rows,F0_limit=50,W075_required=positive['project_free_mm']+5,pack_exits_are_projected=True,source_native=sha(native)));print([(r['field'],r['hits']) for r in rows if r['hits']])
