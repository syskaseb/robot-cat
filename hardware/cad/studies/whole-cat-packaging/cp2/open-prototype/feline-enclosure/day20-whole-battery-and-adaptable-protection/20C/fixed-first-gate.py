from pathlib import Path
from runpy import run_path
import json,numpy as np
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Pnt
p=Path(__file__).resolve().parents[1]
D=run_path(str(p.parent/'day18-front-insert-correction'/'saved-front.py'))['Saved'](p/'whole-cat20A.FCStd')
named=['H19_FrontFrame','E19_RearBase','E19_RearLid','E19_ForeLid','E19_WagoForeNeg','E19_WagoRearPos','E19_WagoForePos','E19_WagoRearNeg','BNO085','Pi_components_and_cooling','AUX_Pololu4092','MAIN_Pololu4853','PCA9685_Adafruit815_PCB','Speaker','E19_ReSpeakerSource','G19_PiAudioBoot','MAX98357A_amp','D19_BODY_CONTROL_TRUNK','D19_JR300_PITCH_RESERVE','D19_JR300_YAW_RESERVE','PBAY_P_AUX','WAGO615_power_0_0','H19_MainTrunk','H19_PowerBranch','Motor_ATO4A_1_1','Motor_ATO4A_1_2','Motor_ATO4A_1_4','Motor_ATO4A_1_5','E19_FieldAxialFuse','G19_Group_I2S','G19_Group_POWER','D19_SIDE_BUNDLE_NEG','D19_SIDE_BUNDLE_POS']
rows={
'XT60_assembled':[12.75,18,132.25,34.75,68,150.25],
'pack_F_unmate_14y':[12.75,43,132.25,34.75,82,150.25],
'F0_21p5_assumed':[-.75,-59,130.5,16.75,-8,152],
'F0_open_lid':[-2,-58,152,20,-22,179],
'W075_transition':[5,-8,136,24,18,147],
'POST_fixed':[-.5,-91,136,12.5,-71,146],
'factory_out_storage':[-10,-89,147,17,-58,174],
'grip_window':[8,30,151.5,42,86,173],
'pack_cross_AUX_then_open_bank':[37,20,122,74,53,149.1],
'pack_turn_closed':[19,51,130,35,91,148.9],
'pack_turn_open':[19,53,130,35,100,155],
}
result={}
for label,b in rows.items():
 s=BRepPrimAPI_MakeBox(gp_Pnt(*b[:3]),gp_Pnt(*b[3:])).Shape()
 hits=[]
 for n in named:
  a=D.bounds(n)
  if np.any(np.minimum(b[3:],a[3:])-np.maximum(b[:3],a[:3])<1.e-5):continue
  op=BRepAlgoAPI_Common(s,D.shape(n))
  if not op.IsDone():hits.append([n,None,None]);continue
  props=GProp_GProps(); r=op.Shape(); BRepGProp.VolumeProperties_s(r,props)
  if props.Mass()>.1:
   bb=Bnd_Box();BRepBndLib.AddOptimal_s(r,bb,False,False)
   hits.append([n,round(props.Mass(),3),[round(v,2) for v in (*bb.CornerMin().Coord(),*bb.CornerMax().Coord())]])
 print(label,hits,flush=True)
 result[label]={'bounds':b,'hits':hits,'lids_removed':label in {'pack_F_unmate_14y','F0_open_lid','grip_window','pack_turn_open'}}
target=p/'20C'/'20C-fixed-first-gate.json'
tmp=target.with_suffix('.tmp')
with tmp.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
tmp.rename(target)