from pathlib import Path
import json,runpy,hashlib,sys
P=Path(__file__).parent;native=P/'whole-cat19G.FCStd'
S=runpy.run_path(str(P.parent/'day18-front-insert-correction/saved-front.py'))['Saved'](native)
rows=[]
groups=[('G19_PermaProto1608',['E19_RearBase','E19_RearLid','S0_body','S0_stud_IN_0_0','S0_stud_OUT_0_0','Speaker','MG92B_Tail','E19_KeyedTail','PCA9685_Adafruit815_PCB']),('G19_E1_population_limits',['E19_RearBase','E19_RearLid','S0_body','MG92B_Tail','E19_KeyedTail','Speaker']),('G19_U1_adapter_region',['E19_RearBase','E19_RearLid','S0_body','MG92B_Tail','E19_KeyedTail'])]
groups+=[(a,[b for b in ['E19_RearLid','F19_RearCap','E19_ForeLid','F19_ForeCap','E19_FrontShroud','E19_UpperYawCover','G19_PermaProto1608','E19_RearBase','E19_KeyedTail'] if b!=a and b in S.members]) for a in ['G19_H3_mate_allowance','G19_JRStation','G19_NeckOverlap'] if a in S.members]
groups.extend([('E19_ReSpeakerSource',['E19_ForeLid','E19_ForeBase','TTP223_touch','Speaker','E19_BUS_PCB','E19_RearLid']),('G19_MIC_C_PlugAllow',['E19_ForeLid','E19_RearLid','E19_RearBase','Speaker','E19_BUS_PCB']),('G19_PiAudioBoot',['Pi_USB_DATA_Delock_mating']),('E19_FrontShroud',['E19_ForeBase','E19_ForeLid','F19_ForeCap']),('F19_RearCap',['E19_RearLid']),('F19_ForeCap',['E19_ForeLid'])])
for k,host,pair in [('yaw','E19_ForeLid','D19D_YawMatedPair'),('tail','E19_RearLid','B19_TailMatedPair'),('pitch','E19_UpperYawCover','BR_FLANK_HP_PAIR')]:groups.append(('G19_RemoteR_'+k,[host,pair]))
for a,ns in groups:
 for b in ns:
    if b in S.members:rows.append(dict(a=a,b=b,**S.common(a,b)))
out=dict(native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),rows=rows,classification='supplier board = material; component max/adapter/plug fields = design allocation; positive common rejects that assignment',physical_PASS=False)
(P/(sys.argv[1]+'-stations.json')).write_bytes((json.dumps(out,indent=1)+'\n').encode())
print([r for r in rows if r.get('common_mm3',0)>.001])
