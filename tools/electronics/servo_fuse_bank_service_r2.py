"""Changed vertical clip access plus continuous rigid TE parking corridors.

Do not repeat unchanged module-lift checks or waive failed WAGO access.
Flexible full-leg lead deformation remains W5, not this rigid-end proof.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-service-r2'

def main():
    import FreeCAD as A
    import Part
    import servo_fuse_side_bank_r10 as layout
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'checks.json').exists()
    p=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-service-r1/checks.json'
    parent=json.loads(p.read_text(encoding='utf-8'))
    assert not parent['errors'] and not any(r['phase'].startswith(('module_lift','bank_fastener')) for r in parent['hits'])
    owners,hashes,_=layout.current_owners();hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    def load(p):hashes[p.relative_to(ROOT).as_posix()]=sha(p);return Part.read(str(p))
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    for n in list(owners):
        if any(f in n for f in ('/servo-fuse-bank-restraints-r2/','/servo-fuse-bank-restraints-fit-r2/')):del owners[n]
    owners['R49Deck']=load(ROOT/'hardware/cad/studies/servo-fuse-deck-native-r1/Deck_WORLD.brep')
    for p in (ROOT/'hardware/cad/studies/servo-fuse-bank-clip-access-r1').glob('*_WORLD.brep'):owners[p.stem]=load(p)
    p=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-clip-access-r1/checks.json'
    clip=json.loads(p.read_text(encoding='utf-8'));hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    hits=[];errors=[];pairs=0
    def check(phase,n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            c=s.common(t)
            if c.Volume>1e-5:hits.append(dict(phase=phase,part=n,owner=m,hit_mm3=c.Volume))
        except Exception as e:errors.append(dict(phase=phase,part=n,owner=m,error=str(e)))
    print('VERTICAL_CLIP_TOOLS',flush=True)
    for p in (ROOT/'hardware/electronics/full-cat/servo-fuse-bank-clip-access-r1').glob('*_TOOL_RESERVE.brep'):
        s=load(p)
        for n,t in owners.items():check('vertical_clip_tool',p.stem,s,n,t)
    terminal_dir=ROOT/'hardware/electronics/full-cat/servo-fuse-side-bank-r11'
    terminals={p.stem:load(p) for p in terminal_dir.glob('F_*_DESIGN.brep') if p.stem.endswith(('IN_DESIGN','OUT_DESIGN'))}
    assert len(terminals)==24
    parked={};paths=[]
    print('RIGID_END_PARKING',flush=True)
    # INPUT pigtails are first removed from WAGO cages and freed from all ties.
    # Remove them, do not stretch a connected short AWG12 route by38mm.
    for role,shift in [('IN',38),('OUT',36)]:
        for n,s in terminals.items():
            if not n.endswith('_'+role+'_DESIGN'):continue
            b=s.BoundBox;side=1 if b.Center.y>0 else -1;dy=side*shift
            bounds=[b.XMin,min(b.YMin,b.YMin+dy),b.ZMin,b.XMax,max(b.YMax,b.YMax+dy),b.ZMax]
            swept=box(bounds)
            for m,t in owners.items():
                # Wire insulation is released and allowed to deform, not a
                # rigid obstacle waived while tied; do not certify its path.
                if '/servo-fuse-bank-outputs-r1/' in m:continue
                check('rigid_end_park_'+role,n,swept,m,t)
            for m,t in terminals.items():
                if m==n:continue
                check('rigid_end_park_'+role,n,swept,m,parked.get(m,t))
            q=s.copy();q.translate(A.Vector(0,dy,0));parked[n]=q
            q.exportBrep(str(OUT/(n+'_PARKED.brep')));swept.exportBrep(str(OUT/(n+'_SWEEP.brep')))
            paths.append(dict(end=n,delta_y_mm=dy,continuous_rectangular_sweep=True,
                final_bounds_mm=[getattr(q.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
    assert len(parked)==24
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='CHANGED_SERVICE_CONFLICTS' if hits or errors else 'VERTICAL_TOOLS_AND_RIGID_END_PARKING_CLEAR_WAGO_OPEN',
        selected=False,W5_complete=False,physical_pass=False,hits=hits,errors=errors,pairs=pairs,
        clip_tools=24,parked_ends=24,parking=paths,module_sampled_clearance_inherited=True,
        inherited_lifts_mm=parent['sampled_lifts_mm'],inherited_basis='New bank only subtracts24 tool slots; cover and installed body unchanged. No full lift recompute.',
        clip_actuation_measured=False,flexible_full_leg_service_motion_qualified=False,
        sequence=['Disconnect/remove battery; release head JR/ties.','Release all12 input ends at P-WAGO before moving pigtails; WAGO access remains unresolved.',
            'Remove ATO. Nominal0.8x3mm tool enters24 new vertical slots and presses the depicted clips; coupon must confirm latch action.',
            'Raise each holder10mm; cut all24 bank strain ties. Remove the released AWG12 input pigtails outward38mm, then move output TE ends outward36mm.',
            'Do not force a TE downward through its backer. Secure loose ends outside the bank before lifting the disconnected bank+cover.'],
        open=['P-WAGO lever approach still conflicts in service-r1; do not label service complete.','Four parent factory feeds and local restraint.',
              'Full moving leg spans must retain sufficient free length for this parked-end position; no actual flexible lead deformation proved here.'],
        source_sha256=hashes,script_sha256=sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(hits=hits,errors=errors,pairs=pairs)),flush=True)
if __name__=='__main__':main()
