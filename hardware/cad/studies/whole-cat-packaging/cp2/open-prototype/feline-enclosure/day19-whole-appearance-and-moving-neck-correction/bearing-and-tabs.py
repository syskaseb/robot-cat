"""Carry eight anchor seats and full yaw steel forward; test material around the common tie slot."""
from pathlib import Path
import json,hashlib
P=Path(__file__).parent
src=(P.parent/"day19-common-floor-and-bundle-assembly/anchor-seats.py").read_text().replace("whole-cat19B.FCStd","whole-cat19D.FCStd").replace("B19_FrontFloor","D19D_FrontFloor")
exec(src[:src.index('(P/"anchor-seats.json")')])
tabs=[]
for x,y in [(-117.6,61.4),(-111.2,66.0),(-117.6,65.4),(-113.4,63.7)]:
    tabs.append(dict(x=x,y=y,rail_material=D.inside("D19D_YawSaddle",[[x,y,131.7]]) is not None,tab_material=D.inside("D19D_YawHood",[[x,y,134.5]]) is not None))
out=dict(pads=rows,yaw_full_steel=steel,tabs=tabs,native_sha256=hashlib.sha256((P/"whole-cat19D.FCStd").read_bytes()).hexdigest(),physical_PASS=False)
(P/"bearing-and-tabs.json").write_bytes((json.dumps(out,indent=1)+"\n").encode());print([r["contact_patch_mm2"] for r in rows],tabs)

