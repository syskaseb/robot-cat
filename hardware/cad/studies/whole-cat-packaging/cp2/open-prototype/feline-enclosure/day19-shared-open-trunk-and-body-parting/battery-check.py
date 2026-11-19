from common import *
base=(P/'profile-check.py').read_text();exec(base[:base.index('for w,q in tr.items():')])
q=rd(P/'battery-leads.json')
# Unplug before removing the cell. Cap off during service; actual battery parent length unknown.
parts={'fixed':['H19_FrontFrame','E19_RearBase','E19_ForeLid','E19_RearLid','F19_ForeCap','F19_RearCap','Pi4B_actual_PCB','F0_FHAC0002_30A','E19_ReSpeakerSource','G19_PermaProto1608','E19_KeyedTail','Battery_GEA223S30X6GT','PBAY_G1','WAGO615_power_0_0'],'yaw':[],'pitch':[]}
parts['fixed']=[n for n in parts['fixed'] if n in D.members]
screen('W075',0,0,circle(q['input']['points'][1:-1],2.4));screen('W001',0,0,circle(q['ground']['points'][1:-1],2.4))
for row in q['battery_return']:
 for sg in [-1,1]:
    pp=np.asarray(row['points'])+[sg*1.87,-sg*1.87,0];pts=np.vstack([np.linspace(a,b,max(2,int(np.linalg.norm(b-a)/1.1)+1),endpoint=False) for a,b in zip(pp,pp[1:]) if np.linalg.norm(a-b)>.01]);screen('battery bight '+str(row['lift_mm'])+' '+str(sg),0,0,circle(pts,2.4))
wr('battery-check.json',dict(rows=rows,stock_W075=q['W075_with_5_termination_mm'],nominal_limit=50));print([(r['field'],r['hits']) for r in rows if r['hits']])
