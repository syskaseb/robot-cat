"""Twelve local output spans from insulated TE ends to bank exit stations.

They are portions of the uncut factory servo leads, NOT extra purchased
cables/connectors. Full moving leg spans remain W5 and are not claimed here.
OD2.4/R10 are explicit prototype reservations, not delivered measurements.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math,re,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-outputs-r1'

def output_path(A,Part,start,side,R=10):
    p=A.Vector(*start);down=A.Vector(0,0,-1);x=A.Vector(1,0,0);out=A.Vector(0,side,0)
    edges=[Part.makeLine(p,p+down*5)];p=p+down*5
    def arc(first,last):
        nonlocal p
        begin=A.Vector(p)
        def q(t):return begin+first*(R*math.sin(t))+last*(R*(1-math.cos(t)))
        edges.append(Part.Arc(q(0),q(math.pi/4),q(math.pi/2)).toShape());p=q(math.pi/2)
    arc(down,x);arc(x,out)
    q=A.Vector(p.x,side*140,p.z);assert (q-p).dot(out)>0
    edges.append(Part.makeLine(p,q))
    for a,b in zip(edges,edges[1:]):
        assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-7
        assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length<1e-7
    return Part.Wire(edges),q

def main():
    import FreeCAD as A
    import Part
    import servo_fuse_side_bank_r9 as layout
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    ledger=ROOT/'hardware/electronics/full-cat/source-switch-selected-r1/body-harness.json'
    rows=[r for r in json.loads(ledger.read_text(encoding='utf-8'))['conductors'] if
          any(re.fullmatch(r'F_(FL|FR|RL|RR)[123]\.out',p) for p in (r['a'],r['b']))]
    assert len(rows)==12
    save(OUT/'intent.json',dict(selected=False,physical_pass=False,W5_complete=False,
        scope='Only TE-to-bank-exit portion; continuous factory lead extends into future full leg loom. No splice at exit.',
        assumptions=dict(output_insulation_OD_mm=2.4,static_radius_mm=10,delivered_OD_mm=None,delivered_copper_mm2=None),
        delivery_conditions='Check actual factory wire against TE0.32..0.82mm²; no folding/tinning/strand removal. Replace planning OD/radius if delivery requires it; preserve keyed factory plug.',
        source_sha256={ledger.relative_to(ROOT).as_posix():sha(ledger)}))
    owners,hashes,_=layout.current_owners()
    for folder,pattern in [('hardware/cad/studies/servo-fuse-bank-native-r5','*_WORLD.brep'),
                           ('hardware/electronics/full-cat/servo-fuse-bank-native-r5','*_DESIGN.brep'),
                           ('hardware/electronics/full-cat/servo-fuse-side-bank-r9','*_DESIGN.brep'),
                           ('hardware/electronics/full-cat/servo-fuse-cover-neighbors-r1','CoverBracket_*.brep')]:
        for f in (ROOT/folder).glob(pattern):
            if f.stem.startswith(('Panel_','Post_','Allen','NutTool')):continue
            owners[folder+'/'+f.stem]=Part.read(str(f));hashes[f.relative_to(ROOT).as_posix()]=sha(f)
    owners.pop('R49Deck');p=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-native-r5/Deck_candidate_UNSELECTED.brep'
    owners['CandidateDeck']=Part.read(str(p));hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    wires={};lengths=[]
    for row in rows:
        fuse=next(p.split('.')[0] for p in (row['a'],row['b']) if p.startswith('F_'))
        leg=fuse[2:4];i=int(fuse[4]);side=1 if leg.endswith('L') else -1
        cx=(-69 if leg.startswith('F') else 39)+26*(i-1)
        if leg=='FL' and i==2:cx-=3
        if leg=='FL' and i==3:cx+=6
        start=[cx,side*109,120-21.717-.381]
        path,end=output_path(A,Part,start,side)
        shape=path.makePipeShell([Part.Wire([Part.makeCircle(1.2,A.Vector(*start),A.Vector(0,0,-1))])],True,False)
        assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
        path.exportBrep(str(OUT/(row['id']+'_LOCAL_CENTERLINE.brep')))
        shape.exportBrep(str(OUT/(row['id']+'_LOCAL_DESIGN.brep')));wires[row['id']]=shape
        lengths.append(dict(id=row['id'],a=row['a'],b=row['b'],local_path_mm=path.Length,
            terminal_end_mm=start,bank_exit_mm=[end.x,end.y,end.z],whole_lead_cut_mm=None,full_moving_span_complete=False))
    hits=[];errors=[];pairs=0
    def check(n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            c=s.common(t)
            if c.Volume>1e-5:hits.append(dict(part=n,owner=m,hit_mm3=c.Volume,bounds_mm=[getattr(c.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
        except Exception as e:errors.append(dict(part=n,owner=m,error=str(e)))
    for n,s in wires.items():
        for m,t in owners.items():check(n,s,m,t)
    keys=list(wires)
    for i,n in enumerate(keys):
        for m in keys[i+1:]:check(n,wires[n],m,wires[m])
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='REJECTED' if hits or errors else 'LOCAL_OUTPUT_SPANS_CLEAR_RESTRAINTS_AND_LEGS_OPEN',
        selected=False,physical_pass=False,W5_complete=False,hits=hits,errors=errors,pairs=pairs,
        local_outputs=len(wires),lengths=lengths,source_sha256=hashes,script_sha256=sha(Path(__file__)),
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(hits=hits,errors=errors,local_outputs=len(wires))),flush=True)
if __name__=='__main__':main()
