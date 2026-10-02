"""One full twelve-input candidate, with explicit replaceable terminal datums.

No inferred MTA blade spacing or seating depth: e=0 and axes +/-7mm are
prototype parameters, not supplier dimensions. Failed geometry is never selected.
"""
from pathlib import Path
from datetime import datetime, timezone
import sys, json, math, hashlib
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/cad'),str(ROOT/'tools/electronics')]
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-inputs-r1'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rounded(points,r):
    import FreeCAD as A
    import Part
    edges=[];current=points[0]
    for i in range(1,len(points)-1):
        p=points[i];u=p-points[i-1];v=points[i+1]-p;u.normalize();v.normalize()
        angle=math.acos(max(-1,min(1,u.dot(v))));cut=r*math.tan(angle/2)
        before=p-u*cut;after=p+v*cut
        assert (before-current).dot(u)>-1e-7,'Overlapping bends'
        if (before-current).Length>1e-7:edges.append(Part.makeLine(current,before))
        normal=v-u*u.dot(v);normal.normalize();centre=before+normal*r
        mid=(before-centre)+(after-centre);mid.normalize()
        edges.append(Part.Arc(before,centre+mid*r,after).toShape());current=after
    assert (points[-1]-current).Length>1e-7
    edges.append(Part.makeLine(current,points[-1]));wire=Part.Wire(edges)
    for a,b in zip(edges,edges[1:]):
        assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-7
        assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length<1e-7
    return wire
def main():
    import FreeCAD as A
    import Part
    import main_positive_input_r1 as C
    begin=datetime.now(timezone.utc)
    OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'checks.json').exists()
    if begin>=datetime.fromisoformat('2026-10-02T08:30:00+00:00'):raise RuntimeError('Deadline')
    ledger=ROOT/'hardware/electronics/full-cat/body-harness-w5-r1/interface.json'
    rows=[r for r in json.loads(ledger.read_text(encoding='utf-8'))['conductors'] if r['group']=='SERVO_FUSE_INPUTS']
    assert len(rows)==12
    sources=[ledger,ROOT/'hardware/reference/servo-holder-p0-2026-09-24/ENVELOPE.md',ROOT/'hardware/electronics/power-platform/SERVO-HOLDERS-P0.md',ROOT/'hardware/manufacturing/one-batch-prototype-r44/selection.json']
    intent=dict(parent='one-batch-prototype-r44',physical_pass=False,selected=False,W5_complete=False,
        prototype={'MTA_terminal_seating_e_mm':0,'terminal_axis_offset_y_mm':7,'IN_length_mm':23.749,'OUT_length_mm':21.717,'IN_width_max_mm':10.3886,'length_tolerance_mm':.381,'LAPP_OD_mm':3.1,'minimum_fixed_radius_mm':12.4},
        distinction='Terminal e/axis coordinates and cage order are explicit prototype assumptions. No measured blade geometry. Conservative straight insulated connector reserves, not fitted models.',
        old_input_blank_limit_mm=100,portal_policy='Candidate full Deck crossing; cut is NOT made in selected CAD before clear route and restraints.',
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sources},started_utc=begin.isoformat())
    save(OUT/'intent.json',intent)
    owners,hashes=C.current_owners()
    def load(rel):
        p=ROOT/rel;hashes[rel]=sha(p);s=Part.Shape();s.read(str(p));return s
    owners.pop('Deck_R41');owners.pop('MAIN_R40')
    deck=load('hardware/cad/studies/main-positive-native-r2/Deck_WORLD.brep')
    owners['MAIN_R44']=load('hardware/cad/studies/main-positive-native-r2/MAIN_WORLD.brep')
    for p in (ROOT/'hardware/electronics/full-cat/main-positive-complete-r8').glob('*_DESIGN.brep'):
        owners['R44/'+p.stem]=load(p.relative_to(ROOT).as_posix())
    for p in (ROOT/'hardware/cad/studies/main-positive-native-r2').glob('*_WORLD.brep'):
        if p.stem not in ('MAIN_WORLD','Deck_WORLD'):owners['R44/'+p.stem]=load(p.relative_to(ROOT).as_posix())
    placements={};paths={};terminals={};lengths=[];portals=[]
    box=lambda b:Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    for row in rows:
        fuse=next(p for p in (row['a'],row['b']) if p.startswith('F_'))
        wago=next(p for p in (row['a'],row['b']) if not p.startswith('F_'))
        leg=fuse[2:4];index=int(fuse[4]);side=1 if leg.endswith('L') else -1
        base=-69 if leg.startswith('F') else 39
        port=int(wago.split('.')[1]);start=[base+(port-3)*6.75,side*30.5,113.5]
        cx=base+26*(index-1);cy=side*75
        for role,dy,L,H in [('IN',7,23.749,9.8552),('OUT',-7,21.717,5.080)]:
            ty=cy+side*dy;bottom=82.5-L-.381
            b=[cx-5.1943,ty-(H+.381)/2,bottom,cx+5.1943,ty+(H+.381)/2,82.5]
            terminals[f"{fuse.split('.')[0]}_{role}"]=box(b)
            if role=='IN':end=[cx,ty,bottom]
        points=[start,[start[0],side*15,113.5],[start[0],side*15,43],[cx,end[1],43],end]
        wire=rounded([A.Vector(*p) for p in points],12.4)
        parts=[]
        for j,e in enumerate(wire.Edges):
            tube=Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(1.55,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False)
            assert tube.isValid() and len(tube.Solids)==1
            tube.exportBrep(str(OUT/f"{row['id']}_{j}_DESIGN.brep"));e.exportBrep(str(OUT/f"{row['id']}_{j}_CENTERLINE.brep"));parts.append(tube)
        paths[row['id']]=Part.makeCompound(parts)
        portals.append(Part.makeCylinder(2.05,4.2,A.Vector(start[0],side*15,104.9)))
        radii=[e.Curve.Radius for e in wire.Edges if hasattr(e.Curve,'Radius')];assert min(radii)>=12.4-1e-7
        blank=math.ceil((wire.Length+14+8.30+10)/10)*10
        lengths.append(dict(id=row['id'],a=row['a'],b=row['b'],path_mm=wire.Length,nominal_blank_mm=blank,old_100mm_limit_met=blank<=100,allowances_mm={'WAGO_reserve':14,'FASTON_strip_max':8.30,'rework':10},actual_cut_mm=None))
        placements[row['id']]=dict(start=start,end=end,waypoints=points)
    for p in portals:deck=deck.cut(p)
    owners['Deck_WITH_UNSELECTED_PORTALS']=deck
    hits=[];tested=0
    def check(n,s,m,t):
        nonlocal tested
        if not s.BoundBox.intersect(t.BoundBox):return
        for q in s.Solids:
            for v in t.Solids:
                if q.BoundBox.intersect(v.BoundBox):
                    tested+=1;vol=q.common(v).Volume
                    if vol>1e-5:hits.append(dict(part=n,owner=m,hit_mm3=vol))
    for n,s in {**paths,**terminals}.items():
        for m,t in owners.items():check(n,s,m,t)
    keys=list(terminals)
    for i,n in enumerate(keys):
        for m in keys[i+1:]:check(n,terminals[n],m,terminals[m])
    for n,s in paths.items():
        for m,t in terminals.items():check(n,s,m,t)
    for i,n in enumerate(paths):
        for m in list(paths)[i+1:]:check(n,paths[n],m,paths[m])
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='REJECTED' if hits or not all(x['old_100mm_limit_met'] for x in lengths) else 'CLEAR_NEEDS_NATIVE_RESTRAINTS',
        selected=False,physical_pass=False,W5_complete=False,pairs=tested,hits=hits,lengths=lengths,placements=placements,
        terminals_checked=24,source_sha256=hashes,script_sha256=sha(Path(__file__)),
        stock=dict(legacy_LAPP_purchase_mm=2000,inputs_candidate_mm=sum(x['nominal_blank_mm'] for x in lengths),BAT_legacy_reserve_mm=150,remaining_mm=2000-150-sum(x['nominal_blank_mm'] for x in lengths)),
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(hits=len(hits),pairs=tested,blanks=[r['nominal_blank_mm'] for r in lengths],status='REJECTED' if hits else 'CLEAR_LENGTH_GATE_OPEN')),flush=True)
if __name__=='__main__':main()
