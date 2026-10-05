"""Receive eight unchanged link clips against complete current cable bodies.

Reuse their existing P0/strap proof. Test ONLY changed grip interfaces, not
unchanged wire-wire pairs. All12 source bundles and49 body wires are included.
This is a static assembly pose, not qualification of motion or selection.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import w5_harness_passages_native as N
from servo_fuse_inputs_r1 import save, sha
from w5_exact_separation import separated

ROOT=N.ROOT; BASE=N.BASE; OUT=BASE/'w5-source-link-harness-interface-r1'
GRIPS=BASE/'w5-source-link-grips-r2'


def main():
    import FreeCAD as A, Part
    start=datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists()
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    proof=read(GRIPS/'checks.json'); bp=read(GRIPS/'blueprint.json')
    assert not proof['hits'] and not proof['errors'] and bp['print_quantity']==8
    pins={}; materials={}
    def pin(p):
        p=Path(p); pins[p.relative_to(ROOT).as_posix()]=sha(p);return p
    def load(p):return Part.read(str(pin(p)))
    pin(GRIPS/'checks.json'); pin(GRIPS/'blueprint.json')
    for rel,digest in {**proof['source_sha256'],**proof['files']}.items():
        assert sha(ROOT/rel)==digest,rel
    proposed=dict(zip(bp['roles'],load(GRIPS/'TWELVE_SOURCE_CLIPS_AND_STRAPS_PROPOSED_WORLD.brep').childShapes()))
    assert len(proposed)==40
    corridor=pin(BASE/'w5-leg-corridors-r3/intent.json')
    rows=read(corridor)['routes']
    bundles=load(corridor.parent/'CORRIDORS_WORLD.brep').childShapes()
    assert len(rows)==len(bundles)==12
    materials.update({'FactoryBundle/'+r['loom']:s for r,s in zip(rows,bundles)})
    central_path=pin(N.CENTRAL);central=read(central_path)
    for wire,row in central['routes'].items():materials[wire]=load(ROOT/row['geometry'])
    branch=pin(BASE/'w5-branch-joint-routes-r3/checks.json')
    for row in read(branch)['accepted']:
        wire=row['wire']
        if wire in materials:continue
        folders=('w5-branch-joint-routes-r3','w5-branch-joint-routes-r2','w5-branch-joint-routes-r1','w5-coupled-corridors-r3')
        p=next(BASE/f/(wire+'_WORLD.brep') for f in folders if (BASE/f/(wire+'_WORLD.brep')).exists())
        materials[wire]=load(p)
    assert sum(k.startswith('W') or k=='XA05' for k in materials)==37
    v_receipt=pin(BASE/'w5-leg-joint-source-layout-r1/checks.json')
    vrows=read(v_receipt)['routes']
    vbodies=load(v_receipt.parent/'FANOUTS_WORLD.brep').childShapes()
    assert len(vrows)==len(vbodies)==36
    for row,s in zip(vrows,vbodies):
        if row['role']=='V':materials[row['wire']]=s
    assert sum(k.startswith('W') or k=='XA05' for k in materials)==49
    native=pin(BASE/'w5-loom-fixed-native-r1/checks.json'); nr=read(native)
    assert nr['restored'] and nr['relocated_reopen']
    for owner in nr['editable_final_objects']:
        p=ROOT/'hardware/cad/studies/w5-loom-fixed-native-r1'/(owner+'_CANDIDATE_WORLD.brep')
        assert sha(p)==nr['files'][p.relative_to(ROOT).as_posix()]
        materials[owner]=load(p)
    for owner in ('SourceCarrier','SourceCover'):
        materials[owner]=load(ROOT/'hardware/cad/studies/w5-side-retention-native-r1'/(owner+'_CANDIDATE_WORLD.brep'))
    for owner in ('SourceWestHood',):
        materials[owner]=load(ROOT/'hardware/cad/studies/w5-harness-passages-qualified-r1'/(owner+'_CANDIDATE_WORLD.brep'))
    materials['SourceBankLeft']=load(ROOT/'hardware/cad/studies/w5-source-bank-passage-native-r1/BankLeft_WORLD.brep')
    OUT.mkdir(parents=True,exist_ok=True)
    hits=[];errors=[];pairs=0
    for label,s in proposed.items():
        for owner,t in materials.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            for a in s.Solids:
                for b in t.Solids:
                    if not a.BoundBox.intersect(b.BoundBox) or separated(a,b):continue
                    pairs+=1
                    try:
                        c=a.common(b)
                        if c.Volume>1e-6:hits.append(dict(part=label,owner=owner,mm3=c.Volume))
                    except Exception as ex:errors.append(dict(part=label,owner=owner,error=str(ex)))
        if label.endswith('CableHead'):
            save(OUT/'progress.json',dict(last_part=label,pairs=pairs,hits=hits,errors=errors))
            print('LINK_HARNESS',label,pairs,len(hits),len(errors),flush=True)
    finish=datetime.now(timezone.utc);pin(Path(__file__))
    save(OUT/'checks.json',dict(status='EIGHT_LINK_GRIPS_CURRENT_HARNESS_STATIC_CLEAR' if not hits and not errors else 'EIGHT_LINK_GRIPS_CURRENT_HARNESS_REJECTED',
        proposed_materials=len(proposed),factory_bundles=12,current_body_wires=49,current_native_fixed_parts=10,
        reused_P0_receipt=(GRIPS/'checks.json').relative_to(ROOT).as_posix(),
        pairs=pairs,hits=hits,errors=errors,wire_paths_unchanged=True,P0_unchanged=True,
        whole_other_fixture_scope_pending=True,whole_motion_and_mounting_pending=True,
        selected=False,native_complete=False,W1_complete=False,W5_complete=False,physical_pass=False,
        source_sha256=pins,started_utc=start.isoformat(),finished_utc=finish.isoformat(),
        worker_wall_seconds=(finish-start).total_seconds()))
    print('LINK_HARNESS_RECEIVED',pairs,len(hits),len(errors),flush=True)


if __name__=='__main__':main()
