"""Receive W2 native: use a dimensioned L-key, not a fictitious50mm rod."""
import time,json
from pathlib import Path
import build_current_head_anchor as B
H=B.H;A,Part,P,ROOT,BASE,OUT=H.A,H.Part,H.P,H.ROOT,H.BASE,H.OUT

def physical_scene(reader):
 targets,torso=H.scene(reader)
 # Intermediate PartDesign features are not additional physical neck parts.
 for n in list(targets):
  if n.startswith('neck/Neck') and not any(k in n.lower() for k in ('bolt','nut','washer','screw')):targets.pop(n)
 return targets,torso

def run():
 tick=time.monotonic();q=H.read(OUT/'anchor-native-checks.json')
 assert q['native_parameter_restore'] and q['fresh_relocated_reopen'] and not q['outside']
 assert len(q['contacts'])==1 and q['contacts'][0]['a']=='SocketKey'
 assert P.sha(B.MODEL)==q['model_sha256']
 reader=P.SavedShapes();targets,torso=physical_scene(reader)
 targets.update({'head/'+n:s for n,s in H.head(reader).items()})
 targets['Anchor']=reader.shape(B.MODEL,'HeadFixedAnchor')
 targets['Carrier']=reader.shape(B.MODEL,'UpperCarrier001')
 r=dict(status='PENDING',contacts=[],pairs=0,physical_pass=False,selected=False)
 for i,(x,y) in enumerate(B.AXES):
  vertical=Part.makeCylinder(1.5,18,A.Vector(x,y,84.22))
  handle=Part.makeCylinder(1.5,40,A.Vector(x,y,102.22),A.Vector(-1 if i==0 else 1,0,0))
  for name,s in [('Lkey_vertical',vertical),('Lkey_handle',handle)]:
   for m,t in targets.items():
    if not H.T.near(s,t,0):continue
    r['pairs']+=1;v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids)
    if v>1e-5:r['contacts'].append(dict(axis=i,a=name,b=m,volume_mm3=v))
 assert not r['contacts'],r['contacts']
 r.update(status='CURRENT_W2_ANCHOR_RELEASE_PREPARED',model_sha256=q['model_sha256'],exports=q['exports'],
  native_parameter_restore=True,fresh_relocated_reopen=True,worker_seconds=round(time.monotonic()-tick,3),
  native_pairs=q['pairs']-1,moving_loop_pairs=45,tool_assumption='Lhex2.5mmAF withinOD3,18mm vertical and40mm horizontal outboard±X; delivered key fit gate, not a50mm straight screwdriver.',
  fixed_tail_y_mm=[67,76],band_y_mm=[73,75.5],source_sha256={**reader.hashes,Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__)),
   (OUT/'anchor-native-checks.json').relative_to(ROOT).as_posix():P.sha(OUT/'anchor-native-checks.json')})
 H.save('anchor-release-checks.json',r);print(json.dumps(r),flush=True)
if __name__=='__main__':run()
