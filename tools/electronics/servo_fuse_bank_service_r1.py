"""One service sequence: release ends first, remove disconnected bank+cover.

Tool/cage/latch reserves are project allowances, not supplier motion models.
Do not turn the former rejected independent cover lift into a pass.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics')]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-service-r1'
def main():
    import FreeCAD as A
    import Part
    import servo_fuse_side_bank_r10 as layout
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'checks.json').exists()
    owners,hashes,_=layout.current_owners()
    def load(p):hashes[p.relative_to(ROOT).as_posix()]=sha(p);return Part.read(str(p))
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    coverkey='hardware/cad/studies/head-yaw-end-restraints-r1/CoverYawEndSeat.brep'
    cover=owners.pop(coverkey)
    owners['R49Deck']=load(ROOT/'hardware/cad/studies/servo-fuse-deck-native-r1/Deck_WORLD.brep')
    omitted=[]
    # These are explicitly released and parked before the module moves, not
    # obstacles waived while connected. All other current body owners remain.
    for n in list(owners):
        if any(f in n for f in ('/servo-fuse-bank-restraints-r2/','/servo-fuse-bank-outputs-r1/','/servo-fuse-bank-restraints-fit-r2/')):
            omitted.append(n);del owners[n]
    module={'Cover':cover}
    for p in (ROOT/'hardware/cad/studies/servo-fuse-bank-restraints-r3').glob('*_WORLD.brep'):module[p.stem]=load(p)
    for p in (ROOT/'hardware/electronics/full-cat/servo-fuse-side-bank-r11').glob('F_*_DESIGN.brep'):
        if p.stem.count('_')==2:module[p.stem]=load(p)
    assert len(module)==15
    hits=[];errors=[];pairs=0;clearances=[]
    def check(phase,n,s,m,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            c=s.common(t)
            if c.Volume>1e-5:hits.append(dict(phase=phase,part=n,owner=m,hit_mm3=c.Volume,
                bounds_mm=[getattr(c.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
        except Exception as e:errors.append(dict(phase=phase,part=n,owner=m,error=str(e)))
    for p in (ROOT/'hardware/electronics/full-cat/servo-fuse-bank-native-r5').glob('*_DESIGN.brep'):
        if not p.stem.startswith(('Allen','NutTool')):continue
        probe=load(p)
        for m,t in {**owners,'Cover':cover,**{n:s for n,s in module.items() if n.endswith('_WORLD')}}.items():check('bank_fastener_tool',p.stem,probe,m,t)
    p=ROOT/'hardware/electronics/full-cat/servo-fuse-wago-map-r1/interface.json'
    hashes[p.relative_to(ROOT).as_posix()]=sha(p);mapping=json.loads(p.read_text(encoding='utf-8'))
    for block in mapping['blocks']:
        for port in block['ports']:
            x,y,z=port['entry_mm'];cy=block['center_mm'][1]
            # Small-tool access above one cage. This is NOT the exact hinge
            # sweep of a WAGO lever or a promised finger space.
            probe=box([x-2.5,cy-9.5,118,x+2.5,cy+9.5,133])
            for m,t in {**owners,**module}.items():
                if m==block['id']+'_design':continue
                check('P_WAGO_top_access',block['id']+'.'+str(port['project_slot']),probe,m,t)
    p=ROOT/'hardware/electronics/full-cat/servo-fuse-side-bank-r11/checks.json'
    hashes[p.relative_to(ROOT).as_posix()]=sha(p);routes=json.loads(p.read_text(encoding='utf-8'))
    for n,row in routes['placements'].items():
        x,cy,z=row['holder'];side=1 if cy>0 else -1
        for face in (-1,1):
            y=cy+face*14.25
            lo,hi=sorted((y+face*.5,y+face*16))
            probe=box([x-1.5,lo,128,x+1.5,hi,143])
            # The figure shows opposed clips but no press-point dimensions;
            # test a broad corridor, retain that assumption for the coupon.
            for m,t in {**owners,**{n:s for n,s in module.items() if n=='Cover' or n.endswith('_WORLD')}}.items():check('provisional_clip_access',n+':'+str(face),probe,m,t)
    for lift in (0,10,30,60,100):
        for n,s in module.items():
            q=s.copy();q.translate(A.Vector(0,0,lift))
            for m,t in owners.items():check('module_lift_'+str(lift),n,q,m,t)
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='SERVICE_SEQUENCE_CONFLICTS' if hits or errors else 'SAMPLED_DISCONNECTED_MODULE_CLEAR_ACCESS_PROVISIONAL',
        selected=False,W5_complete=False,physical_pass=False,hits=hits,errors=errors,pairs=pairs,
        module_parts=list(module),omitted_after_release_and_parking=omitted,sampled_lifts_mm=[0,10,30,60,100],
        continuous_module_withdrawal_qualified=False,physical_latch_or_lever_verified=False,
        sequence=['Disconnect/remove battery; do not energize.','Release head JR and both existing cover ties.',
            'Remove ATO, unclip and raise each holder10mm while TE ends remain stationary. Nominal clip actuation must fit the coupon.',
            'Cut all24 bank strain ties. After blades are free, park all24 TE ends away from the bank. Do not force an input TE down through a backer.',
            'Release bank M2 bolts/nuts and four cover mounts. Do not attempt independent cover lift.',
            'Lift disconnected cover+two bare bank parts with loose holders together. This result does not qualify connected-wire motion.'],
        open='Four parent feeds/strain relief and actual end parking remain open. Access boxes are provisional, not exact supplier lever/clip motion.',
        source_sha256=hashes,script_sha256=sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(hits=hits,errors=errors,pairs=pairs)),flush=True)
if __name__=='__main__':main()
