"""Reopen delivered exports and verify that the retained bearings stay pinned."""
from pathlib import Path
from runpy import run_path
from zipfile import ZipFile
from xml.etree import ElementTree
import hashlib
import json, os

import numpy as np
import trimesh
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_ReturnStatus
from OCP.STEPControl import STEPControl_Reader

d=Path(__file__).resolve().parent
source=d.parent/'20C'/'whole-cat20C.FCStd'
native=d/'whole-cat20D.FCStd'
S=run_path(str(d.parent.parent/'day18-front-insert-correction'/'saved-front.py'))['Saved']
a,b=S(source),S(native)
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

pin='92fc832c49983ce98cd8d0c7b182f126481d2aff89de36a9c76ee67842985059'
assert sha(source)==pin
def measure(s):
    props=GProp_GProps();BRepGProp.VolumeProperties_s(s,props,1e-8)
    return float(props.Mass())

index=json.loads((d/'20D-print-index.json').read_bytes())
support=json.loads((d/'20D-support-fit.json').read_bytes())
quality={}
for key,data in index.items():
    s=b.shape(key)
    assert np.allclose(b.bounds(key),support['forms'][key]['bounds_mm'],atol=1e-3)
    ex=d/'parts'
    reader=STEPControl_Reader()
    stp=ex/(key+'.step')
    assert sha(stp)==data['STEP_sha256']
    assert reader.ReadFile(str(stp))==IFSelect_ReturnStatus.IFSelect_RetDone
    assert reader.TransferRoots()>0
    t=reader.OneShape()
    actual,independent=measure(s),measure(t)
    common=BRepAlgoAPI_Common(s,t)
    assert common.IsDone()
    delta=abs(actual+independent-2*measure(common.Shape()))
    assert delta<0.01,(key,actual,independent,delta)
    stl=ex/(key+'.stl')
    assert sha(stl)==data['STL_sha256']
    mesh=trimesh.load(stl,force='mesh')
    assert mesh.is_watertight and mesh.is_winding_consistent and len(mesh.split())==1,(key,mesh)
    assert np.allclose(mesh.bounds[0],[0,0,0],atol=.002)
    assert np.allclose(mesh.extents,data['bed_axes_mm'],atol=.02)
    assert abs(mesh.volume-actual)/actual<.01,(key,mesh.volume,actual)
    quality[key]={'step_difference_mm3':round(delta,7),'stl_watertight':True,
                  'stl_components':1,'stl_volume_mm3':round(mesh.volume,3),'native_volume_mm3':round(actual,3)}

keep=['H19_FrontFrame','E19_RearBase','E19_BatteryDoor','C20_BatteryUpperBridge','C20_MTA_FL',
      'C20_MTA_FR','C20_MTA_RL','C20_MTA_RR','Battery_GEA223S30X6GT','B19_ToolEightAnchors',
      'S0_body','Pi4B_actual_PCB']
preserved={}
for n in keep:
    first=a.zip.read(a.members[n]); second=b.zip.read(b.members[n])
    assert first==second,(n,'serialization changed')
    preserved[n]=hashlib.sha256(first).hexdigest()

receipt=json.loads((d/'20D-native-readback.json').read_bytes())
assert receipt['sha256']==sha(native) and receipt['state']=='IDLE' and receipt['pending_operation'] is None
assert receipt['modified'] is False and receipt['touched'] is False
print(quality,flush=True)
data={'verified_source_sha256':pin,'verified_native_sha256':sha(native),'source_BRep_identity':preserved,
      'reopened_changed_prints':quality,'physicalPASS':False,'actualfit':None,'cut':None,'slack':None}
out=d/'20D-export-verification.json';tmp=out.with_suffix('.tmp')
prior=out.read_bytes() if out.exists() else None
with tmp.open('x',encoding='utf-8',newline='\n') as f:
    json.dump(data,f,indent=2,ensure_ascii=False);f.write('\n')
assert (out.read_bytes() if out.exists() else None)==prior
os.replace(tmp,out)
