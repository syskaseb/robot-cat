"""Twelve integral input grips, preserving R2 output seats and four mounts.

Build and check the changed interface together. This unselected construction
does not qualify complete W5, removal or physical insulation/tie fit.
"""
from pathlib import Path
from datetime import datetime, timezone
import sys, json, math, shutil, tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/cad'),str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save, sha
CAD=ROOT/'hardware/cad/studies/servo-fuse-bank-restraints-r3'
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-restraints-r3'

def main():
    import FreeCAD as A
    import Part, MeshPart
    import servo_fuse_side_bank_r10 as layout
    from open_deck_p0_plate import rect
    begin=datetime.now(timezone.utc)
    CAD.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    src=ROOT/'hardware/cad/studies/servo-fuse-bank-restraints-r2/ServoFuseBank.FCStd'
    input_dir=ROOT/'hardware/electronics/full-cat/servo-fuse-side-bank-r11'
    meta=input_dir/'checks.json';inputs=json.loads(meta.read_text(encoding='utf-8'))
    assert not inputs['hits'] and not inputs['errors'] and inputs['straight_grip_minimum_mm']==8
    hashes={p.relative_to(ROOT).as_posix():sha(p) for p in (src,meta)}
    d=A.openDocument(str(src));docname=d.Name;sketches=[];parts={};original={};raw_parts={};ties={};slots=[];grips=[]
    def block(n,b):
        sk=d.addObject('Sketcher::SketchObject',n+'Profile');sk.Placement.Base.z=b[2]
        rect(sk,b[0],b[1],b[3]-b[0],b[4]-b[1]);sketches.append(sk)
        t=d.addObject('Part::Extrusion',n);t.Base=sk;t.Dir=A.Vector(0,0,b[5]-b[2]);t.Solid=True
        return t
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    def mirrored(x0,x1,y0,y1,z0,z1,side):
        lo,hi=sorted((side*y0,side*y1));return [x0,lo,z0,x1,hi,z1]
    try:
        par=d.addObject('App::VarSet','InputSeatParameters')
        par.addProperty('App::PropertyLength','GrooveRadius');par.GrooveRadius=1.7
        finals=[]
        for side in (-1,1):
            tag='Right' if side<0 else 'Left';parent=d.getObject(tag+'OutputSeatFinished')
            assert parent and parent.Shape.isValid();original[tag]=parent.Shape.copy()
            stock=[parent];cutters=[]
            for row in inputs['lengths']:
                n=row['id'];x,y,z=inputs['placements'][n]['end']
                if side*y<0:continue
                g=row['straight_grip_mm'];low=z-g;mid=z-g/2
                stock.append(block(n+'InputBacker',mirrored(x-6,x+6,124.3,126.3,low,z,side)))
                stock.append(block(n+'InputRib',mirrored(x+10,x+12,125.5,127.5,low,144.7,side)))
                stock.append(block(n+'InputBridge',mirrored(x-6,x+12,124.3,127.5,low,low+2,side)))
                groove=d.addObject('Part::Cylinder',n+'InputGroove');groove.Radius=1.7;groove.Height=g+.2
                groove.setExpression('Radius','InputSeatParameters.GrooveRadius')
                groove.Placement.Base=A.Vector(x,y,low-.1);cutters.append(groove)
                for i,dx in enumerate((-3.5,3.5)):
                    b=mirrored(x+dx-1,x+dx+1,124.1,127.7,mid-1.5,mid+1.5,side)
                    cutters.append(block(n+'InputTieSlot'+str(i),b));slots.append(dict(id=n,box_mm=b))
                bands=[box(mirrored(x+dx-.6,x+dx+.6,120.25,127.5,mid-1.25,mid+1.25,side)) for dx in (-3.5,3.5)]
                bands += [box(mirrored(x-4.1,x+4.1,120.25,121.45,mid-1.25,mid+1.25,side)),
                          box(mirrored(x-4.1,x+4.1,126.3,127.5,mid-1.25,mid+1.25,side))]
                ties[n+'_INPUT_TIE_DESIGN']=Part.makeCompound(bands)
                ties[n+'_INPUT_TIE_HEAD_RESERVE']=box(mirrored(x-10.5,x-4.5,126.3,130.3,mid-2.5,mid+2.5,side))
                grips.append(dict(id=n,center_mm=[x,y,mid],straight_grip_mm=g,tie='Existing T18I, insulation only',head_envelope_mm=[6,4,5]))
            raw=d.addObject('Part::MultiFuse',tag+'InputSeatStock');raw.Shapes=stock;raw.Refine=False
            holes=d.addObject('Part::MultiFuse',tag+'InputSeatTools');holes.Shapes=cutters
            f=d.addObject('Part::Cut',tag+'InputSeatFinished');f.Base=raw;f.Tool=holes;f.Refine=True;finals.append(f)
        d.recompute()
        for f in finals:assert f.Shape.isValid() and len(f.Shape.Solids)==1 and not f.Shape.check(True),f.Name
        assert len(grips)==12 and len(slots)==24
        assert all(s.solve()==0 and s.FullyConstrained for s in sketches)
        before=[f.Shape.Volume for f in finals];par.GrooveRadius=1.8;d.recompute();probe=[f.Shape.Volume for f in finals]
        assert all(a>b for a,b in zip(before,probe));par.GrooveRadius=1.7;d.recompute()
        assert all(abs(f.Shape.Volume-v)<1e-5 for f,v in zip(finals,before))
        dest=CAD/'ServoFuseBank.FCStd';d.saveAs(str(dest));parts={f.Name:f.Shape.copy() for f in finals}
        raw_parts={tag:d.getObject(tag+'InputSeatStock').Shape.copy() for tag in ('Left','Right')}
    finally:A.closeDocument(docname)
    with tempfile.TemporaryDirectory(prefix='robot-cat-bank-inputs-') as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);re=A.openDocument(str(q))
        try:
            re.recompute()
            assert all(re.getObject(n).Shape.isValid() and abs(re.getObject(n).Shape.Volume-s.Volume)<1e-5 for n,s in parts.items())
        finally:A.closeDocument(re.Name)
    dims={};added={}
    for n,s in parts.items():
        s.exportBrep(str(CAD/(n+'_WORLD.brep')))
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1;mesh.rotate(math.pi,0,0);b=mesh.BoundBox
        dims[n]=[b.XLength,b.YLength,b.ZLength];assert b.XLength+10<256 and b.YLength+10<256 and b.ZLength<256
        mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/(n+'_x1.stl')))
        tag='Right' if n.startswith('Right') else 'Left';added[n]=s.cut(original[tag])
        added[n].exportBrep(str(OUT/(n+'_ADDED.brep')))
    for n,s in ties.items():s.exportBrep(str(OUT/(n+'.brep')))
    owners,h,_=layout.current_owners();hashes.update(h)
    # R10 uses old banks; check against changed final banks separately below.
    for n in list(owners):
        if '/servo-fuse-bank-restraints-r2/' in n:del owners[n]
    for p in input_dir.glob('*_DESIGN.brep'):
        if p.stem.startswith(('Post_','Panel_')):continue
        hashes[p.relative_to(ROOT).as_posix()]=sha(p);owners['InputR11/'+p.stem]=Part.read(str(p))
    target={**added,**ties};hits=[];errors=[];pairs=0
    def check(n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            c=s.common(t)
            if c.Volume>1e-5:hits.append(dict(part=n,owner=m,hit_mm3=c.Volume,bounds_mm=[getattr(c.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
        except Exception as e:errors.append(dict(part=n,owner=m,error=str(e)))
    for n,s in target.items():
        for m,t in owners.items():check(n,s,m,t)
        if n in ties:
            for m,t in parts.items():check(n,s,m,t)
    # Restraints on insulation are permitted surface contact, not overlapping
    # tube/terminal volumes. Geometry reserves never justify a physical PASS.
    for i,(n,s) in enumerate(ties.items()):
        for m,t in list(ties.items())[i+1:]:check(n,s,m,t)
    slot_checks=[]
    for spec in slots:
        b=spec['box_mm'];p=box([b[0]+.1,b[1],b[2]+.1,b[3]-.1,b[4],b[5]-.1])
        # Original R2 has no pad; evaluate the uncut stock, not air.
        tag='Right' if inputs['placements'][spec['id']]['end'][1]<0 else 'Left'
        stock_v=p.common(raw_parts[tag]).Volume
        after_v=sum(p.common(t).Volume for t in parts.values())
        assert stock_v>1 and after_v<1e-5
        slot_checks.append(dict(id=spec['id'],stock_mm3=stock_v,finished_mm3=after_v,full_through=True))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='INPUT_GRIPS_CLEAR_REMOVAL_PORTS_STOCK_OPEN' if not hits and not errors else 'INPUT_GRIPS_CONFLICTS',
        selected=False,physical_pass=False,W5_complete=False,native=dest.relative_to(ROOT).as_posix(),
        strict_BOP_errors=0,closed_STLs=True,relocated_reopen=True,new_constrained_sketches=len(sketches),
        parameter_volumes=[before,probe,before],dimensions_mm=dims,grips=grips,slots=slot_checks,
        bank_input_ties=12,bank_output_ties=12,bank_total_ties=24,added_print_count=0,
        delivered_tie_head_verified=False,print_policy='Roof down; local bridges need support evaluation in phase2. No slicer qualification.',
        hits=hits,errors=errors,pairs=pairs,source_sha256=hashes,script_sha256=sha(Path(__file__)),
        remaining='Five-port WAGO mapping/feeds, actual removal, native Deck, stock and selection. Full moving leg spans remain W5.',
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(hits=hits,errors=errors,pairs=pairs,dimensions_mm=dims)),flush=True)
if __name__=='__main__':main()
