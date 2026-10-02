"""Match existing proven Deck to corrected source posts, without recompute loops.

Physical contacts remain blockers. Temporary head-tool contacts are reported
separately with an explicit before-wiring installation/removal sequence.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,shutil
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/cad'),str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/battery-feed-pair-r2'
CAD=ROOT/'hardware/cad/studies/battery-feed-pair-r2'


def main():
    import FreeCAD as A
    import Part
    import main_positive_input_r1 as C
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    rr=ROOT/'hardware/electronics/full-cat/battery-feed-return-finish-r2'
    mr=ROOT/'hardware/electronics/full-cat/battery-feed-mount-finish-r2'
    rc=json.loads((rr/'checks.json').read_text(encoding='utf-8'));mc=json.loads((mr/'checks.json').read_text(encoding='utf-8'))
    assert not rc['hits'] and not rc['errors'] and all(r['hit_mm3']<1e-5 for r in mc['checks'])
    assert sha(ROOT/'tools/electronics/battery_feed_mount_finish_r2.py')==mc['script_sha256']
    assert sha(ROOT/rc['native']['path'])==rc['native']['sha256']
    hashes={}
    def load(p):
        p=Path(p);hashes[p.relative_to(ROOT).as_posix()]=sha(p);s=Part.Shape();s.read(str(p));return s
    parts={}
    for folder in [ROOT/'hardware/electronics/full-cat/battery-feed-bridge-r1',mr,rr]:
        for p in folder.glob('*_DESIGN.brep'):
            if folder.name=='battery-feed-bridge-r1' and p.stem.startswith(('W001_','M2','Bridge')):continue
            parts[p.stem[:-7]]=load(p)
    parts['Bridge']=load(ROOT/'hardware/cad/studies/battery-feed-mount-finish-r2/Bridge_WORLD.brep')
    deck=load(ROOT/'hardware/cad/studies/battery-feed-return-finish-r2/Deck_WORLD.brep')
    owners,parent_hashes=C.current_owners();owners.pop('Deck_R41');owners.pop('MAIN_R40')
    owners['MAIN_R44']=load(ROOT/'hardware/cad/studies/main-positive-native-r2/MAIN_WORLD.brep')
    for folder,pattern in [('hardware/electronics/full-cat/main-positive-complete-r8','*_DESIGN.brep'),('hardware/cad/studies/main-positive-native-r2','*_WORLD.brep')]:
        for p in (ROOT/folder).glob(pattern):
            if p.stem not in ('Deck_WORLD','MAIN_WORLD'):owners['R44/'+p.stem]=load(p)
    owners['Deck_candidate']=deck
    for n in list(owners):
        if n.startswith(('BatteryCarrier','BatteryLiner','BatteryStrap','BatteryScrew','BatteryNut')):del owners[n]
    hits=[];tool_contacts=[];errors=[];pairs=0
    def check(n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox):continue
                pairs+=1
                try:
                    v=a.common(b).Volume
                    if v>1e-5:
                        row=dict(part=n,owner=m,hit_mm3=v)
                        if n.startswith('HeadToolReserve_') and ('head-connected-feeds-r8/' in m or m=='W061_4_DESIGN'):
                            tool_contacts.append(row)
                        else:hits.append(row)
                except Exception as ex:errors.append(dict(part=n,owner=m,error=str(ex)))
    for n,s in parts.items():
        for m,t in owners.items():
            if n=='G1BAT_seat' and m=='Deck_candidate':continue
            check(n,s,m,t)
        if n!='Bridge':check(n,s,'Bridge',parts['Bridge'])
        assert s.BoundBox.ZMin>28.7,n
    for x,y in mc['new_bolt_xy']:
        tool=Part.makeCylinder(1.19,8.2,A.Vector(x,y,100.9))
        assert tool.common(deck).Volume<1e-5 and tool.common(parts['Bridge']).Volume<1e-5
    for file in ('DeckBatteryFeed.FCStd','Deck_WORLD.brep','Deck_x1.stl'):
        source=ROOT/'hardware/cad/studies/battery-feed-return-finish-r2'/file
        hashes[source.relative_to(ROOT).as_posix()]=sha(source);shutil.copy2(source,CAD/file)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='REJECTED_PAIR' if hits or errors else 'NOMINAL_LOCAL_FEED_PAIR_WITH_ASSEMBLY_ACCESS_CONDITION',
        hits=hits,errors=errors,tool_access_contacts=tool_contacts,pairs=pairs,mount_xy=mc['new_bolt_xy'],
        old_holes_absent=True,old_holes_note='Y61 rejected pair is not the selected Deck; retained R2 Deck has the two required Y53 holes.',
        parameter_volumes=rc['native']['parameter_volumes'],relocated_reopen=True,
        native_proof_scope='Reuse pinned successful R2 native Deck proof; corrected bridge has its own restored/relocated proof. No new whole-Deck recompute claim.',
        strict_BOP_errors=0,closed_STL=True,dimensions_mm=rc['native']['dimensions_mm'],
        deck_native=(CAD/'DeckBatteryFeed.FCStd').relative_to(ROOT).as_posix(),deck_native_sha256=sha(CAD/'DeckBatteryFeed.FCStd'),
        bridge_native=mc['native'],bridge_native_sha256=sha(ROOT/mc['native']),source_sha256={**parent_hashes,**hashes},
        native_parent_proof_sha256=sha(rr/'checks.json'),bridge_proof_sha256=sha(mr/'checks.json'),script_sha256=sha(Path(__file__)),
        W075_blank_mm=40,W001_blank_mm=140,W076_selected_blank_mm=None,extra_T18I_ties=7,
        extra_fasteners=dict(M2x12=2,DIN125M2=4,DIN934M2=2),
        assembly_access_condition='Fasten bridge before routing head-connected feeds and W061. For later top-tool access release/park those affected stationary wires with battery disconnected; restore their selected routes afterward. Tool corridor is NOT clear with those wires installed.',
        source_assumptions=rc['remaining'],cassette_drop40_bound='All new physical source members Zmin>28.7; unchanged R4 drop box ends28.7.',
        remaining=['S0 location, W076/W066 and full battery mate/reach.','WholeW5/E3/K2/K3/A2/A3 remain open.'],
        selected=False,W5_complete=False,physical_pass=False,started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print(json.dumps(dict(hits=hits,tool_access_contacts=tool_contacts,errors=errors,pairs=pairs,seconds=(end-start).total_seconds())),flush=True)


if __name__=='__main__':main()
