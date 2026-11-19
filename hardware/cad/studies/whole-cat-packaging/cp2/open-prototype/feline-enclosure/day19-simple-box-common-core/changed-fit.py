"""Delta tests of rigid assemblies, stock ports and the moving tail. Saved native only."""
from pathlib import Path
import runpy,json,math,hashlib,sys
import numpy as np
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Trsf,gp_Ax1,gp_Pnt,gp_Dir
P=Path(__file__).parent; file=P/'whole-cat19E.FCStd';S=runpy.run_path(str(P.parent/'day18-front-insert-correction/saved-front.py'))['Saved'](file)
result=dict(source_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),physical_PASS=False,static=[],swing=[])
def save():(P/('changed-fit'+('' if len(sys.argv)<2 else '-'+sys.argv[1])+'.json')).write_text(json.dumps(result,indent=1)+'\n')
for a,others in [('D19D_YawMatedPair',['E19_ForeBase','Pi4B_actual_PCB','CF17_POWER_DELOCK60047_APPROX_FULL','E19_FrontShroud','Motor_ATO4A__1_3','BR_FLANK_HP_PAIR']),('S0_body',['E19_RearBase','PBAY_P_SYS','E1_populated_prototype_board','MG92B_Tail']),('S0_key',['E19_RearBase','E19_RearLid']),('S0_ring_IN_0_0',['E1_populated_prototype_board','PBAY_F_PI','E19_RearBase']),('OP_S1_PRIMARY_STEM',['E19_RearBase']),('E19_BUS_PCB',['E19_RearLid','Speaker','BNO085','E19_RearBase','PCA9685_Adafruit815_PCB']),('D18C_DATA_BUS_FULL26_PROJECT_BOOT',['PCA9685_Adafruit815_PCB','E19_RearLid','S0_body','E19_RearBase']),('E19_FrontShroud',['E19_ForeBase','E19_ForeLid']),('E19_RearBase',['E19_RearLid'])]:
    for b in others:result['static'].append(dict(a=a,b=b,**S.common(a,b)))
    save()
for a,axis,angles,ns in [('E19_UpperYawCover',(-130,0,0,0,0,1),[-20,0,20],['E19_ForeBase','E19_FrontShroud']),('E19_KeyedTail',(140,0,130,0,1,0),[-15,0,15],['E19_RearBase','E19_RearLid','S0_body','B19_TailMatedPair','TAIL_FIXED_OUTER_RACE_CAP','WAVEGO_complete_126_source_solids'])]:
    for angle in angles:
        t=gp_Trsf();t.SetRotation(gp_Ax1(gp_Pnt(*axis[:3]),gp_Dir(*axis[3:])),math.radians(angle));s=BRepBuilderAPI_Transform(S.shape(a),t,False).Shape()
        for b in ns:
            if b.startswith('WAVEGO'): # lower bound throughout ±15 for all tail points
                low=130+(123-130)-max(abs(S.bounds(a)[[0,3]]-140))*math.sin(math.radians(15))
                result['swing'].append(dict(part=a,angle=angle,other=b,all_range_Z_gap_lower_mm=low-S.bounds(b)[5]));continue
            op=BRepAlgoAPI_Common(s,S.shape(b));assert op.IsDone()
            g=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),g)
            result['swing'].append(dict(part=a,angle=angle,other=b,common_mm3=g.Mass()))
        save()
print([(q.get('a',q.get('part')),q.get('b',q.get('other')),q['common_mm3']) for q in result['static']+result['swing'] if q.get('common_mm3',0)>.02])
