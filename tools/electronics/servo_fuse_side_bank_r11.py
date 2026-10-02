"""Correct only R10/W046's XT60 witness, retain eleven checked input routes.

RL1 receives8mm straight grip instead of10; outside turnaround rises2mm.
No change to fuses/terminal datums, WAGO entry fan or nominal bend radius.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math,sys,shutil
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-side-bank-r11'

def main():
    import FreeCAD as A
    import Part
    import servo_fuse_side_bank_r10 as prior
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'checks.json').exists():
        rejected=json.loads((OUT/'checks.json').read_text(encoding='utf-8'))
        assert len(rejected['hits'])==1 and rejected['hits'][0]['owner']=='R49Deck' and not rejected['errors']
        assert not (OUT/'checks-before-candidate-deck.json').exists()
        shutil.copy2(OUT/'checks.json',OUT/'checks-before-candidate-deck.json')
    old_path=prior.OUT/'checks.json';old=json.loads(old_path.read_text(encoding='utf-8'))
    assert len(old['hits'])==1 and old['hits'][0]['part']=='W046'
    assert old['hits'][0]['owner']=='Source/XT60_robot_body_DESIGN' and not old['errors'] and not old['cover_hits_not_waived']
    assert old['input_routes']==12 and old['terminal_reserves']==24
    assert sha(ROOT/'tools/electronics/servo_fuse_side_bank_r10.py')==old['script_sha256']
    for rel,h in old['source_sha256'].items():assert sha(ROOT/rel)==h,rel
    owners,hashes,_=prior.current_owners()
    spec=old['placements']['W046'];start=spec['start'];end=spec['end'];raised_end=[end[0],end[1],end[2]+2]
    # R10 tests the terminal height before its 10mm lower turnaround. With
    # the raised RL1 endpoint that assertion must test the descent target.
    route_source=(ROOT/'tools/electronics/servo_fuse_side_bank_r8.py').read_text(encoding='utf-8')
    route_source=route_source[route_source.index('def input_path('):route_source.index('\ndef current_owners(')]
    route_source=route_source.replace('assert p.z>end[2]','assert p.z>end[2]-10')
    route_source=route_source.replace('line(A.Vector(p.x,p.y,end[2]));arc(dz,u,math.pi/2)',
        'line(A.Vector(p.x,p.y,end[2]-10));arc(dz,u,math.pi/2)')
    route_source=route_source.replace('line(A.Vector(p.x,side*stop,p.z));arc(u,up,math.pi/2)',
        'line(A.Vector(p.x,side*stop,p.z));arc(u,up,math.pi/2);line(A.Vector(*end))')
    route_ns={'math':math};exec(route_source,route_ns)
    path=route_ns['input_path'](A,Part,start,raised_end,1,lift=-5,delay=9)
    edges=path.Edges[:-1]+[Part.makeLine(path.Edges[-1].valueAt(path.Edges[-1].FirstParameter),A.Vector(*end))]
    assert abs(edges[-1].Length-8)<1e-7
    for a,b in zip(edges,edges[1:]):
        assert (a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length<1e-7
        assert (a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length<1e-7
    path=Part.Wire(edges)
    def pipe(p,r):return p.makePipeShell([Part.Wire([Part.makeCircle(r,A.Vector(*start),A.Vector(0,1,0))])],True,False)
    changed=pipe(path,1.55);assert changed.isValid() and len(changed.Solids)==1 and not changed.check(True)
    source_deck=owners['R49Deck'];clearance=pipe(path,1.95)
    old_line=Part.Wire(Part.read(str(prior.OUT/'W046_CENTERLINE.brep')).Edges);old_clearance=pipe(old_line,1.95)
    delta=old_clearance.cut(clearance).fuse(clearance.cut(old_clearance))
    assert delta.common(source_deck).Volume<1e-5,'Portal changed: rebuild actual Deck instead of copying'
    # Test the inherited full-through portals, not the uncut source plate.
    candidate=prior.OUT/'Deck_candidate_UNSELECTED.brep'
    owners['R49Deck']=Part.read(str(candidate));hashes[candidate.relative_to(ROOT).as_posix()]=sha(candidate)
    for p in prior.OUT.glob('*.brep'):
        if p.name in ('W046_DESIGN.brep','W046_CENTERLINE.brep'):continue
        shutil.copy2(p,OUT/p.name);hashes[p.relative_to(ROOT).as_posix()]=sha(p)
        if p.stem!='Deck_candidate_UNSELECTED' and not p.stem.startswith(('Post_','Panel_')):
            owners['BankR10/'+p.stem]=Part.read(str(p))
    changed.exportBrep(str(OUT/'W046_DESIGN.brep'));path.exportBrep(str(OUT/'W046_CENTERLINE.brep'))
    hits=[];errors=[];pairs=0
    for n,s in owners.items():
        if not changed.BoundBox.intersect(s.BoundBox):continue
        pairs+=1
        try:
            c=changed.common(s)
            if c.Volume>1e-5:hits.append(dict(part='W046',owner=n,hit_mm3=c.Volume,bounds_mm=[getattr(c.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
        except Exception as e:errors.append(dict(part='W046',owner=n,error=str(e)))
    lengths=[dict(r,straight_grip_mm=8 if r['id']=='W046' else 10) for r in old['lengths']]
    row=next(r for r in lengths if r['id']=='W046');row['path_mm']=path.Length
    row['nominal_unselected_blank_mm']=math.ceil((path.Length+14+8.30+10)/10)*10
    for r in lengths:assert r['actual_cut_mm'] is None
    hashes[old_path.relative_to(ROOT).as_posix()]=sha(old_path)
    endtime=datetime.now(timezone.utc)
    report=dict(old)
    report.update(status='INTERNAL_INPUTS_CLEAR_NATIVE_GRIPS_READY' if not hits and not errors else 'INTERNAL_CONFLICTS',
        hits=hits,errors=errors,lengths=lengths,planned_required_blank_mm=sum(r['nominal_unselected_blank_mm'] for r in lengths),
        prospective_added_panels=0,prospective_print_panels_mm=None,cover_adaptation_not_completed=True,
        source_sha256=hashes,script_sha256=sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=endtime.isoformat(),worker_wall_seconds=(endtime-begin).total_seconds(),
        checks_scope='Only changed W046 repeated against current owners, eleven copied routes and all ends. R10 other eleven checks inherited without rerun.',
        inherited_pairs=old['pairs'],changed_pairs=pairs,previous_contact=old['hits'][0],
        straight_grip_minimum_mm=8,unchanged_deck_portals_proven=True)
    save(OUT/'checks.json',report)
    print(json.dumps(dict(hits=hits,errors=errors,changed_pairs=pairs,blanks=report['planned_required_blank_mm'])),flush=True)
if __name__=='__main__':main()
