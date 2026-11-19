from pathlib import Path
import json,hashlib,runpy,sys,math,numpy as np
P=Path(__file__).parent;O=P.parent
G=O/'day19-real-terminations-and-assembly';F=O/'day19-connected-servo-usb-and-closure';E=O/'day19-simple-box-common-core'
R=next(p for p in P.parents if (p/'.git').exists());H=R/'hardware'
def rd(n):return json.loads(Path(n).read_bytes())
def wr(n,q):(P/n).write_bytes((json.dumps(q,indent=1,ensure_ascii=False)+'\n').encode())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
Saved=runpy.run_path(str(O/'day18-front-insert-correction/saved-front.py'))['Saved']
native=P/'whole-cat19H.FCStd'
