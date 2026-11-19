from common import *
d=Saved(native);rows=[]
tests={'H19_FrontFrame':['E19_ForeLid','F19_ForeCap','E19_RearBase','D19D_YawMatedPair','BR_FLANK_HP_PAIR','MG92B_Head_yaw','YAW_SHAFT_FORK_POSITIVE_CROSSPIN_full_screw','B19_ToolEightAnchors'],'E19_ReSpeakerSource':['E19_ForeLid'],'H19_DATA_A_Boot':['G19_PiAudioBoot','E19_ForeLid','H19_FrontFrame'],'E19_ForeLid':['F19_ForeCap'],'E19_RearLid':['F19_RearCap']}
for a,ns in tests.items():
 for b in ns:
    if b in d.members:rows.append(dict(a=a,b=b,**d.common(a,b)))
wr('static-stations.json',dict(native=sha(native),rows=rows,physical_PASS=False));print([r for r in rows if r.get('common_mm3',0)>.00002])
