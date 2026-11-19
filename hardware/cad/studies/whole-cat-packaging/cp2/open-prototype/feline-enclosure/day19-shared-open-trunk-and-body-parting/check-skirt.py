from common import *
s=(G/'side-clearance.py').read_text();s=s.replace("if pairs:\n","if pairs:\n target=Saved(native).shape('H19_FrontFrame')\n");s=s.replace("for i,n,h,t in pairs:","solid=[BRepAlgoAPI_Common(a,target).Shape() for a in solid]\n for i,n,h,t in pairs:")
exec(s.replace("P/'side-clearance.json'","P/'leg-delta.json'"))
