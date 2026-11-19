"""Read the actual displayed hardware and its positions from the received file."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json,runpy
P=Path(__file__).parent
D=P.parent/'day19-whole-appearance-and-moving-neck-correction'
S=runpy.run_path(str(P.parent/'day18-front-insert-correction/saved-front.py'))['Saved'](D/'whole-cat19D.FCStd')
g=ET.fromstring(S.zip.read('GuiDocument.xml'))
rows={}
for o in g.findall('.//ViewProvider'):
    n=o.get('name')
    v=o.find('./Properties/Property[@name="Visibility"]/Bool')
    if n in S.members and v is not None and (v.get('value')=='true' or n.startswith(('TAIL','B19','D19D'))):
        rows[n]=dict(shown=v.get('value')=='true',bounds=S.bounds(n).round(3).tolist())
(P/'source-layout.json').write_text(json.dumps(rows,indent=1)+'\n')
for n,v in rows.items():
    if v['shown'] and not n.startswith(('H01','YAW_','PITCH_','CAM_','TOF_','CB_','CF17','F3_','HB_','Motor_ATO','WAGO','S0_RING','NIGHT_','D19D_Ear','D19D_Iris','D19D_Pupil')): print(n,v['bounds'])
