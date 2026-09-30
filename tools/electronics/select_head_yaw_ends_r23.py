"""Select two complete end restraints; retain explicit whole-harness limits."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'hardware/manufacturing/one-batch-prototype-r22'
OUT=ROOT/'hardware/manufacturing/one-batch-prototype-r23'
F=ROOT/'hardware/cad/studies/head-yaw-end-restraints-r2'
C=ROOT/'hardware/cad/studies/head-yaw-end-restraints-r1'
R=ROOT/'hardware/electronics/full-cat/head-complete-yaw-transitions-r3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'selection.json').exists()
    fc=read(F/'checks.json');rc=read(R/'checks.json');assert not fc['hits'] and not rc['hits'] and rc['moving_radius_sample_bound_met']
    s=read(P/'selection.json');q=read(P/'one-order-quantities.json')
    for identity,file in [('head:UpperFork',F/'ForkYawEndSeatSplices_candidate_x1.stl'),('body:RaisedUpperCover',C/'CoverYawEndSeat_candidate_x1.stl')]:
        matches=[x for x in s['prints'] if x['identity']==identity]
        if not matches and identity=='body:RaisedUpperCover':
            matches=[x for x in s['prints'] if 'CoverHeadWirePassage' in x['stl']]
        assert len(matches)==1,(identity,[x['identity'] for x in s['prints'] if 'cover' in x['identity'].lower()])
        matches[0].update(stl=file.relative_to(ROOT).as_posix(),sha256=sha(file),recipe=(F/'plan.json' if file.parent==F else C/'plan.json').relative_to(ROOT).as_posix(),status='selected_prototype_full_yaw_end_restraint')
    s['conditions'].append('R23 replaces both incomplete loop endpoints: tangent-clamped260mm free span, rigid R12.6 transitions, two integral insulation seats and rigid staggered-splice pocket. Sampled yaw±15/pitch−10..+5 nominal clear, min sampled radius32.948mm; not continuous/physical PASS. Large outside loop reachesY240.30 atyaw−15: fit/snags to inspect unpowered. Central feeds/fixed yaw feed and remaining SKU/protection still open.')
    s.update(parent_selection_sha256=sha(P/'selection.json'),phase1_complete=False)
    ties=next(x for x in q['lines'] if x['id']=='tie:111-02370');assert ties['installed']==42;ties['installed']=44;ties['note']+=' R23 adds2 independent moving/fixed insulation-seat ties, cut and replaced for cover removal.'
    q.update(selected_prints=(OUT/'selection.json').relative_to(ROOT).as_posix(),phase1_complete=False)
    dump(OUT/'selection.json',s);dump(OUT/'one-order-quantities.json',q)
    interface=dict(status='SELECTED_PROTOTYPE_BOTH_YAW_END_TRANSITIONS',
      moving_anchor_rest_mm=[-177.2,130,141],fixed_cover_anchor_mm=[-10,136,141],
      free_moving_length_mm=260,min_sampled_radius_mm=min(x['min_sampled_radius_mm'] for x in rc['poses']),
      tangent_continuity_all_sampled=True,rigid_transition_radius_mm=12.6,
      outside_loop_max_y_mm=max(p[1] for pose in rc['poses'] for p in pose['flexible_samples']),
      rigid_moving_reserved_length_mm=rc['rigid_moving_length_mm'],rigid_fixed_reserved_length_mm=rc['rigid_fixed_length_mm'],
      wires=read(R/'plan.json')['wires'],JR_factory_lead_cut=False,
      splices=read(F/'plan.json'),
      quantity_delta={'replacement_STL':2,'installed_parts':0,'additional_ties_from_existing_bag100':2,'additional_screws':0,'new_SKU':0},
      cover_removal='Unplug C_HP and cut both ordinary seat ties before lifting cover. Fixed rest anchor is part of cover, not Deck; no pulling servo lead or lifting tensioned loop.',
      remaining=['Central fixed feed from the existing wire endpoint(-10,76,124) to F_HP/G_AUX/R2','Complete fixed yaw-servo feed','Exact moving PWM/heatshrink SKU and remaining source/protection/harness'],
      sample_pose_scope='Yaw−15/0/+15,pitch−10/0/+5; separate component intersections, not continuous sweep.',physical_pass=False,phase1_complete=False)
    dump(OUT/'head-yaw-ends-interface.json',interface)
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig,axs=plt.subplots(1,2,figsize=(12,5))
    ax=axs[0];ax.add_patch(Rectangle((-98,-100),238,200,fill=False,ec='#555'));ax.add_patch(Rectangle((-205,-58),115,116,fill=False,ec='#888'))
    for pose in rc['poses']:
        points=pose['flexible_samples'];ax.plot([p[0] for p in points],[p[1] for p in points],label='yaw '+str(pose['yaw']))
    ax.add_patch(Rectangle((-184,62),16,72,alpha=.25));ax.add_patch(Rectangle((-23,88),21,54,alpha=.25))
    ax.set(xlabel='X mm',ylabel='Y mm',title='XY: pełna pętla i obrys osłony');ax.legend();ax.set_aspect('equal');ax.grid(alpha=.2)
    ax=axs[1];ax.add_patch(Rectangle((62,134),72,4.5,color='#779eb4'));ax.add_patch(Rectangle((95.5,137),28,1.5,color='white'))
    ax.plot([76,130],[141,141],color='#a86645');ax.plot([100,108,116],[141]*3,'o',label='oddzielne izolowane luty')
    ax.text(130,143,'odciążenie',ha='right');ax.set(xlabel='Y mm',ylabel='Z mm',title='Ruchomy sztywny odcinek: luty poza pętlą',ylim=(130,150));ax.legend();ax.grid(alpha=.2)
    fig.suptitle('R23: oba końce pętli, nie cała wiązka / bez fizycznego PASS');fig.tight_layout();fig.savefig(OUT/'preview.png',dpi=150);plt.close(fig)
    (OUT/'README.md').write_text('# R23: oba końce pętli yaw\n\nDwa zamienne STL,66 zadań/100PETG/4próbki. Zachowane uszy/P0 i fabryczny kabel250mm. Nowa pętla260mm ma zgodne styczne, minimalny próbkowany R32,948mm; obie integralne podpory i sztywna kieszeń lutów.44 T18I z istniejącego bag100. Maksymalny Y240,30mm: duża zewnętrzna pętla prototypu, ocenić zaczepianie po złożeniu. Złącze rozpiąć i opaski przeciąć przed zdjęciem osłony. Nadal otwarte centralne feedy, stały yaw i pozostałe SKU/zabezpieczenia. Slicer/druk/realne pasowania w fazie2, ROS w fazie3.\n',encoding='utf-8')
    pins=read(P/'manifest.json')['files_sha256'].copy()
    for folder in (F,C,R,OUT):
        for p in folder.iterdir():
            if p.is_file() and p.name not in ('manifest.json','partial-rows.json','progress.json') and p.suffix!='.FCBak':pins[p.relative_to(ROOT).as_posix()]=sha(p)
    for name in ('head_complete_yaw_transitions_r1.py','head_complete_yaw_transitions_r2.py','head_complete_yaw_transitions_r3.py','head_yaw_end_splices_r1.py','select_head_yaw_ends_r23.py'):
        p=ROOT/'tools/electronics'/name;pins[p.relative_to(ROOT).as_posix()]=sha(p)
    assert all(sha(ROOT/p)==h for p,h in pins.items())
    assert len(s['prints'])==66 and s['installed_petg_parts']==100 and len(q['lines'])==104
    dump(OUT/'manifest.json',dict(files_sha256=pins,new_stls=2,selected_jobs=66,installed_petg_parts=100,samples=4,physical_pass=False,phase1_complete=False))
    print(json.dumps(dict(pins=len(pins),jobs=66,parts=100)))
def finalize():
    m=read(OUT/'manifest.json'); pins={}
    for key,value in m['files_sha256'].items():
        normal=key.replace('\\','/')
        while '//' in normal: normal=normal.replace('//','/')
        assert normal not in pins or pins[normal]==value
        pins[normal]=value
    for p in (Path(__file__),OUT/'work-time.json'):
        pins[p.relative_to(ROOT).as_posix()]=sha(p)
    assert all(sha(ROOT/p)==h for p,h in pins.items())
    m['files_sha256']=pins;dump(OUT/'manifest.json',m)
    validation=dict(schema_version=1,readiness='prototype',files=[dict(path=p,sha256=h) for p,h in pins.items()],
      gates={k:dict(status='open',reason='Changed R23 nominal geometry only; whole prototype and physical readiness not established') for k in ('geometry','assembly','fit','petg','loads','electrical','service')})
    dump(OUT/'validation-manifest.json',validation)
    print(json.dumps(dict(pins=len(pins),all_hashes_verified=True,physical_pass=False)))
if __name__=='__main__':
    if '--finalize' in sys.argv: finalize()
    else: main()
