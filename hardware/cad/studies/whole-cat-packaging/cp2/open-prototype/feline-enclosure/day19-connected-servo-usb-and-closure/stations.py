from pathlib import Path
import runpy,hashlib,json
P=Path(__file__).parent;native=P/'whole-cat19F.FCStd'
S=runpy.run_path(str(P.parent/'day18-front-insert-correction/saved-front.py'))['Saved'](native)
rows=[]
for a,bs in [('E19_BUS_PCB',['F19_RearCap','E19_RearLid','E19_KeyedTail']),('D18C_DATA_BUS_FULL26_PROJECT_BOOT',['F19_RearCap','E19_RearLid','E19_KeyedTail']),('TTP223_touch',['F19_ForeCap','E19_ForeLid','D19D_YawMatedPair']),('Speaker',['E19_RearLid','E19_RearBase','E19_ReSpeakerSource','S0_body','OP_MONITOR_PRIMARY_CASE_CONSERVATIVE']),('B19_TailMatedPair',['E19_RearLid','F19_RearCap','E19_KeyedTail']),('D19D_YawMatedPair',['E19_ForeLid','F19_ForeCap','E19_FrontShroud']),('BR_FLANK_HP_PAIR',['E19_UpperYawCover','E19_FrontShroud','D19D_PitchBack']),('E19_ForeLid',['F19_ForeCap']),('E19_RearLid',['F19_RearCap'])]:
    for b in bs:
        if b in S.members:rows.append(dict(a=a,b=b,**S.common(a,b)))
    (P/'stations.json').write_bytes((json.dumps(dict(native=hashlib.sha256(native.read_bytes()).hexdigest(),rows=rows),indent=1)+'\n').encode())
print([r for r in rows if r.get('common_mm3',0)>.001])
