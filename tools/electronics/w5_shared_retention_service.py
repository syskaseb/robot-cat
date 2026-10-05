"""Check current bank withdrawal against all new integral retention material.

Receive unchanged source-family/R47 checks, rather than repeating them. Read
only the small saved new roots and grooves. No whole Deck Boolean/recompute.
Source/leg/central cables are explicitly released before bank withdrawal;
their flexible removal is a phase2 fitting operation, not a rigid simulation.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys, re
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/cad'))
from check_main_p0_placement import SavedShapes,prop
from servo_fuse_inputs_r1 import sha,save
BASE=ROOT/'hardware/electronics/full-cat';OUT=BASE/'w5-shared-retention-service-r1'

def main():
    import FreeCAD as A, Part
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);reader=SavedShapes();pins={}
    def read(p):pins[p.relative_to(ROOT).as_posix()]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    def load(p):pins[p.relative_to(ROOT).as_posix()]=sha(p);return Part.read(str(p))
    old=read(BASE/'w5-source-family-service-r2/assembly.json')
    frames=read(BASE/'w5-common-service-delta-r1/checks.json')
    assert not old['hits'] and not old['errors'] and not frames['hits'] and not frames['errors']
    for proof in (old,frames):
        for rel,h in proof['source_sha256'].items():assert sha(ROOT/rel)==h,rel
    side=ROOT/'hardware/cad/studies/w5-side-retention-native-r1/WholeHarnessSideRetention.FCStd'
    central=ROOT/'hardware/cad/studies/w5-central-retention-native-r1/WholeHarnessCentralRetention.FCStd'
    sobjects=reader.doc(side);cobjects=reader.doc(central)
    bp=read(BASE/'w5-side-retention-received-r2/native-blueprint.json')
    fixed={}
    for name in bp['raw_boxes']:
        obj=name+'Slotted' if name+'Slotted' in sobjects else name+'Raw'
        fixed['Side/'+name]=reader.shape(side,obj)
    tools=reader.shape(central,'InsulationAndTieTools')
    roots=prop(cobjects['DeckAndIntegralRetentionRoots'],'Shapes').findall('.//Link')
    for r in roots:
        name=r.get('value')
        if name=='ReceivedHarnessDeck':continue
        # Small root-only cut is the exact added material, without the old
        # large Deck. Holes in shared parent can only remove extra material.
        fixed['Central/'+name]=reader.shape(central,name).cut(tools)
    # Remote seats lie below the bank floor but are included explicitly.
    remote=ROOT/'hardware/cad/studies/w5-remote-end-native-r1/RemoteEndRetention.FCStd'
    reader.doc(remote)
    for tag in ('BAT','AUX'):
        fixed['Remote/'+tag]=reader.shape(remote,tag+'SeatBlank').cut(reader.shape(remote,tag+'LocalTools'))
    module=dict(BankRight=load(ROOT/'hardware/cad/studies/servo-fuse-bank-inner-feed-service-r1/BankRight_WORLD.brep'),
        BankLeft=load(ROOT/'hardware/cad/studies/w5-source-bank-passage-native-r1/BankLeft_WORLD.brep'),
        Cover=load(ROOT/'hardware/cad/studies/w5-side-retention-native-r1/SourceCover_CANDIDATE_WORLD.brep'))
    # New positive cover bridges must not inherit the old cover lift proof.
    additions={k:reader.shape(side,k) for k in bp['cover_bridges']}
    unchanged=read(BASE/'w5-installed-r52/owners.json')
    pieces=load(BASE/'w5-installed-r52'/unchanged['geometry']).childShapes()
    assert len(pieces)==len(unchanged['rows'])
    assert sha(BASE/'w5-installed-r52'/unchanged['geometry'])==unchanged['geometry_sha256']
    owners={r['key']:pieces[r['child_index']] for r in unchanged['rows']}
    hits=[];errors=[];pairs=0
    def check(dz,name,s,key,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        for a in s.Solids:
            for b in t.Solids:
                if not a.BoundBox.intersect(b.BoundBox):continue
                pairs+=1
                try:
                    c=a.common(b)
                    if c.Volume>1e-5:
                        p=OUT/('HIT_'+str(len(hits)+1)+'.brep');c.exportBrep(str(p))
                        hits.append(dict(lift_mm=dz,moving=name,fixed=key,mm3=c.Volume,witness=p.relative_to(ROOT).as_posix()))
                except Exception as e:errors.append(dict(lift_mm=dz,moving=name,fixed=key,error=str(e)))
    # Only new positive bridges are checked against unchanged fixed rigid
    # owners. Explicit removal of old bank/cover/holders/released wire/tie
    # roles uses the received release census, not collision-based exclusion.
    census=read(BASE/'servo-fuse-bank-fixed-rr-lift-r22/owner-census.json')
    released=set(census['removed'])|set(census['parked'])|set(census['released_inputs'])
    old_fixed={k:s for k,s in owners.items() if k not in released and k not in ('Cover','BankLeft','BankRight')}
    # Neither earlier installed wires nor tie envelopes are rigid obstacles
    # after the explicitly specified full harness/source release.
    wire_roles=[]
    for k in list(old_fixed):
        tail=Path(k).stem
        # Exact wire-shaped naming roles only. WConnector and WAGO/MTA
        # purchased blocks are retained, even after their ends are released.
        wire=bool(re.match(r'^(?:W\d{3}|X[ABLSP]\d{2}|PI5V|PI_GND|USB_BUS)(?:$|_(?:\d|bare|insulated|wire|extension|factory|Bare|Sleeve|Solder))',tail))
        wire=wire or bool(re.match(r'^W\d{3}/(?:factory|extension)$',k))
        if wire or any(t in k.lower() for t in ('tie','strap')):
            wire_roles.append(k);del old_fixed[k]
    sampled=[];clear=[]
    for dz in (2,5,10,30,60,100):
        sampled.append(dz)
        for name,s in module.items():
            q=s.copy();q.translate(A.Vector(0,0,dz))
            for key,t in fixed.items():check(dz,name,q,key,t)
        for name,s in additions.items():
            q=s.copy();q.translate(A.Vector(0,0,dz))
            for key,t in {**old_fixed,**fixed}.items():check(dz,'CoverBridge/'+name,q,key,t)
        save(OUT/'progress.json',dict(lift_mm=dz,pairs=pairs,hits=len(hits),errors=len(errors),updated_utc=datetime.now(timezone.utc).isoformat()))
        print('SHARED_RETENTION_SERVICE',dz,pairs,len(hits),len(errors),flush=True)
        if hits or errors:break
        clear.append(dz)
    finish=datetime.now(timezone.utc);pins[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    save(OUT/'checks.json',dict(status='CURRENT_RETENTION_SHARED_BANK_RELEASE_CONFLICT' if hits or errors else 'CURRENT_RETENTION_SHARED_BANK_RELEASE_SAMPLES_CLEAR',
        fixed_new_roots=len(fixed),new_cover_bridges=len(additions),requested_lifts_mm=[2,5,10,30,60,100],sampled_lifts_mm=sampled,completed_clear_lifts_mm=clear,
        inherited_source_recipe=old['removal'],explicit_additional_release=[
            'Battery disconnected. Remove hoods; disconnect the12servo plugs and body D/G/V ends using their received terminal recipes.',
            'Cut12factory split and12source insulation ties; remove the12continuous factory looms rather than attempting a wired bank lift.',
            'Release central/side junction ends and their insulation ties before bank lift; preserve labels and fixed printed roots.',
            'Apply existing source-family/R47 ring/holder/24TE-end release and bank+cover fastener order. Never independently lift Cover.',
            'Reverse bench-first assembly; use replacement cut ties. Physical flexible threading/tool/lever fit remains phase2.'],
        released_wire_or_tie_owner_roles=wire_roles,physical_flexible_removal_simulated=False,
        no_parts_removed_due_to_detected_collision=True,continuous_sweep_verified=False,
        hits=hits,errors=errors,pairs=pairs,selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        source_sha256={**reader.hashes,**pins},files={p.relative_to(ROOT).as_posix():sha(p) for p in OUT.glob('HIT_*.brep')},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))

if __name__=='__main__':main()
