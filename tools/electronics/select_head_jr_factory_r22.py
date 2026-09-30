"""Select the JR/factory-lead construction, not a complete head harness."""
import json,hashlib,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PARENT=ROOT/'hardware/manufacturing/one-batch-prototype-r21'
CAD=ROOT/'hardware/cad/studies/head-jr-support-r5'
ROUTE=ROOT/'hardware/electronics/full-cat/head-factory-lead-remedy-r3'
OUT=ROOT/'hardware/manufacturing/one-batch-prototype-r22'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def main():
    c=read(CAD/'checks.json');r=read(ROUTE/'checks.json')
    assert c['status']=='JR_HOLDER_CANDIDATE' and not c['hits']
    assert r['status']=='SAMPLED_FACTORY_LEAD_ROUTE_CLEAR' and not r['hits']
    OUT.mkdir(exist_ok=True)
    s=read(PARENT/'selection.json');q=read(PARENT/'one-order-quantities.json')
    for identity,name,orientation in [('head:UpperFork','ForkJRHolder','broad side Y+90, brim5, supports after slicer review'),
      ('head:PitchCarrier','PitchCarrierThroughLeadExit','open side up, brim5, supports after slicer review')]:
        p=CAD/(name+'_candidate_x1.stl');row=next(x for x in s['prints'] if x['identity']==identity)
        row.update(stl=p.relative_to(ROOT).as_posix(),sha256=sha(p),recipe=(CAD/'plan.json').relative_to(ROOT).as_posix(),
          orientation=orientation,status='selected_prototype_JR_factory_wire_candidate')
    s.update(parent_selection_sha256=sha(PARENT/'selection.json'),phase1_complete=False)
    s['conditions'].append('R22: integral JR shelf, independent insulation ties, loose factory-coil guard and local Carrier/Fork wire windows. 250mm factory lead preserved, provisional profile/exit; sampled route224.886mm. Custom moving-loop transitions and fixed yaw feed still open, not complete head wiring.')
    row=next(x for x in q['lines'] if x['id']=='tie:111-02370');assert row['installed']==37
    row['installed']=42;row['note']+=' R22 adds5 for C_HP:two housing straps,two insulated ends andone loose factory-coil guard. Bag100 unchanged; ordinary ties cut/replaced for removal.'
    q.update(selected_prints=(OUT/'selection.json').relative_to(ROOT).as_posix(),phase1_complete=False,head_JR_ties_used_from_existing_bag100=5)
    dump(OUT/'selection.json',s);dump(OUT/'one-order-quantities.json',q)
    interface=dict(status='SELECTED_JR_AND_FACTORY_LEAD_INTERFACES',replacement_stls=2,new_installed_printed_parts=0,new_screws=0,new_skus=0,
      new_ties_from_existing_bag100=5,ties_total_installed_allowance=42,
      ownership='C_HP on integral UpperFork, same yaw frame as pitch servo, not detachable pitch shell. Supersedes Carrier-only location.',
      JR_design_bbox_mm=[-158,82,136,-146,112,146],JR_bbox_is_provisional=True,
      factory_lead={'cut':False,'nominal_length_mm':250,'reserved_centerline_mm':r['centerline_length_mm'],'nominal_residual_mm':r['nominal_factory250_residual_mm'],
        'provisional_flat_profile_mm':[3.5,1.8],'minimum_design_bend_mm':22,'coil_upper_center_mm':[-143,114,186.769728648],
        'scope':'sampled yaw/pitch geometry, not actual wire stiffness or continuous motion qualification'},
      ends={'V+':'XB22 F_HP.out -> C_HP red,HELU23302 0.5mm2,AUX6V behind1A F_HP',
        'GND':'XB23 G_AUX.4 -> C_HP brown/black,HELU23301 0.5mm2,power return not signal ground',
        'PWM':'XS23 U1/R2.2 -> C_HP yellow,Kamami1178401 candidate0.12mm2,never used as servo power return'},
      connector='Existing selected Kamami586761 JR/Futaba30cm22AWG mating lead. Factory connector and250mm cable unchanged. Verify actual view/pin order; no keyed-unique claim.',
      assembly=['Only two replacement prints; keep R21 front-right relief and cover passage.','Install Carrier and lay factory lead before head closure; S-exit uses the new low windows, never the journal.','Place JR pair on shelf;two ties atY86/108,independent insulated-end tiesY76/118. Keep contacts/solder uncompressed.','Keep factory coil outside the pitch shell; one loose tie through upper guard slots. No preloading, no bend at connector crimp.','Ordinary T18I are cut and replaced for removal; deburr slot/window edges0.5mm.','Retain nominal25.114mm factory residual as a fit allowance, not extra purchased wire. Do not cut factory lead.'],
      remaining=['Both complete custom yaw-loop end transitions and fixed yaw feed','Remaining harness/SKUs/source protection','Actual factory exit/length/profile,pinout and PETG journal-window/guard fit after delivery'],
      next_step='Construct both custom loop end transitions/restraints plus fixed yaw motor feed as one complete head-harness stage.',
      physical_pass=False,phase1_complete=False)
    dump(OUT/'head-JR-factory-interface.json',interface)
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig,axs=plt.subplots(1,2,figsize=(12,5))
    ax=axs[0];ax.add_patch(Rectangle((-170,62),40,18,color='#729eb8'));ax.add_patch(Rectangle((-170,79),32,43,color='#729eb8'))
    ax.add_patch(Rectangle((-158,82),12,30,color='#e7b456'));ax.text(-152,97,'JR',ha='center')
    for b in c['slot_checks']:v=b['bbox_mm'];ax.add_patch(Rectangle((v[0],v[1]),v[3]-v[0],v[4]-v[1],color='white',ec='black'))
    ax.set(xlim=(-178,-125),ylim=(55,130),title='XY: JR i niezależne mocowania',xlabel='X mm',ylabel='Y mm')
    ax=axs[1];ax.add_patch(Rectangle((62,133),60,3,color='#729eb8'));ax.add_patch(Rectangle((82,136),30,10,color='#e7b456'))
    ax.add_patch(Rectangle((114,136),6,48,color='#729eb8'));ax.add_patch(Rectangle((110,182),8,2,color='#729eb8'))
    for lo,hi,cy,cz,ry,rz in [(-90,0,70,150.5,22,22),(180,0,114,163,22,math.hypot(9,22)),(0,-90,114,163,22,22)]:
        ts=[math.radians(lo+(hi-lo)*i/100) for i in range(101)];ax.plot([cy+ry*math.cos(t) for t in ts],[cz+rz*math.sin(t) for t in ts],color='#ae654a')
    ax.plot([92,92],[150.5,163],color='#ae654a');ax.plot([114,112],[141,141],color='#ae654a')
    ax.set(xlim=(57,143),ylim=(123,193),title='YZ: zewnętrzny zapas fabrycznego kabla',xlabel='Y mm',ylabel='Z mm')
    for ax in axs:ax.set_aspect('equal');ax.grid(alpha=.2)
    fig.suptitle('R22: JR i fabryczny przewód głowy / nadal nie cała wiązka');fig.tight_layout();fig.savefig(OUT/'preview.png',dpi=150);plt.close(fig)
    (OUT/'README.md').write_text('# R22: JR i fabryczny przewód głowy\n\nDwa zamienne STL,66 zadań/100 PETG/4 próbki. Bez nowych śrub i SKU;5 T18I z bag100,razem42. Fabryczny lead250mm bez cięcia,trasa224,886mm z luźnym zewnętrznym mocowaniem. Wymiary przewodu/JR i wyjście prowizoryczne. Nie cała wiązka ani ukończona faza1: oba końce pętli yaw i stały feed pozostają otwarte. Montaż/końce/ryzyka w head-JR-factory-interface.json; slicer i próby po dostawie w fazie2.\n',encoding='utf-8')
    pins=read(PARENT/'manifest.json')['files_sha256'].copy()
    pins.update(read(ROOT/'hardware/cad/studies/head-jr-support-r2/manifest.json')['files_sha256'])
    pins.update(read(ROOT/'hardware/electronics/full-cat/head-factory-lead-storage-r3/checks.json')['source_sha256'])
    pins.update(r['parent_hashes']);pins.update(read(CAD/'plan.json')['parent_files_sha256'])
    for folder in (CAD,OUT,ROUTE,ROOT/'hardware/electronics/full-cat/head-factory-lead-storage-r3',ROOT/'hardware/electronics/full-cat/head-factory-lead-local-profiles-r1'):
        for p in folder.iterdir():
            if p.is_file() and p.name!='manifest.json' and p.suffix!='.FCBak':pins[p.relative_to(ROOT).as_posix()]=sha(p)
    for file in [Path(__file__),ROOT/'tools/cad/head_jr_support_r5.py',ROOT/'tools/electronics/head_factory_lead_guard_r5_check.py',ROOT/'tools/electronics/head_factory_lead_storage_r1.py',ROOT/'tools/electronics/head_factory_lead_storage_r2.py',ROOT/'tools/electronics/head_factory_lead_storage_r3.py',ROOT/'tools/electronics/head_factory_lead_local_profiles.py']:pins[file.relative_to(ROOT).as_posix()]=sha(file)
    assert len(s['prints'])==66 and s['installed_petg_parts']==100 and len(q['lines'])==q['line_count']==104
    assert all(sha(ROOT/x['stl'])==x['sha256'] for x in s['prints'])
    assert all(sha(ROOT/p)==h for p,h in pins.items())
    dump(OUT/'manifest.json',dict(files_sha256=pins,selected_jobs=66,installed_petg_parts=100,samples=4,new_stls=2,physical_pass=False,phase1_complete=False))
    print(json.dumps(dict(pins=len(pins),jobs=66,parts=100,ledger_lines=104)))
if __name__=='__main__':main()
