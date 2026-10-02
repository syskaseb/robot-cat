"""Select one Deck replacement; no new routes, jobs or purchase quantities."""
import copy,json,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/cad'))
from release_check import verify,sha256
PARENT=ROOT/'hardware/manufacturing/one-batch-prototype-r40'
BATCH=ROOT/'hardware/manufacturing/one-batch-prototype-r41'
OUT=ROOT/'hardware/electronics/full-cat/g1-exit-restraints-finish-r1'
CAD=ROOT/'hardware/cad/studies/g1-exit-restraints-finish-r1'
START='2026-10-02T04:30:06+00:00'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

def payload(selection,quantities,checks):
    assert checks['status']=='G1_INDEPENDENT_RESTRAINTS_COMPLETE' and not checks['hits'] and checks['mesh_export_complete']
    s,q=copy.deepcopy(selection),copy.deepcopy(quantities)
    recipe=(OUT/'interface.json').relative_to(ROOT).as_posix()
    row=next(r for r in s['prints'] if r['identity']=='electronics:DeckP10-cover-mount')
    row.update(stl=(CAD/'Deck_x1.stl').relative_to(ROOT).as_posix(),sha256=sha256(CAD/'Deck_x1.stl'),
        native=(CAD/'DeckG1ExitRestraints.FCStd').relative_to(ROOT).as_posix(),recipe=recipe,
        orientation='Lower Deck base on bed, +Zup. Retained DATA/W061/W060 features except the two superseded G1 cradles.',
        supports='Inspect all retained raised grooves and beams in phase2 slicer; no print qualification.',
        print_size_mm_including_5mm_brim=[v+10 if i<2 else v for i,v in enumerate(checks['dimensions_mm'])],
        status='conditional_hobby_phase1_selection')
    assert len(s['prints'])==71 and s['installed_petg_parts']==110 and s['fit_samples']==4
    assert len(q['lines'])==114 and next(r for r in q['lines'] if r['id']=='tie:111-02370')['installed']==93
    s.update(parent_selection_sha256=sha256(PARENT/'selection.json'),G1_exit_restraints=recipe,
        G1_exit_restraints_sha256=sha256(OUT/'interface.json'),phase1_percent=70,W5_complete=False)
    s['W5_recipe_precedence']='R41 overrides ONLY W061 G1_end and W060 G1_input cradle/tie placement. R38/R40 wire routes, endpoints, cut lengths, other restraints and insulation remain effective. R40 soft-contact condition remains OPEN. No W036 trial is selected.'
    q.update(selected_prints=(BATCH/'selection.json').relative_to(ROOT).as_posix(),G1_exit_restraints=recipe,G1_net_extra_ties=0,W5_complete=False)
    return s,q

def main():
    assert not (BATCH/'manifest.json').exists()
    c=read(OUT/'checks.json');assert (OUT/'preview.png').is_file(),'Inspect actual saved native preview first'
    s,q=payload(read(PARENT/'selection.json'),read(PARENT/'one-order-quantities.json'),c)
    parent=read(PARENT/'manifest.json');assert verify(ROOT,parent)['integrity_ok']
    runs=[];tick=time.monotonic()
    for pattern in ('test_g1_exit_restraints.py','test_main_input_return.py','test_body_ground_bridge.py','test_body_data_bridges_r3.py','test_assembly_materials_r39.py'):
        r=subprocess.run([sys.executable,'-X','utf8','-m','unittest','discover','-s','tools/electronics','-p',pattern,'-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        runs.append(dict(pattern=pattern,exit_code=r.returncode,output=r.stdout+r.stderr))
    save(OUT/'regression-run.json',dict(runs=runs,wall_seconds=time.monotonic()-tick));assert all(r['exit_code']==0 for r in runs)
    BATCH.mkdir(exist_ok=True);save(BATCH/'selection.json',s);save(BATCH/'one-order-quantities.json',q)
    summary=(OUT/'README.md').read_text(encoding='utf-8');(BATCH/'README.md').write_text(summary,encoding='utf-8',newline='\n')
    trials=[]
    for rev in (3,4,5):
        folder=ROOT/f'hardware/electronics/full-cat/body-ground-front-shared-r{rev}'
        trial=read(folder/'checks.json')
        trials.append(dict(revision=rev,selected=False,hits=trial['hits'],checks=(folder/'checks.json').relative_to(ROOT).as_posix()))
    save(OUT/'rejected-W036.json',dict(attempts=trials,selected=False,
        reason='R3 XA02/P_AUX; R4 RL_G/head support, and invalid same-loop self comparison. R5 actual head feed XB22/XB23/XS23 conflicts. No further similar corridor retries without a new packing solution. G1-only correction is independently checked.',
        unbuilt_trial_builder='tools/electronics/body_ground_front_finish_r1.py',unbuilt_trial_is_selected=False))
    end=datetime.now(timezone.utc);save(OUT/'work-time.json',dict(start_utc=START,end_utc=end.isoformat(),wall_seconds=(end-datetime.fromisoformat(START)).total_seconds(),
        kind='Three rejected W036 corridors, then independent two-G1-restraint native correction/export/current-interface checks/selection',active_CPU_seconds=None,physical_pass=False))
    pins={r['path']:r['sha256'] for r in parent['files']}
    folders=[OUT,CAD,BATCH]+[ROOT/f'hardware/electronics/full-cat/body-ground-front-shared-r{i}' for i in (3,4,5)]
    paths=[p for d in folders for p in d.iterdir() if p.is_file() and not p.name.endswith('.FCBak') and p.name not in ('manifest.json','validation.json')]
    names=['g1_exit_restraints_finish_r1.py','g1_exit_restraints_preview.py','test_g1_exit_restraints.py','package_g1_exit_restraints_r41.py','body_ground_front_shared_r3.py','body_ground_front_shared_r4.py','body_ground_front_shared_r5.py','body_ground_front_finish_r1.py','body_ground_front_preview.py']
    paths += [ROOT/'tools/electronics'/n for n in names]+[PARENT/'manifest.json']
    for rel,digest in c['source_sha256'].items():assert sha256(ROOT/rel)==digest;paths.append(ROOT/rel)
    for p in paths:
        rel=p.relative_to(ROOT).as_posix();digest=sha256(p);assert rel not in pins or pins[rel]==digest,rel;pins[rel]=digest
    m=copy.deepcopy(parent);m.update(parent_pins_preserved=len(parent['files']),phase1_percent=70,W5_complete=False,newly_selected_stls=1,
        files=[dict(path=p,sha256=h) for p,h in sorted(pins.items())])
    m['gates']['geometry']['evidence'].append((OUT/'checks.json').relative_to(ROOT).as_posix())
    m['gates']['geometry']['status']='open'
    m['gates']['geometry']['reason']='Changed G1 restraints and retained wire/Deck interfaces checked; inherited R40 soft-insulation condition and whole-W5 packing remain OPEN. Not global collision freedom or physical PASS.'
    integrity=verify(ROOT,m);assert integrity['integrity_ok']
    save(BATCH/'manifest.json',m);save(BATCH/'validation.json',dict(integrity=integrity,parent_pins_preserved=len(parent['files']),
        replaced_STL=1,new_print_jobs=0,unchanged_other_print_jobs=70,installed_petg=110,fit_samples=4,quantity_lines=114,
        purchase_lines_unchanged=True,net_extra_ties=0,phase1_percent=70,W5_complete=False,physical_pass=False))
    print(json.dumps(dict(pins=len(pins),parent_pins=len(parent['files']),phase1_percent=70,work_wall_seconds=(end-datetime.fromisoformat(START)).total_seconds())))

if __name__=='__main__':main()
