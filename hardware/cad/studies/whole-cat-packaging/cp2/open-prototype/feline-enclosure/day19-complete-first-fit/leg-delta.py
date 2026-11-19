from common import *
s=(G/'side-clearance.py').read_text()
a=s.index('skirts=');b=s.index(';pairs=[]',a)
# Only additions below the proven 96.62 mm leg height require the retained corner basis.
boxes=[[-121,-28.9,41,-65,-24.5,74],[-71,-22.9,41.2,-50.4,32.35,78.3],[-77,26,94.8,-48,35.2,98],[-40.16,-102,41.3,.14,-58.2,75.44],[109,37.7,41,115.6,40.8,75.5]]
cur=Saved(native)
for n in cur.members:
 if n.startswith('I19_FuseBand_'):boxes.append(cur.bounds(n).tolist())
s=s[:a]+'skirts='+repr(boxes)+s[b:]
s=s.replace("for i,n,h,t in pairs:","now=Saved(native); names=['H19_FrontFrame']*4+['E19_RearBase']+[n for n in cur.members if n.startswith('I19_FuseBand_')]; solid=[BRepAlgoAPI_Common(now.shape(names[i]),v).Shape() for i,v in enumerate(solid)]\n for i,n,h,t in pairs:")
s=s.replace('three added lower walls only','changed lower material only; fixed neck guard starts at Z100.2, above leg max96.62').replace("P/'side-clearance.json'","P/'leg-delta.json'")
exec(s)
