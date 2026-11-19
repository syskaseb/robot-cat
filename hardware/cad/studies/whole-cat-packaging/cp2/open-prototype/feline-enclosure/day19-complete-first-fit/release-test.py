from common import *
from importlib.machinery import SourceFileLoader
j=SourceFileLoader('bight',str(P/'joint-layout.py')).load_module()
s=(G/'named-check.py').read_text().split('tr=json.loads')[0].replace('whole-cat19G.FCStd','whole-cat19I.FCStd');exec(s)
from scipy.spatial import cKDTree
from collections import defaultdict
parts={'fixed':rd(H19/'space-map.json')['members'],'yaw':[],'pitch':[]}
# Cups are the actual support at the bottom boot. The flexing jacket region begins at its upper face.
parts['fixed']=[n for n in parts['fixed'] if n!='XT60H_mated_with_boots']
b=j.layout(27,-30,[1,0]);rest=[a for a in b if a['lift']==0]
# Head is parked straight before removal. Full running sweep is checked in the seated state.
nr=j.neighbours(rest);sv=j.neighbours(b)
sv={n:v for n,v in sv.items() if not n.startswith('JR_pitch pose') or n=='JR_pitch pose 8'}
for q in b:
 pts=np.asarray(q['points']);pts=pts[np.r_[True,np.linalg.norm(np.diff(pts,axis=0),axis=1)>.001]]
 screen('battery_'+str(q['lift'])+'_'+str(q['side']),0,0,circle(pts[1:],2.4))
wr('battery-jackets.json',dict(rows=rows,rest_margin_mm=nr,parked_withdrawal_margin_mm=sv,developed_mm=82.4070751,unplug_stroke=14,free_length_at_radius_17=[11,math.pi*17,18],project_inner_bend=14.6,physical_measured=None));print([(k['field'],[(h['part'],h['point']) for h in k['hits']]) for k in rows if k['hits']])
