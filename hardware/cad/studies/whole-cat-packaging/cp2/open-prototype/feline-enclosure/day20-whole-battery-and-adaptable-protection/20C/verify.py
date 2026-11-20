"""Check the affected 20C interfaces with the installed FreeCAD kernel."""
from pathlib import Path
import json
import os
from runpy import run_path

import FreeCAD as App

here=Path(__file__).resolve().parent
g=run_path(str(here/'geometry.py'))
l=run_path(str(here/'layout.py'))
box,bbox,ov=[g[k] for k in ('box','bbox','overlap')]
source=here.parent/'whole-cat20A.FCStd'
prior=json.loads((here.parent/'20B-dlugosci.json').read_bytes())
d=App.openDocument(str(source))
assert not d.isTouched() and len(d.Objects)==551
q=g['collect'](d)
front,f0,f0_socket,f0_mm3=l['f0_prints'](d,g)
post=l['post_print'](d,g)
wires=l['wire_budgets'](prior)
def rows(shape, names):
    rec={}
    for n in names:
        o=d.getObject(n)
        if not o:continue
        v=ov(shape,o.Shape)
        if v>.05:
            rec[n]=round(v,4)
    return rec
def record(s):
    return {"bounds":bbox(s),"solids":len(s.Solids),"valid":s.isValid(),"volume":round(s.Volume,3)}
keep=['E19_BatteryDoor','Battery_GEA223S30X6GT','NIGHT_INLINE_RR_W052','NIGHT_INLINE_RR_W053',
      'Motor_ATO4A_1_2','Motor_ATO4A_1_5','E19_WagoRearPos','E19_ForeLid','E19_RearLid']
structure=['H19_FrontFrame','E19_RearBase','E19_ForeLid','E19_RearLid','Pi_components_and_cooling',
           'BNO085','PCA9685_Adafruit815_PCB','D19_JR300_PITCH_RESERVE','H19_MainTrunk',
           'D19_JR300_YAW_RESERVE','PBAY_P_AUX','WAGO615_power_0_0','Speaker','E19_ReSpeakerSource',
           'AUX_Pololu4092','E19_WagoForeNeg','E19_WagoRearNeg','D19_SIDE_BUNDLE_NEG','D19_SIDE_BUNDLE_POS',
           'Motor_ATO4A__1_1','Motor_ATO4A__1_4','Motor_ATO4A__1_5','S0_body','E19_UpperYawCover','G19_Group_JRP']
summary={
 "root_contact":{"door":q['seats'],"XT60_dock_common_mm3":q['dock_root_common_mm3'],"F0_socket_common_mm3":f0_mm3},
 "changed_prints":{n:record(s) for n,s in [('RearBase',q['rear']),('DoorBridge',q['bridge']),
                                       ('FrontFrame',front),('F0_mount',f0),('POST_mount',post)]},
 "bridge_vs_door_and_neighbors":rows(q['bridge'],keep),
 "bridge_fixed_base_overlap":round(ov(q['bridge'],q['rear']),4),
 "f0_mount_neighbor_overlap":rows(f0,structure),
 "post_mount_neighbor_overlap":rows(post,structure),
 "XT60_dock_neighbor_overlap":rows(q['dock'],[n for n in structure if n!='E19_RearBase']),
 "wires":wires
}
print("structure",json.dumps({k:v for k,v in summary.items() if k!='wires'}),flush=True)
print("wire budget", {k:(v.get('project_total_mm',v.get('project_blank_mm',v.get('modeled_choices_mm_including_11_end')))) for k,v in wires.items() if isinstance(v,dict)},flush=True)
for p,v in wires['battery_factory'].items():
 print("battery",p,v['min_exit_to_boot_incl_dressing_mm'],v['transfer_inner_R_mm'],flush=True)
for k,(s,n,z,bc,sa) in q['mta'].items():
 summary["changed_prints"][k]={**record(s),"root_member":n,"seat_z":z,"root_native_bounds":bc,"sample_bounds":sa,
            "mount_overlaps":rows(s,structure),"sample_overlaps":rows(box(*sa),structure)}
 print(k,summary["changed_prints"][k],flush=True)
open_regions={
 "pack_body_both_directions":[-12,20,52,94.5,142,73.5],
 "stationary_XT60_M":l["ACTIVE_M"],
 "pack_F_14mm_positive_Y":[14.25,43,132.25,36.25,82,148.75],
 "full_unmated_F_boot_wall_throat":[72,96,80,94,144,98],
 "two_jacket_exit_wall_throat":[82,94,73.5,92,108,83],
 "two_factory_leads_parked_U":[22.85,58,134.6,60.65,94.4,147.4],
 "two_factory_leads_open_U":[22.85,58,134.6,60.65,101.4,147.4],
 "whole_F0_assumed_21p5":l['FUSE_FULL'],
 "full_W076_output_strip":[7,-88.4,138.85,84,-73.5,149.4],
 "POST_max_and_min_adjustment":[58,-89.25,142.,104,-76.25,152.],
}
summary["gate"]={}
allgate=structure+['Motor_ATO4A_1_2','Motor_ATO4A_1_5']
for label,b in open_regions.items():
    s=box(*b)
    names=[n for n in allgate if n not in ('E19_RearBase','H19_FrontFrame')]
    if 'throat' in label or 'both_directions' in label or 'open' in label or '14mm' in label:
        names=[n for n in names if n not in ('E19_ForeLid','E19_RearLid','Speaker','E19_ReSpeakerSource')]
    collisions=rows(s,names)
    for det,m in [('20C_RearBase',q['rear']),('20C_FrontFrame',front),('20C_FuseStand',f0),('20C_POST_mount',post)]:
        value=ov(s,m)
        if value>.05:collisions[det]=round(value,4)
    summary["gate"][label]={"bounds":b,"common_mm3":collisions}
    print(label,collisions,flush=True)
# Named local check: the jacket cannot be qualified by the common
# upper lay envelope at the AUX and BNO PCB corners.
from FreeCAD import Vector
import Part
summary['named_pack_corners']={}
for pole,data in wires['battery_factory'].items():
    pts=data['states']['seated']['points']
    pcbs={}
    for region,item,z0,z1 in [('AUX_PCB','AUX_Pololu4092',86,96),('BNO','BNO085',103,115)]:
        target=d.getObject(item).Shape
        results=[Part.Vertex(Vector(*p)).distToShape(target)[0]-2.4 for p in pts if z0<=p[2]<=z1]
        pcbs[region]=round(min(results),3)
    summary['named_pack_corners'][pole]=pcbs
print('PCB exits',summary['named_pack_corners'],flush=True)
def atomic(name,obj):
    f=here/name
    t=f.with_suffix('.tmp')
    with t.open('x',encoding='utf-8',newline='\n') as fp:
        json.dump(obj,fp,indent=2,ensure_ascii=False);fp.write('\n')
    os.replace(t,f)
atomic('20C-dry-gate.json',summary)
App.closeDocument(d.Name)