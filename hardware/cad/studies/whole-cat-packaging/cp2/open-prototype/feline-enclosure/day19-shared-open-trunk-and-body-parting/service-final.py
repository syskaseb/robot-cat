from common import *
s=(P/'service-space.py').read_text();exec(s[:s.index('bay=[')])
m=list(dict.fromkeys(m+['E19_KeyedTail','G19_MIC_C_PlugAllow','B19_TailMatedPair']))
rows={}
for name,b,ig in [('XT60_joined',[8,-39,102,32,-21,152],['XT60H_mated_with_boots']),('battery_half_pull14',[8,-39,127,32,-21,166],['XT60H_mated_with_boots']),('fingers_from_split',[8,-39,152,32,-21,174],['XT60H_mated_with_boots']),('five_D_FL_mouths',[124,-93,115.4,150,-79,122.2],[]),('isolated_cell_withdrawal',[-12,20,52,94.5,140,73.5],['E19_BatteryDoor','Battery_GEA223S30X6GT','NIGHT_INLINE_RR_W052','NIGHT_INLINE_RR_W053'])]:
 rows[name]=dict(field=b,hits=screen(b,ig))
wr('service-final.json',rows);print({k:[v['n'] for v in q['hits']] for k,q in rows.items()})
