"""Try an actual rigid holder lift with the upper decks removed; test the cap zone separately."""
from common import *
s=(P/'service-space.py').read_text();exec(s[:s.index('bay=[')])
from OCP.gp import gp_Trsf,gp_Vec
from OCP.TopLoc import TopLoc_Location
m=['H19_FrontFrame','E19_RearBase','Pi4B_actual_PCB','Battery_GEA223S30X6GT','F0_FHAC0002_30A','AUX_Pololu4092','MAIN_Pololu4853','PBAY_P_SYS','PBAY_P_REAR','XT60H_mated_with_boots']
out={}
for k in ['F_HY','F_HP','F_TY','F_PI','F_AUX']:
 n='PBAY_'+k;b=d.bounds(n);lo=b[:3].copy();lo[2]=b[5];hi=b[3:].copy();hi[2]+=21.45;h=screen([*lo,*hi],[])
 # The exact bought holder/installed nominal solid may be raised along its original vertical open seat.
 seated=[dict(neighbour=a,**d.common(n,a)) for a in m if a!=n and a in d.members]
 out[k]=dict(seated=seated,incremental_lift=h,procedure='isolated rare service: remove upper decks, remove the overlying Pi if present, release the open bank and labelled cage leads before extracting the holder; leave soldered PCA/E1 whole',actual_cap_profile_and_dress=None)
wr('five-fuse-service.json',out);print([(k,[(r['neighbour'],r['common_mm3']) for r in v['seated'] if r.get('common_mm3',0)>.001]) for k,v in out.items()])
