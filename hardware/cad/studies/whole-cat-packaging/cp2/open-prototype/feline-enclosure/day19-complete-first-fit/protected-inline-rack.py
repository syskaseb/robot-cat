from pathlib import Path
P=Path(__file__).parent;text=(P/'closed-leg-well.py').read_text()
exec(text[:text.index("n='H19_FrontFrame'")])
s=Part.Shape();s.read(str(P/'before-well.tmp.brep'));s=s.Solids[0]
names=['NIGHT_INLINE_FL_W026','NIGHT_INLINE_FL_W041']
for name,origy in zip(names,[-88,-78]):
 for station in [.19,.76]:
    x=-104+35.5*station;s=s.cut(box(x-.02,origy-1.12,45.48,3.44,10.34,8.27),.00001)
# Reinstate the prior side wall locally and close the wheel well. Both inline
# housings now belong to one separate pair of levels clear of the leg envelope.
t=text[text.index('# Reuse exactly'):text.index('r=dict(')].replace('.fuse(join(tabs),.00001)','');exec(t)
assert s.isValid() and len(s.Solids)==1
# C-shaped bearings open at -Y. Wire both ends before sliding the lower unit
# sideways; the upper nest has its own open mouth. Factory plugs need not pass a ring.
rack=[];zlevels=[67,80]
for i,(name,z0) in enumerate(zip(names,zlevels)):
 o=D.getObject(name);b=sh(name).BoundBox;o.Placement=A.Placement(V(-26.75-b.XMin,-38.05-b.YMin,z0-b.ZMin),A.Rotation()).multiply(o.Placement)
 for x in [-25.6,5.0]:
    rack.extend([box(x,-39.1,z0-2.15,3.25,12.8,2.15),box(x,-29.76,z0-1,3.25,2.8,11.5),box(x,-37.88,z0+9.12,3.25,10.6,1.2),box(x,-39.10,z0-1.6,3.25,.9,2.4)])
 for x in [-27.99,8.94]:
    rack.append(box(x,-30.4,z0-1.55,1.08,3.65,3.1))
 rack.append(box(-28,-29.65,z0-2.15,38.02,2.85,2.12))
for x in [-25.55,6.45]:
 rack.append(box(x,-29.45,41.1,2.9,2.65,48.5))
rack.append(box(-25.55,-29.45,41.1,35,2.65,3.1))
# A cross-member extends to the retained negative anchor rail below the fuse bodies.
rack.append(box(-25.5,-29.45,41.1,3.3,8.7,3.1))
rack=join(rack);wr('rack-debug.json',dict(host=s.isValid(),rack=rack.isValid(),pieces=[dict(volume=a.Volume,box=bounds(a)) for a in rack.Solids]))
s.exportBrep(str(P/'well-no-inline.tmp.brep'))
res=s.Solids[0]
for a in rack.Solids:res=res.fuse(a,.00001)
res=res.removeSplitter()
report=dict(without_rack=s.Volume,rack_volume=rack.Volume,host_overlap=s.Volume+rack.Volume-res.Volume,members=[dict(volume=v.Volume,bounds=bounds(v)) for v in res.Solids],valid=res.isValid(),moved={n:bounds(sh(n)) for n in names},open_side='-Y',two_separate_levels=zlevels)
wr('inline-installed.json',report);assert res.isValid() and len(res.Solids)==1
D.getObject('H19_FrontFrame').Shape=res
# Make a seat for the HP keeper's external spring corner on the second original rung.
n='I19_FuseBand_HP';keeper=sh(n);res=res.Solids[0].cut(keeper.makeOffsetShape(.14,.01),.00001).removeSplitter()
assert len(res.Solids)==1 and res.isValid();D.getObject('H19_FrontFrame').Shape=res
# Relieve only the outboard edge of the XT60 support at the adjacent full JPWM housing.
n='E19_RearLid';old=sh(n);s=old.cut(box(34.75,-24.05,119.75,.63,3.45,12.5),.00001).removeSplitter()
assert len(s.Solids)==1 and s.isValid();D.getObject(n).Shape=s
wr('two-plug-seats.json',dict(initial_common=7.44,relief_volume=old.Volume-s.Volume,remaining_cup_width=2.25,JPWM=sh('E19_FieldJPWM').common(s).Volume))
D.recompute();D.save()
