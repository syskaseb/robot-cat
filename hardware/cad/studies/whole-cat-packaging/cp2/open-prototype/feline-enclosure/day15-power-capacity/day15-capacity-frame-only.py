from pathlib import Path
import json
p=Path('C:/Users/Sysq/AppData/Local/Temp/day15-capacity-missing.py');code=p.read_text(encoding='utf-8');a=code.index(' fields=[D.getObject(');b=code.index(" r['power_complete']=True;save()",a)
code=code[:a]+" fields=[]\n"+code[b:];code=code.replace("r['power_complete']=True","r['power_complete']=False; r['independent_frame_check']=True; r['power_open']='F0_short_input vs P10 common180; frozen, not resumed'")
code=code.replace("(P/'missing-result.json')","(P/'missing-frame-result.json')").replace("'RECEIVED_POWER_AND_MISSING_ADDED_MATERIAL_AUDIO_CLEAR_SCOPED'","'MISSING_ADDED_MATERIAL_AUDIO_CLEAR_SCOPED_POWER_F0_OPEN'")
exec(compile(code,'day15-capacity-frame-only-inner.py','exec'))
