"""Measure named 20D support interfaces on the frozen source, without opening a GUI."""
from pathlib import Path
from runpy import run_path
from zipfile import ZipFile
from xml.etree import ElementTree
import hashlib
import json
import os

import FreeCAD as App
import Part

folder=Path(__file__).resolve().parent
g=run_path(str(folder/'geometry.py')); l=run_path(str(folder/'layout.py'))
b,l_bounds,vol=[g[n] for n in ('cube','bounds','volume')]
forms=g['forms']()
p=folder.parent/'20C'/'whole-cat20C.FCStd'
sha=hashlib.sha256(p.read_bytes()).hexdigest()
assert sha=='92fc832c49983ce98cd8d0c7b182f126481d2aff89de36a9c76ee67842985059'
with ZipFile(p) as z:
    xml=ElementTree.fromstring(z.read('Document.xml'))
    members={x.get('name'):x.find('./Properties/Property[@name="Shape"]/Part') for x in xml.findall('./ObjectData/Object')}
    references={}
    def source(n):
        if n not in references:
            shape=Part.Shape();shape.importBrepFromString(z.read(members[n].get('file')).decode('ascii'))
            references[n]=shape
        return references[n]
    bounds={}
    collisions={}
    targets={'D20_XT60_Axial_Adapter':['E19_RearBase','H19_FrontFrame','E19_RearLid','E19_ForeLid','BNO085','G19_Group_JRP'],
             'D20_F0_Open_Adapter':['H19_FrontFrame','E19_ForeLid','E19_RearLid','PCA9685_Adafruit815_PCB','E19_WagoForePos','Motor_ATO4A_1_0','BNO085','Pi_components_and_cooling'],
             'D20_POST_Aft_Slotted':['H19_FrontFrame','E19_ForeLid','Pi4B_actual_PCB','Pi_components_and_cooling','D19_SIDE_BUNDLE_NEG','E19_UpperYawCover','D19D_YawSaddle','D19D_PitchBack'],
             'D20_POST_Clamp_M3x12':['H19_FrontFrame','Pi4B_actual_PCB','Pi_components_and_cooling'],
             'D20_POST_Clamp_Nut':['H19_FrontFrame','Pi4B_actual_PCB','Pi_components_and_cooling']}
    physicals={'D20_XT60_Axial_Adapter':{'XT60':l['BOX_M'],'plug_sweep':l['BOX_SWEEP']},
               'D20_F0_Open_Adapter':{'F0':l['F0'],'cap_open':l['F0_OPEN']},
               'D20_POST_Aft_Slotted':{'POST_sweep':l['POST_SWEEP'],'lever_access':l['POST_ACCESS']}}
    for n,s in forms.items():
        assert len(s.Solids)==1 and s.isValid(),(n,len(s.Solids),s.isValid(),l_bounds(s))
        bounds[n]={'bounds_mm':l_bounds(s),'volume_mm3':round(s.Volume,3)}
        local={q:source(q) for q in targets[n]}
        local.update({k:b(v) for k,v in physicals.get(n,{}).items()})
        collisions[n]={}
        for k,q in local.items():
            v=vol(s,q)
            if v>.04:collisions[n][k]=[round(v,4),l_bounds(s.common(q))]
        print(n,bounds[n],collisions[n],flush=True)
    f=source('H19_FrontFrame');r=source('E19_RearBase')
    xt=forms['D20_XT60_Axial_Adapter']; f0=forms['D20_F0_Open_Adapter']; post=forms['D20_POST_Aft_Slotted']
    def bearing(s,ref,bb,axis):
        q=s.common(b(bb));q.translate(App.Vector(*axis));return round(vol(q,ref)/.03,2)
    faces={
        'XT60_primary_source_pad_mm2':bearing(xt,r,[14.23,27.86,132.25,22,41.3,132.28],[0,0,-.03]),
        'XT60_right_key_source_pad_mm2':bearing(xt,r,[35.85,28,135.55,37.14,39.9,135.58],[0,0,-.03]),
        'F0_rib_top_mm2':bearing(f0,f,[-62,41.8,135.1,-52,49.85,135.13],[0,0,-.03]),
        'POST_frame_top_mm2':bearing(post,f,[-117,-31,107.5,-109,-26.5,107.53],[0,0,-.03]),
    }
    attach={
      'F0_source_through_slot_tail_free_mm3':round(vol(f,b([-58.58,43.2,129.6,-55.42,45.16,137.7])),5),
      'XT60_band_under_receiver_free_mm3':round(vol(r,b([19.35,25,127.4,22.45,43.6,129.10])),5),
      'POST_bolt_and_rail_overlap_mm3':round(vol(post,forms['D20_POST_Clamp_M3x12']),5),
      'POST_nut_and_rail_overlap_mm3':round(vol(post,forms['D20_POST_Clamp_Nut']),5),
    }
    print('bearing',faces,'attachment',attach,flush=True)
data={'frozen_source_sha256':sha,'forms':bounds,'positive_volume_overlap':collisions,'bearing':faces,
      'attachment_regions':attach,'actualfit':None,'cut':None,'slack':None,'physicalPASS':False}
out=folder/'20D-support-fit.json';tmp=out.with_suffix('.tmp')
before=out.read_bytes() if out.exists() else None
with tmp.open('x',encoding='utf-8',newline='\n') as f:
    json.dump(data,f,indent=2,ensure_ascii=False);f.write('\n')
assert (out.read_bytes() if out.exists() else None)==before
os.replace(tmp,out)
