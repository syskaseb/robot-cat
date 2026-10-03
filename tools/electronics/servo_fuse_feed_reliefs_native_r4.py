"""Reconnect the preserved front-left lower lip with an explicit native rib.

R3 contact-sized slots preserved the upper cover but isolated its lower lip.
This changes construction, not just Boolean validation. Check the rib against
retained owners and all actual feeds before accepting even a candidate export.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_feed_reliefs_native_r3.py')
wrapper=parent.read_text(encoding='utf-8')
tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.count(tail)==1
exec(compile(wrapper.replace(tail,''),str(parent),'exec'))
code=code.replace('servo-fuse-feed-reliefs-native-r3','servo-fuse-feed-reliefs-native-r4')
def replace(old,new):
    global code
    assert code.count(old)==1,old[:80]
    code=code.replace(old,new)
replace("    pins = {dependency.relative_to(ROOT).as_posix():sha(dependency),", """    pins = {'tools/electronics/servo_fuse_feed_reliefs_native_r3.py':sha(ROOT/'tools/electronics/servo_fuse_feed_reliefs_native_r3.py'),
            'hardware/electronics/full-cat/servo-fuse-feed-reliefs-native-r3/fault.json':sha(ROOT/'hardware/electronics/full-cat/servo-fuse-feed-reliefs-native-r3/fault.json'),
            dependency.relative_to(ROOT).as_posix():sha(dependency),""")
replace("d.addObject('Part::Cut','FeedReliefsFinished')", "d.addObject('Part::Cut','FeedReliefsRaw')")
replace("            shape=final.Shape.copy();strict=shape.check(True)", """            bridge_hits=[]
            if tag=='Cover':
                rib=d.addObject('Part::Box','FrontLeftLipBridge')
                rib.Length=4;rib.Width=3.5;rib.Height=22
                rib.Placement.Base=A.Vector(-85,96.5,118)
                unionfinal=d.addObject('Part::Fuse','FeedReliefsFinished');unionfinal.Base=final;unionfinal.Tool=rib;unionfinal.Refine=False
                final.Visibility=False;rib.Visibility=False;final=unionfinal;d.recompute()
                from servo_fuse_rolled_cradles_native_r1 import retained_owners
                owners=retained_owners(pin,load,Part)
                for q in folder.glob('*_DESIGN.brep'):owners['ActualFeed/'+q.stem]=load(q)
                for name,owner in owners.items():
                    if name=='RetainedCover' or not rib.Shape.BoundBox.intersect(owner.BoundBox):continue
                    contact=rib.Shape.common(owner)
                    if contact.Volume>1e-5:bridge_hits.append(dict(owner=name,volume_mm3=contact.Volume))
                save(OUT/'bridge-fit.json',dict(bounds_mm=bounds(rib.Shape),hits=bridge_hits,physical_pass=False,selected=False))
                assert not bridge_hits,bridge_hits
            export_final_name=final.Name
            shape=final.Shape.copy();strict=shape.check(True)""")
replace("re.FeedReliefsFinished.Shape.Volume", "re.getObject(export_final_name).Shape.Volume")
replace("final='FeedReliefsFinished',", "final=export_final_name,bridge_hits=bridge_hits,")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
