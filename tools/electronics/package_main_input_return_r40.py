"""Select complete W060 only; preserve every R39 source pin and other print."""
import copy,json,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/cad'))
from release_check import verify,sha256
PARENT=ROOT/'hardware/manufacturing/one-batch-prototype-r39'
BATCH=ROOT/'hardware/manufacturing/one-batch-prototype-r40'
OUT=ROOT/'hardware/electronics/full-cat/main-input-return-finish-r3'
CAD=ROOT/'hardware/cad/studies/main-input-return-finish-r3'
START='2026-10-02T03:21:43+00:00'

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

def payload(selection,quantities,checks):
    assert checks['status']=='W060_READY_WITH_SOFT_CONTACT_RESERVE' and not checks['blocking_hits']
    assert checks['mesh_export_complete']
    assert checks['hits']==checks['nominal_soft_contacts']
    assert len(checks['nominal_soft_contacts'])==1
    assert checks['nominal_soft_contacts'][0]['hit_mm3']<.2
    s,q=copy.deepcopy(selection),copy.deepcopy(quantities)
    identities={'electronics:DeckP10-cover-mount':('Deck','DeckMainInput.FCStd'),
                'P0-MAIN-MOUNT-R5':('MAIN','MainInputMount.FCStd')}
    recipe=(OUT/'interface.json').relative_to(ROOT).as_posix()
    native_sources=read(OUT/'interface.json')['native_sources']
    for row in s['prints']:
        if row['identity'] not in identities:continue
        name,native=identities[row['identity']];f=CAD/(name+'_x1.stl')
        row.update(stl=f.relative_to(ROOT).as_posix(),sha256=sha256(f),
            native=native_sources[name],recipe=recipe,
            print_size_mm_including_5mm_brim=[v+10 if i<2 else v for i,v in enumerate(checks['dimensions_mm'][name])],
            orientation='Retain lower Deck base, +Zup; DATA/W061 seats preserved' if name=='Deck' else 'Retain60x26mm base on bed, +Zup; raised input beam on original mount',
            supports='Inspect new wire-groove/beam overhangs and retained openings in phase2 slicer; no print qualification',
            status='conditional_hobby_phase1_selection')
    assert len(s['prints'])==71 and s['installed_petg_parts']==110 and s['fit_samples']==4
    ties=next(r for r in q['lines'] if r['id']=='tie:111-02370');assert ties['installed']==90
    ties['installed']=93;ties['note']+=' R40 W060 adds3 insulation seats/ties. Working93 from the same100pc bag; fullW5/K3 census remains open.'
    cable=next(r for r in q['lines'] if r['id']=='p0:PI-POWER-CABLE');assert cable['planning_quantity']==1
    cable['note']+=' R40 W060 black nominal220mm blank after178.669mm route, not a second cable. Black leftover489.751mm after Pi reserve290.249mm; redW078 still unrouted<=150mm. Parallel conductors are not summed against one1m cable.'
    for identity,addition in [('sleeve:5052942064',' W060 adds one4mm inner blank; trim to actual2mm neck offPCB.'),('sleeve:5053042067',' W060 adds one15mm outer blank allowance, trimmed offPCB to nominal8.01mm placement and at least6mm intact overlap.')]:
        next(r for r in q['lines'] if r['id']==identity)['note']+=addition
    s.update(parent_selection_sha256=sha256(PARENT/'selection.json'),main_input_return=recipe,
        main_input_return_sha256=sha256(OUT/'interface.json'),phase1_percent=70,W5_complete=False,K3_complete=False)
    q.update(selected_prints=(BATCH/'selection.json').relative_to(ROOT).as_posix(),main_input_return=recipe,
        main_input_ties_from_existing_bag100=3,W5_complete=False,K3_complete=False)
    assert len(q['lines'])==q['line_count']==114
    return s,q

def main():
    assert not (BATCH/'manifest.json').exists()
    c=read(OUT/'checks.json');assert (OUT/'preview.png').is_file(),'Inspect saved CAD preview before selection'
    s,q=payload(read(PARENT/'selection.json'),read(PARENT/'one-order-quantities.json'),c)
    parent=read(PARENT/'manifest.json');assert verify(ROOT,parent)['integrity_ok']
    before=read(PARENT/'selection.json')['prints'];after=s['prints'];changed={a['identity'] for a,b in zip(after,before) if a!=b}
    assert changed=={'electronics:DeckP10-cover-mount','P0-MAIN-MOUNT-R5'}
    runs=[];tick=time.monotonic()
    for pattern in ('test_main_input_return.py','test_body_ground_bridge.py','test_body_data_bridges_r3.py','test_assembly_materials_r39.py'):
        r=subprocess.run([sys.executable,'-X','utf8','-m','unittest','discover','-s','tools/electronics','-p',pattern,'-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
        runs.append(dict(pattern=pattern,exit_code=r.returncode,output=r.stdout+r.stderr))
    save(OUT/'regression-run.json',dict(runs=runs,wall_seconds=time.monotonic()-tick));assert all(r['exit_code']==0 for r in runs)
    BATCH.mkdir(exist_ok=True);save(BATCH/'selection.json',s);save(BATCH/'one-order-quantities.json',q)
    (BATCH/'README.md').write_text((OUT/'README.md').read_text(encoding='utf-8'),encoding='utf-8',newline='\n')
    failures=[]
    for revision in (1,2,3):
        d=ROOT/f'hardware/electronics/full-cat/main-input-return-r{revision}';v=read(d/'checks.json')
        failures.append(dict(revision=revision,hits=v['hits'],checks=(d/'checks.json').relative_to(ROOT).as_posix(),selected=False))
    save(OUT/'rejected-corridors.json',dict(attempts=failures,selected=False,
        note='R1 output/DATA/Deck; R2 retained P0 north support; R3 DATA clearance. R4 uses X132.5,Y0; no support/DATA remap. FinishR1 failed deleted-proxy check after saving, not a native geometry assertion.'))
    end=datetime.now(timezone.utc);save(OUT/'work-time.json',dict(start_utc=START,end_utc=end.isoformat(),wall_seconds=(end-datetime.fromisoformat(START)).total_seconds(),
        kind='Complete W060 route, three native seats, insulation, recovery of native checker, exports and one selected replacement set',active_CPU_seconds=None,physical_pass=False))
    pins={r['path']:r['sha256'] for r in parent['files']}
    folders=[OUT,CAD,BATCH]
    folders += [ROOT/f'hardware/electronics/full-cat/main-input-return-r{i}' for i in (1,2,3,4)]
    folders += [ROOT/f'hardware/electronics/full-cat/main-input-return-finish-r{i}' for i in (1,2)]
    folders += [ROOT/f'hardware/cad/studies/main-input-return-finish-r{i}' for i in (1,2)]
    paths=[p for d in folders for p in d.iterdir() if p.is_file() and not p.name.endswith('.FCBak') and p.name not in ('manifest.json','validation.json')]
    paths += [p for p in (ROOT/'tools/electronics').glob('main_input_return*.py')]+[Path(__file__),Path(__file__).with_name('test_main_input_return.py'),PARENT/'manifest.json']
    for rel,digest in c['source_sha256'].items():assert sha256(ROOT/rel)==digest;paths.append(ROOT/rel)
    for p in paths:
        rel=p.relative_to(ROOT).as_posix();h=sha256(p);assert rel not in pins or pins[rel]==h,rel;pins[rel]=h
    m=copy.deepcopy(parent);m.update(new_stls=2,newly_selected_stls=2,parent_pins_preserved=len(parent['files']),phase1_percent=70,W5_complete=False,K3_complete=False,
        files=[dict(path=p,sha256=h) for p,h in sorted(pins.items())])
    m['gates']['geometry']['evidence'].append((OUT/'checks.json').relative_to(ROOT).as_posix())
    m['gates']['geometry']['status']='open'
    m['gates']['geometry']['reason']='W060 native/rigid parts and closed prints checked; explicit0.177mm3 soft-insulation reserve contact to dry-fit in phase2. NOT collision-free or physical fit.'
    integrity=verify(ROOT,m);assert integrity['integrity_ok']
    save(BATCH/'manifest.json',m);save(BATCH/'validation.json',dict(integrity=integrity,parent_pins_preserved=len(parent['files']),
        replaced_STL=2,new_print_jobs=0,unchanged_other_print_jobs=69,installed_petg=110,fit_samples=4,quantity_lines=114,
        phase1_percent=70,W5_complete=False,K3_complete=False,physical_pass=False))
    print(json.dumps(dict(pins=len(pins),parent_pins=len(parent['files']),changed_prints=sorted(changed),phase1_percent=70,work_wall_seconds=(end-datetime.fromisoformat(START)).total_seconds())))

if __name__=='__main__':main()
