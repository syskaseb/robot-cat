"""Keep the original four bank mounts; wrap fixed RR stock around them.

R1's three lever openings severed RightPost57 from its bolted foot. That
cannot qualify a removable bank. Fixed ownership removes the need to open
the RR cages for bank removal: retain the entire R19 bank and its foot/post,
subtract their actual material plus native foot/post clearance from the
fixed fixture. Inspect fixture connectivity before union/export of Deck.
No dropped solids, removed fastener, changed wire or extra printed part.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-fixed-station-r2'

def main():
    import FreeCAD as A
    import Part
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists(),'Preserve result'
    loader=ROOT/'tools/electronics/servo_fuse_rr_clip_approach_r1.py'
    code=loader.read_text(encoding='utf-8');code=code[:code.index('    # These boxes are exactly')]
    code=code.replace('servo-fuse-rr-clip-approach-r1','servo-fuse-rr-fixed-station-r2')+'    return owners,pins,final\n'
    ns=dict(__file__=str(loader),__name__='owners_only');exec(compile(code,str(loader),'exec'),ns)
    owners,pins,_=ns['main']();pins[loader.relative_to(ROOT).as_posix()]=sha(loader)
    def load(rel):
        p=ROOT/rel;pins[rel]=sha(p);return Part.read(str(p))
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    fixture0=load('hardware/electronics/full-cat/servo-fuse-rr-fixed-station-r1/RR_FIXED_FIXTURE.brep')
    bank=load('hardware/cad/studies/servo-fuse-rear-output-reliefs-native-r1/BankRight_WORLD.brep')
    native=ROOT/'hardware/cad/studies/servo-fuse-rear-output-reliefs-native-r1/BankRightRearOutputPassages.FCStd'
    pins[native.relative_to(ROOT).as_posix()]=sha(native)
    d=A.openDocument(str(native))
    try:
        # Proven structural owners, not an arbitrary disconnected volume.
        foot=d.RightFoot57.Shape.copy();post=d.RightPost57.Shape.copy()
        footclear=foot.makeOffsetShape(.2,1e-6);postclear=post.makeOffsetShape(.2,1e-6)
    finally:A.closeDocument(d.Name)
    tools=bank.fuse(footclear).fuse(postclear)
    fixture=fixture0.cut(tools)
    fixture.exportBrep(str(OUT/'RR_FIXED_FIXTURE.brep'))
    footclear.exportBrep(str(OUT/'FOOT_CLEARANCE.brep'));postclear.exportBrep(str(OUT/'POST_CLEARANCE.brep'))
    states=dict(valid=fixture.isValid(),solids=len(fixture.Solids),BOP=[str(e) for e in (fixture.check(True) or [])],
                solid_volumes_mm3=[s.Volume for s in fixture.Solids])
    owners['Bank/RightClipAccessFinished_WORLD']=bank
    hits=[];errors=[];pairs=0
    for key,t in owners.items():
        if key=='CandidateDeck':continue # intended fixture/roof embed
        if not fixture.BoundBox.intersect(t.BoundBox):continue
        pairs+=1
        try:
            c=fixture.common(t)
            if c.Volume>1e-5:hits.append(dict(owner=key,mm3=c.Volume,bounds_mm=bounds(c)))
        except Exception as e:errors.append(dict(owner=key,error=str(e)))
    embed=fixture.common(owners['CandidateDeck']).Volume
    save(OUT/'checks.json',dict(status='FIXED_RR_WRAPPED_STATION_PREFLIGHT',selected=False,physical_pass=False,
        W5_complete=False,states=states,pairs=pairs,hits=hits,errors=errors,deck_embed_mm3=embed,
        original_bank_retained=True,bank_mounts_preserved=4,bank_changed=False,
        fixture_tool_owners=['RightFoot57','RightPost57','complete R19 bank'],clearance_mm=.2,
        wires_changed=False,purchased_parts_changed=False,installed_ties_changed=False,
        native_export_complete=False,common_module_lift_qualified=False,
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),
        finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds()))
    print('FIXED_RR_WRAPPED_PREFLIGHT',json.dumps(dict(states=states,pairs=pairs,hits=hits,errors=errors,embed=embed)),flush=True)
if __name__=='__main__':main()
