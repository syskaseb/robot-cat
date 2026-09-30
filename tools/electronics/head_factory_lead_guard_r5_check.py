"""Only changed Fork/Carrier versus saved lead segments; inherit unchanged clear rows."""
import json
from pathlib import Path
import head_factory_lead_storage_r1 as B
ROOT=B.ROOT
CAD=ROOT/'hardware/cad/studies/head-jr-support-r5'
P=ROOT/'hardware/electronics/full-cat/head-factory-lead-storage-r3'
F=ROOT/'hardware/electronics/full-cat/head-factory-lead-local-profiles-r1'
OUT=ROOT/'hardware/electronics/full-cat/head-factory-lead-remedy-r3'
def main():
    OUT.mkdir(exist_ok=True);assert not (OUT/'checks.json').exists()
    old=json.loads((P/'checks.json').read_text());flat=json.loads((F/'checks.json').read_text())
    geom=json.loads((CAD/'checks.json').read_text());assert geom['status']=='JR_HOLDER_CANDIDATE' and not geom['hits']
    rows=[]
    fork=B.load(CAD/'ForkJRHolder.brep')
    for b in geom['coil_slots_mm']:
        probe=B.R.box([b[0]+.1,b[1]+.1,b[2]-.5,b[3]-.1,b[4]-.1,b[5]+.5])
        assert B.R.volume(probe.common(fork))<1e-6
    assert len(geom['coil_slots_mm'])==2
    for n,p in [('Fork',CAD/'ForkJRHolder.brep'),('Carrier',CAD/'PitchCarrierThroughLeadExit.brep')]:
        owner=B.load(p);assert len(owner.Solids)==1
        for i in range(8):
            precise=F/f'FlatLead{i}.brep';lead=B.load(precise if precise.exists() else P/f'LeadEnvelope{i}.brep')
            bounded=not B.R.overlap(owner.BoundBox,lead.BoundBox)
            v=0 if bounded else B.R.volume(owner.common(lead))
            rows.append(dict(owner=n,segment=i,profile='pinned flat provisional' if precise.exists() else 'circumscribed envelope',
              status='bbox_separated' if bounded else 'exact_single_solids',hit_mm3=v))
    inherited=[]
    for r in old['exact_component_rows']:
        if r['owner'] in ('Fork','Carrier'):continue
        if r['hit_mm3']>1e-5:
            resolved=next(q for q in flat['rows'] if all(q[k]==r[k] for k in ('owner','segment','solid','pose')))
            assert resolved['hit_mm3']<1e-5
            inherited.append({**r,'original_conservative_hit_mm3':r['hit_mm3'],'hit_mm3':resolved['hit_mm3'],'resolution':'local pinned flat profile'})
        else:inherited.append(r)
    hits=[r for r in rows+inherited if r['hit_mm3']>1e-5]
    result=dict(status='REJECTED' if hits else 'SAMPLED_FACTORY_LEAD_ROUTE_CLEAR',new_affected_rows=rows,inherited_unchanged_rows=inherited,hits=hits,
      centerline_length_mm=old['centerline_length_mm'],nominal_factory250_residual_mm=old['nominal_residual_mm'],
      parent_hashes={str(p.relative_to(ROOT)):B.R.sha(p) for p in [P/'checks.json',F/'checks.json',CAD/'checks.json',CAD/'plan.json']},
      script_sha256=B.R.sha(Path(__file__)),new_stls=0,physical_pass=False,phase1_complete=False,
      conditions=['Factory250 length/exit/3.5x1.8 profile provisional','Up to25.114mm residual nominal budget, actual slack and connector end must be fitted, no factory cut',
        'Native wire windows below journal bound are geometric ligaments, not loaded PETG qualification','Loose coil guard and independent housing/end straps use5 T18I from the existing bag; actual fit and no preload verified after delivery',
        'Whole head harness still needs both yaw loop end transitions/restraints and fixed yaw feed'])
    (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(status=result['status'],hits=hits)),flush=True)
if __name__=='__main__':main()
