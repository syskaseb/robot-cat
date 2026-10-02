"""Two integral Deck cradles for the complete W066 R5 route.

Use the existing F0 restraint for W076 and the tied F_PI housing for W043.
No new splices, fastener family or electrical net. Screening precedes native
Deck update/selection. Left middle tie wraps the Deck edge intentionally.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/cad'),str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
LAYOUT=ROOT/'hardware/electronics/full-cat/source-switch-layout-r6'
OUT=ROOT/'hardware/electronics/full-cat/source-switch-restraints-r2'


def main():
    import FreeCAD as A
    import Part
    import main_positive_input_r1 as C
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    decision=json.loads((LAYOUT/'checks.json').read_text(encoding='utf-8'))
    assert not decision['hits'] and not decision['errors']
    owners,hashes=C.current_owners();owners.pop('Deck_R41');owners.pop('MAIN_R40')
    def load(p):
        p=Path(p);hashes[p.relative_to(ROOT).as_posix()]=sha(p);s=Part.Shape();s.read(str(p));return s
    deck=load(LAYOUT/'Deck_candidate_UNSELECTED.brep')
    owners['MAIN_R44']=load(ROOT/'hardware/cad/studies/main-positive-native-r2/MAIN_WORLD.brep')
    for folder,pattern in [('hardware/electronics/full-cat/main-positive-complete-r8','*_DESIGN.brep'),('hardware/cad/studies/main-positive-native-r2','*_WORLD.brep')]:
        for p in (ROOT/folder).glob(pattern):
            if p.stem not in ('Deck_WORLD','MAIN_WORLD') and not p.stem.startswith('W043_'):owners['R44/'+p.stem]=load(p)
    for p in LAYOUT.glob('*_DESIGN.brep'):
        if not p.stem.startswith('S0_key'):owners['Switch/'+p.stem]=load(p)
    for p,h in json.loads((ROOT/'hardware/electronics/full-cat/battery-feed-access-finish-r1/checks.json').read_text(encoding='utf-8'))['source_sha256'].items():
        if '/battery-feed-' in p and p.endswith('_DESIGN.brep'):
            if '/battery-feed-bridge-r1/' in p and Path(p).stem.startswith(('W001_','W076_FREE_STUB','M2','Bridge','F0BodyTie','FreeSwitchLeadWireTie','PlusWireTie','ReturnWireTie','XT60BodyTie')):continue
            if 'ToolReserve' not in p:owners['Source/'+Path(p).stem]=load(ROOT/p)
    owners['Source/Bridge']=load(ROOT/'hardware/cad/studies/battery-feed-mount-finish-r2/Bridge_WORLD.brep')
    for n in list(owners):
        if n.startswith(('BatteryCarrier','BatteryLiner','BatteryStrap','BatteryScrew','BatteryNut')):owners.pop(n)
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    seats={};bands={};slots=[];specs=[]
    for name,x,y,z,left,right in [('Middle',-90.5,-60,121.4,-93.4,-87.6),('P_SYS',-84,-15.25,113.5,-88.1,-79.9)]:
        yhalf=3.75 if name=='P_SYS' else 1.4
        raw=[x-3.3,y-yhalf,108.8,x+3.3,y+yhalf,z+.7]
        s=box(raw).cut(Part.makeCylinder(2.35,2*yhalf+.2,A.Vector(x,y-yhalf-.1,z),A.Vector(0,1,0)))
        bottom=109.5 if name=='P_SYS' else 103.8
        if name=='P_SYS':
            tunnel=[left-1,y-1.6,109.4,right+1,y+1.6,110.8]
            s=s.cut(box(tunnel));slots.append(box(tunnel))
        lanes=[]
        for sx in (left,right):
            b=[sx-.8,y-1.6,bottom if name=='P_SYS' else 104.9,sx+.8,y+1.6,z+2.7]
            lanes.append(b);slots.append(box(b));s=s.cut(box(b));deck=deck.cut(box(b))
        seats[name]=s;deck=deck.fuse(s)
        upper=z+2.35
        pieces=[box([sx-.6,y-1.25,bottom,sx+.6,y+1.25,upper+1.2]) for sx in (left,right)]
        pieces += [box([left-.6,y-1.25,upper,right+.6,y+1.25,upper+1.2]),
            box([left-.6,y-1.25,bottom,right+.6,y+1.25,bottom+1.2]),
            box([left-4.9 if name=='P_SYS' else right-1.4,y-2.5,bottom-.1 if name=='P_SYS' else 99.8,left+.1 if name=='P_SYS' else right+3.6,y+2.5,bottom+3.9 if name=='P_SYS' else 103.8])]
        bands[name]=Part.makeCompound(pieces)
        specs.append(dict(name=name,seat_box_mm=raw,groove_centre=[x,y,z],groove_radius_mm=2.35,
            groove_axis=[0,1,0],tie_lanes=lanes,tie_SKU='111-03110 T18I',tie_head_project_mm=[5,5,4],
            tie_head_not_measured=True,left_lane_open_deck_edge=name=='Middle',bottom_z=bottom,
            tie_tunnel=tunnel if name=='P_SYS' else None))
    assert deck.isValid() and len(deck.Solids)==1
    hits=[];errors=[];pairs=0
    def check(n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox):continue
                pairs+=1
                try:
                    v=a.common(b).Volume
                    if v>1e-5:hits.append(dict(part=n,owner=m,hit_mm3=v))
                except Exception as ex:errors.append(dict(part=n,owner=m,error=str(ex)))
    for n,s in {**{n+'_seat':s for n,s in seats.items()},**{n+'_tie':s for n,s in bands.items()}}.items():
        for m,t in owners.items():check(n,s,m,t)
        if n.endswith('_tie'):check(n,s,'Deck_candidate',deck)
        s.exportBrep(str(OUT/(n+'_DESIGN.brep')))
    for n,s in bands.items():
        for m,t in seats.items():check(n+'_tie',s,m+'_seat',t)
    for n,s in owners.items():
        if n.startswith('Switch/W'):check(n,s,'Deck_candidate',deck)
    deck.exportBrep(str(OUT/'Deck_candidate_UNSELECTED.brep'))
    end=datetime.now(timezone.utc)
    report=dict(status='REJECTED_RESTRAINTS' if hits or errors else 'COMPLETE_LOCAL_W066_RESTRAINTS_NEED_NATIVE_DECK',
        hits=hits,errors=errors,pairs=pairs,specs=specs,added_T18I=2,selected=False,W5_complete=False,physical_pass=False,
        W076_restraint='Selected R48 F0FreeSwitchLead cradle atX-26/Y65 retained, TE ring atS0 end; no splice.',
        W043_restraint='Selected R44 tied F_PI housing retained; short factory lead to adjacent P_SYS cage, no added joint.',
        P_SYS_labels_plus_X=decision['P_SYS_labels_plus_X'],
        native_required='Retain editable R48 Deck; add R5 portal/two bolt bores and these two cradle/strap lanes before selecting.',
        source_sha256=hashes,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds())
    save(OUT/'checks.json',report)
    print(json.dumps({k:report[k] for k in ('status','hits','errors','pairs','worker_wall_seconds')}),flush=True)

if __name__=='__main__':main()
