"""Whole W4 station: unclipped factory lead, JR/local tails and removable rail.

No selected M3 part is drilled or replaced. Two ordinary bands retain a new
rail on the existing fixed JR shelf; both housing and wire bands are separate.
"""
import json,math,time
from functools import lru_cache
from pathlib import Path
import numpy as np
import plan_current_tail_complete as Q
from head_local_rigid_conductors_r1 import radius
A,Part,P,ROOT,BASE,OUT=Q.A,Q.Part,Q.P,Q.ROOT,Q.BASE,Q.OUT
C=Q.C;B=C.B;old_scene=B.scene;old_local=C.retained_local

def coil(r):
 u=np.linspace(0,1,601);s=10*u**3-15*u**4+6*u**5;a=math.pi/2+2*math.pi*u
 return np.column_stack([149+16*s+r*np.cos(a),-41.5-6.5*s+r*(np.sin(a)-1),120.5-8.5*s])

@lru_cache(maxsize=1)
def factory():
 parts=[Q.arc([171,-19.5,94],[171,-19.5,72],[171,-41.5,94]),Q.line([171,-41.5,94],[171,-41.5,98.5]),Q.arc([149,-41.5,98.5],[171,-41.5,98.5],[149,-41.5,120.5])]
 approach=Q.wire(parts);remaining=247-approach.Length;lo,hi=22.,30.
 for _ in range(40):
  r=(lo+hi)/2;points=coil(r);length=np.linalg.norm(np.diff(points,axis=0),axis=1).sum()
  if length>remaining:hi=r
  else:lo=r
 def edge(r):
  c=Part.BSplineCurve();c.interpolate([A.Vector(*p) for p in coil(r)]);return c.toShape()
 lo,hi=r-.01,r+.01
 for _ in range(32):
  r=(lo+hi)/2;e=edge(r)
  if e.Length>remaining:hi=r
  else:lo=r
 curve=Part.Wire(list(approach.Edges)+[edge((lo+hi)/2)])
 assert curve.isValid() and abs(curve.Length-247)<1e-4 and radius(curve.Edges[-1])>=22,(curve.Length,radius(curve.Edges[-1]))
 return curve,dict(uncut_total_mm=250,exit_stub_mm=3,external_mm=curve.Length,approach_mm=approach.Length,
  radius_mm=min(22,radius(curve.Edges[-1])),storage_radius_mm=(lo+hi)/2,JR_factory_station_mm=[165,-48,112],
  profile_mm=[3.5,1.8],basis='Provisional flat cable andR22; no manufacturer dimensional claim; fit after delivery.')

def scene(reader):
 targets,torso=old_scene(reader)
 for n,s in targets.items():
  if n.startswith('local/'):s.translate(A.Vector(12,-3,20))
 targets.pop('Band_SourceBlack');targets.pop('TieHead_SourceBlack') # one matched paired-source replacement
 return targets,torso

def local(targets,reader):
 curves=old_local(targets,reader);curves.pop('local/factory_flat_circumscribed_RESERVATION')
 for c,r in curves.values():c.translate(A.Vector(12,-3,20))
 for name in ('XB32','XB33','XS33'):
  curves.pop('local/'+name+'/2_CENTERLINE')
  curves['local/'+name+'/2_CENTERLINE']=curves.pop('local/'+name+'/1_CENTERLINE')
 targets['local/JR_paired_RESERVATION']=Q.box([125,-54,107,155,-42,117])
 curve,_=factory();curves['local/factory_flat_circumscribed_RESERVATION']=(curve,math.hypot(1.75,.9))
 return curves

def build():
 p=Q.build();n=1.05/math.sqrt(3)*5/3;zr=112-2*n;zg=112+n
 red=p['routes']['XB32']['parts'][:7];red+=[Q.line([-65,-45,77.2],[20,-45,77.2])];red+=Q.shift(red[-1]['end'],[1,0,0],[0,-1,0],4.5)
 x=red[-1]['end'][0];red+=[Q.arc([x,-49.5,89.8],red[-1]['end'],[x+12.6,-49.5,89.8]),Q.line([x+12.6,-49.5,89.8],[x+12.6,-49.5,zr-12.6]),
 Q.arc([x+25.2,-49.5,zr-12.6],[x+12.6,-49.5,zr-12.6],[x+25.2,-49.5,zr])];red+=Q.shift(red[-1]['end'],[1,0,0],[0,1,0],1.5);red+=[Q.line(red[-1]['end'],[88,-48,zr])]
 g=[Q.line([37.5,-44.5,141],[46.5,-44.5,141])]
 g+=Q.shift(g[-1]['end'],[1,0,0],[0,-1,0],1.75)
 x=g[-1]['end'][0];g+=[Q.arc([x,-46.25,128.4],g[-1]['end'],[x+12.6,-46.25,128.4]),Q.line([x+12.6,-46.25,128.4],[x+12.6,-46.25,zg+12.6]),
 Q.arc([x+25.2,-46.25,zg+12.6],[x+12.6,-46.25,zg+12.6],[x+25.2,-46.25,zg]),Q.line([x+25.2,-46.25,zg],[88,-46.25,zg])]
 sig=p['routes']['XS33']['parts'][:-4];sig+=[Q.line(sig[-1]['end'],[40,-46.05,95])];sig+=Q.shift(sig[-1]['end'],[1,0,0],[0,0,1],zg-95)
 sig+=Q.shift(sig[-1]['end'],[1,0,0],[0,-1,0],3.7);sig+=[Q.line(sig[-1]['end'],[88,-49.75,zg])]
 for n,parts in [('XB32',red),('XB33',g),('XS33',sig)]:p['routes'][n]['parts']=parts
 p['local_translation_mm']=[12,-3,35];p['JR_bounds_mm']=[125,-54,107,155,-42,117]
 p['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()]=P.sha(Path(__file__))
 return p

def layout():
 result=Q.layout()
 # Ground now uses the full9mm source stub as its independent grip. Move
 # its complete support/band to that stub, not into the short vertical leg.
 result.pop('E2W4Addition');result.pop('Band_Ground');result.pop('TieHead_Ground')
 result['E2W4Addition']=Q.channel(Q.box([39,-47.5,132.3,49,-41.5,139.95]),[42.1,-48,137.4,44.9,-30,139])
 result['E2W4Addition']=Q.channel(result['E2W4Addition'],[42.1,-47.15,137.2,44.9,-45.55,144])
 result['Band_PairedSourceGround'],result['TieHead_PairedSourceGround']=Q.tie_x(43.5,-46.95,-30.2,137.4,143.325)
 # One native removable arch, seated on selected shelfZ86; no new holes.
 rail=Q.union([Q.box([77,-54,103,165,-36,106]),Q.box([123.5,-55.5,103,156.5,-40.5,106]),Q.box([125,-54,106,155,-42,107]),
 Q.box([123.5,-55.5,106,156.5,-54.5,109]),Q.box([123.5,-41.5,106,156.5,-40.5,109]),Q.box([123.5,-54.5,106,124.5,-41.5,109]),Q.box([155.5,-54.5,106,156.5,-41.5,109]),
 Q.box([113,-51.3,86,123,-38.7,103]),Q.box([133,-51.3,86,143,-38.7,103]),
 Q.box([136,-97,103,144,-50,106]),Q.box([136,-95.6,106,144,-87.4,115.0])]+[Q.box([x-4,-51.2,106,x+4,-44.8,108.85]) for x in (85,112)])
 for x in (118,138):
  rail=Q.channel(rail,[x-1.5,-54,104.8,x+1.5,-36.9,106.3])
  for a,b in [(-52.9,-51.3),(-38.7,-37.1)]:rail=Q.channel(rail,[x-1.5,a,81.4,x+1.5,b,106.3])
 # Full band legs cross the housing fences, not just the floor. The north
 # passage also receives the complete4.8mm head, with0.2mm side clearance.
 rail=Q.channel(rail,[143.5,-57,102.8,146.5,-53,109.2])
 rail=Q.channel(rail,[142.4,-43,102.8,147.6,-35.8,112.05])
 result['TailLocalRail']=rail
 # Rail straps pass around the entire fixed shelf and theirown posts.
 for x in (85,112):
  rail=Q.channel(rail,[x-1.5,-53,101.6,x+1.5,-43.2,103.2])
  for a,b in [(-53,-51.15),(-44.85,-43.2)]:rail=Q.channel(rail,[x-1.5,a,101.6,x+1.5,b,109.1])
 for a,b in [(-97,-95.6),(-87.4,-85.8)]:rail=Q.channel(rail,[138.5,a,102.8,141.5,b,124])
 result['TailLocalRail']=rail
 for x in (118,138):result['Band_Rail'+str(x)],result['TieHead_Rail'+str(x)]=Q.tie_x(x,-52.7,-37.3,81.6,106.2)
 # Two housing bands and two separate insulation bands on the new rail.
 for x in (145,):result['Band_JR'+str(x)],result['TieHead_JR'+str(x)]=Q.tie_x(x,-55.4,-40.6,101.8,118.4)
 for x in (85,112):result['Band_Local'+str(x)],result['TieHead_Local'+str(x)]=Q.tie_x(x,-52.4,-43.6,101.8,115.9)
 result['Band_FactoryGuard'],result['TieHead_FactoryGuard']=Q.tie_x(140,-97,-86,101.8,123.5)
 return result

def run():
 tick=time.monotonic();curve,meta=factory();path=OUT/'FactoryElevatedReceivedCentreline.brep';curve.exportBrep(str(path));B.save('factory-elevated-received-plan.json',meta)
 C.build=build;C.retained_local=local;B.scene=scene;C.run('elevated-received',lambda unused:layout())
 # The complete local group also needs its own neighbour/self receipt.
 reader=P.SavedShapes();targets,torso=scene(reader);curves=local(targets,reader);targets.update(layout())
 r=dict(status='PENDING',contacts=[],pairs=0,physical_pass=False,selected=False,factory=meta)
 for n,(s,rr) in curves.items():
  for m,t in targets.items():
   if m.startswith('local/') and not 'factory' in n:continue
   if not C.near(s,t,rr):continue
   r['pairs']+=1;d=s.distToShape(t)[0]
   if d<rr-1e-5:r['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=rr))
 # Factory's nonlocal return must not cross its own approach. Sharedjoint
 # is removed locally only, not an entire curve or housing.
 approach=Part.Wire(curve.Edges[:-1]);end=approach.Vertexes[-1].Point;ball=Part.makeSphere(6,end)
 d=approach.cut(ball).distToShape(curve.Edges[-1].cut(ball))[0]
 r['factory_nonlocal_distance_mm']=d
 if d<2*math.hypot(1.75,.9):r['contacts'].append(dict(a='factory_approach',b='factory_storage',distance_mm=d))
 r.update(status='CURRENT_W4_LOCAL_PREPARED' if not r['contacts'] else 'CURRENT_W4_LOCAL_REJECTED',worker_seconds=round(time.monotonic()-tick,3),source_sha256=reader.hashes,curve_sha256=P.sha(path))
 B.save('elevated-received-local-checks.json',r);print(json.dumps({k:r[k] for k in ('status','contacts','pairs','factory_nonlocal_distance_mm','worker_seconds')}),flush=True)
if __name__=='__main__':run()
