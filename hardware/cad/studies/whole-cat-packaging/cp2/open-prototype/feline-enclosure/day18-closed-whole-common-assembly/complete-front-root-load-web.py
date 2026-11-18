import FreeCAD as A,Part,json
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector
rows=[]
for tag,side in [('NEG',-1),('POS',1)]:
 o=D.getObject('F3_BODY_FORE_'+tag);old=o.Shape.copy()
 # Actual upper wall starts outside the first low crossarm: one useful vertical side web spans the complete load gap.
 web=Part.makeBox(10,6,19,V(-75,87.5 if side>0 else -93.5,55))
 o.Shape=old.fuse(web).removeSplitter();rows.append({'name':o.Name,'valid':o.Shape.isValid(),'solids':len(o.Shape.Solids),'retained_missing':old.cut(o.Shape).Volume,'new_web_missing':web.cut(o.Shape).Volume,'web_volume':web.Volume,'function':'source removable lower bearing receiver -> existing outboard column/crossarm -> real vertical side web -> cowl wall; no leg/frame motion assumption inherited'})
(P/'front-load-web-completion.json').write_bytes((json.dumps(rows,indent=2)+'\n').encode());D.recompute();D.save();print('FRONT_REAL_LOAD_WEB',rows)
