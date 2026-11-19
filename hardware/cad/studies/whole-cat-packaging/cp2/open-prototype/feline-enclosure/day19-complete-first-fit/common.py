from pathlib import Path
import json,hashlib,math,sys,runpy,numpy as np
P=Path(__file__).parent;O=P.parent;H19=O/'day19-shared-open-trunk-and-body-parting';G=O/'day19-real-terminations-and-assembly';F=O/'day19-connected-servo-usb-and-closure';E=O/'day19-simple-box-common-core'
R=next(p for p in P.parents if (p/'.git').exists());H=R/'hardware';native=P/'whole-cat19I.FCStd'
def rd(p):return json.loads(Path(p).read_bytes())
def wr(n,q):(P/n).write_bytes((json.dumps(q,ensure_ascii=False,indent=1)+'\n').encode())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
Saved=runpy.run_path(str(O/'day18-front-insert-correction/saved-front.py'))['Saved']
