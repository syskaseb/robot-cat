"""One coherent RR ownership change: fixed Deck station, removable bare bank.

The service pocket collides with fixed Deck/cover bracket and needs an open
lever translation. Avoid that unnecessary electrical disconnection: retain
the housing and both wire paths on fixed Deck, using its actually measured
west roof stock. Restore the bank parent without RR tray; preserve the open
post clearance from R5. Preflight the complete installed station and current
parents before any new native export. No guessed mounting screw or stock.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-fixed-station-r1'

def main():
    import FreeCAD as A
    import Part
    start=datetime.now(timezone.utc)
    loader=ROOT/'tools/electronics/servo_fuse_rr_clip_approach_r1.py'
    code=loader.read_text(encoding='utf-8');code=code[:code.index('    # These boxes are exactly')]
    code=code.replace('servo-fuse-rr-clip-approach-r1','servo-fuse-rr-fixed-station-r1')+'    return owners,pins,final\n'
    ns=dict(__file__=str(loader),__name__='owners_only');exec(compile(code,str(loader),'exec'),ns)
    owners,pins,native=ns['main']();pins[loader.relative_to(ROOT).as_posix()]=sha(loader)
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def load(p):pin(p);return Part.read(str(p))
    def read(p):pin(p);return json.loads(p.read_text(encoding='utf-8'))
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    parked=read(ROOT/'hardware/electronics/full-cat/servo-fuse-rr-output-park-r1/checks.json')
    assert parked['hits'] and not parked['errors']
    # Proven exact fixed roof contact in R1, not inferred from a bbox alone.
    assert any(r['phase']=='installed_added_floor' and r['owner']=='CandidateDeck' and abs(r['mm3']-38.4)<1e-5 for r in parked['hits'])
    rr=load(ROOT/'hardware/electronics/full-cat/servo-fuse-rear-output-stations-native-r3/RRFixture_DESIGN.brep')
    bridge_b=[-75.5,-95,109.35,-67.5,-91,111.75]
    bridge=box(bridge_b);roof=box([-75.5,-95,109.35,-71.5,-91,111.75])
    embed=roof.common(owners['CandidateDeck']).Volume
    assert abs(embed-38.4)<1e-5,embed
    # Match both actual installed input paths; retain their centreline and OD.
    wire_tools=[]
    for ident in ('W038','W039'):
        p=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-connected-release-r4'/('release_0.0_'+ident+'_CENTERLINE.brep')
        path=Part.Wire(load(p).Edges);edge=path.Edges[0];normal=edge.tangentAt(edge.FirstParameter)
        profile=Part.Wire([Part.makeCircle(3.1/2+.2,path.Vertexes[0].Point,normal)])
        wire_tools.append(path.makePipeShell([profile],True,False))
    bridge=bridge.cut(wire_tools[0].fuse(wire_tools[1]))
    fixture=rr.fuse(bridge)
    # Reuse actual R5 three native boxes to free the original raised bank
    # post. Do NOT retain RR grip stock or the R5 replacement support frame.
    bankbase=load(ROOT/'hardware/cad/studies/servo-fuse-rear-output-reliefs-native-r1/BankRight_WORLD.brep')
    access=read(ROOT/'hardware/electronics/full-cat/servo-fuse-rr-output-disconnect-r2/checks.json')
    banktools=[];bank_tool_boxes=[]
    for k,h in enumerate(access['hits']):
        b=list(h['bounds_mm'])
        if k==2:b[2]=117.5
        q=[b[i]-.2 for i in range(3)]+[b[i]+.2 for i in range(3,6)]
        bank_tool_boxes.append(q);banktools.append(box(q))
    bank=bankbase.cut(banktools[0].multiFuse(banktools[1:]))
    deck=owners['CandidateDeck'].fuse(fixture)
    states=[]
    for n,s in [('Deck',deck),('BankRight',bank)]:
        states.append(dict(part=n,valid=s.isValid(),solids=len(s.Solids),BOP=[str(e) for e in (s.check(True) or [])]))
        s.exportBrep(str(OUT/(n+'_CANDIDATE.brep')))
    # Never silently remove disconnected pieces or qualify a failed parent.
    owners['Bank/RightClipAccessFinished_WORLD']=bank;owners['CandidateDeck']=deck
    hits=[];errors=[];pairs=0
    def check(name,s,key,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            c=s.common(t)
            if c.Volume>1e-5:
                hits.append(dict(part=name,owner=key,mm3=c.Volume,bounds_mm=bounds(c)))
                c.exportBrep(str(OUT/f'HIT_{len(hits)}.brep'))
        except Exception as e:errors.append(dict(part=name,owner=key,error=str(e)))
    for key,t in owners.items():
        if key=='CandidateDeck':continue # deliberate full fixed-Deck union
        check('FixedRRStation',fixture,key,t)
    # Three retained RR ties are now attached to this FIXED station, not to
    # the moving bank. Recheck only their new fixture intersection.
    for key,t in owners.items():
        if key.startswith('CurrentRear/RR'):check(key,t,'FixedRRStation',fixture)
    fixture.exportBrep(str(OUT/'RR_FIXED_FIXTURE.brep'));bridge.exportBrep(str(OUT/'RR_ROOF_BRIDGE.brep'))
    save(OUT/'checks.json',dict(status='FIXED_RR_STATION_PREFLIGHT_CONFLICTS' if hits or errors or any(not r['valid'] or r['solids']!=1 or r['BOP'] for r in states) else 'FIXED_RR_STATION_PREFLIGHT_CLEAR_NATIVE_PENDING',
        selected=False,physical_pass=False,W5_complete=False,states=states,hits=hits,errors=errors,pairs=pairs,
        new_owner='FIXED_DECK',old_owner='REMOVABLE_BANK_RIGHT',wire_paths_changed=False,installed_straps_changed=False,
        roof_embed_mm3=embed,bridge_bounds_mm=bridge_b,bank_tool_boxes_mm=bank_tool_boxes,
        stock_delta=dict(additional_prints=0,fasteners=0,wires=0,straps=0),
        sequence='Prewire both RR output cages on removed Deck and secure existing3ties to fixed station. Bank+Cover can then be removed without opening or translating this connector; shared lift still requires current joint check.',
        native_export_complete=False,common_module_lift_qualified=False,
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
        worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds()))
    print('FIXED_RR_STATION_PREFLIGHT',json.dumps(dict(states=states,pairs=pairs,hits=hits,errors=errors)),flush=True)
if __name__=='__main__':main()
