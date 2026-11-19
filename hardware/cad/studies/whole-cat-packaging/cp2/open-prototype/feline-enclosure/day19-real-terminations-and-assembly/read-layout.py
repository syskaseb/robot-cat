"""Read installed geometries, world frames and source terminal contracts without moving parts."""
from pathlib import Path
import json,zipfile,runpy,hashlib
from xml.etree import ElementTree as XML
import numpy as np
P=Path(__file__).parent;F=P.parent/'day19-connected-servo-usb-and-closure';E=P.parent/'day19-simple-box-common-core';H=next(q for q in P.parents if (q/'electronics/kicad-current/design.json').exists());A=H/'electronics/full-cat';ADD=A/'closed-prototype-add7-2026-11-16'
def read(p):return json.loads(p.read_bytes())
def wr(name,q):(P/name).write_bytes((json.dumps(q,ensure_ascii=False,indent=1)+'\n').encode())
def bbox(a):return np.asarray(a,dtype=float)
def xyz(p):return np.round(p,5).tolist()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
S=runpy.run_path(str(P.parent/'day18-front-insert-correction/saved-front.py'))['Saved'](P/'whole-cat19G.FCStd')
tree=XML.fromstring(S.zip.read('Document.xml'));obj={o.get('name'):o for o in tree.findall('./ObjectData/Object')}
names={}
for n,o in obj.items():
    if n not in S.members:continue
    if n.startswith(('PBAY','WAGO','Motor_ATO','NIGHT_','CF17_POWER','CF17_PI_PRIMARY','OP_S1','S0_','E19_ReSpeaker','XT60','CF17_POL','Pi_USB','BR_FLANK_HP','D19D_YawMated','B19_TailMated','F0_FH','E1_','PCA968','F3_MAIN','CB_PCA','CB_E1','MAIN_','BNO085','AUX_Pol','MAX983','TTP223','Speaker','Monitor','F19_ForeCap','E19_BUS_PCB','E19_KeyedTail')):
        prop=o.find("./Properties/Property[@name='Label']/String")
        names[n]=dict(label=prop.get('value') if prop is not None else n,bounds=xyz(S.bounds(n)))
wr('installed-stations.json',names)
