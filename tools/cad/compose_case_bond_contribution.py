"""Twelve provisional case-only patches, never wire strain relief."""
import json,math,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from plan_current_harness_interfaces import ROOT,OUT,SHA
from current_source_case_retention import material


def patch_size(bounds):
    dimensions=sorted(b-a for a,b in zip(bounds[:3],bounds[3:]))
    assert abs(dimensions[0]-.5)<1e-6
    return dimensions[1:]


def run():
    tick=time.monotonic();archive=OUT/'remaining25-space-context.zip'
    allocation_file=OUT/'remaining25-interface-allocation.json';legs_file=OUT/'leg-stations-plan.json'
    proof_file=OUT/'source-case-retention-space.json';proof=json.loads(proof_file.read_text())
    assert len(proof['parts'])==24 and not proof['errors'] and not any(r['contacts'] for r in proof['parts'])
    targets={}
    with zipfile.ZipFile(archive) as z:
        for r in json.loads(z.read('index.json'))['entries']:
            if r['kind']!='target':continue
            if not (r['name'].startswith('MTA/') or r['name'].split('/')[0] in {w+'_Joint' for w in ('W026','W037','W041','W042','W044','W045','W052','W053')}):continue
            s=Part.Shape();s.importBrepFromString(z.read(r['file']).decode());targets[r['name']]=s
    q=material(targets,json.loads(allocation_file.read_text()),json.loads(legs_file.read_text()))
    helper=Path(__file__).with_name('current_source_case_retention.py');key=helper.relative_to(ROOT).as_posix()
    assert proof['source_sha256'][key]==SHA(helper)
    facts_file=ROOT/'hardware/reference/case-retention-2026-10-16/facts.json';facts=json.loads(facts_file.read_text())
    assert facts['nominal_thickness_mm']==.5 and not facts['physical_pass']
    rows=[]
    for n,r in q['recipes'].items():
        width,length=patch_size(r['adhesive_bounds_mm']);assert width<=11.91
        rows.append(dict(role=n,quantity=1,cut_width_project_mm=width,cut_length_project_mm=length,
            nominal_thickness_mm=.5,area_project_mm2=width*length,actual_cut_mm=None,case_only_NOT_wire_restraint=True))
    nominal=sum(r['cut_length_project_mm'] for r in rows);trim=3*len(rows)
    assert nominal+trim<=500
    files=[archive,allocation_file,legs_file,proof_file,helper,facts_file,
        facts_file.with_name('3M-VHB-4905-TDS.pdf'),Path(__file__)]
    p=dict(status='TWELVE_CASE_ONLY_BOND_PATCHES_NOMINAL_STOCK_CONTRIBUTION',patches=rows,
        total_patch_area_project_mm2=sum(r['area_project_mm2'] for r in rows),
        sequential_stock_draw_project_mm=nominal,project_cut_allowance_mm=trim,
        candidate_stock=dict(part_family='3M VHB4905',width_project_mm=12.7,length_project_mm=500,
            fraction_of_roll_NOT_claimed_purchase_unit=True,nominal_thickness_mm=.5),
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in files},worker_seconds=round(time.monotonic()-tick,3),
        gates=['Unpowered actual flat-contact/PETG/case/adhesion/creep and thickness trial before use',
               'Hand support holder during cap servicing; no load rating inferred from metal coupon data',
               'All wire loads use independent native insulation restraints','Whole stock still includes other module materials'],
        selected=False,stock_selected=False,purchase_authorized=False,W5_complete=False,physical_pass=False)
    (OUT/'case-bond-material-contribution.json').write_text(json.dumps(p,indent=2)+'\n')
    print(json.dumps(dict(patches=len(rows),area_mm2=p['total_patch_area_project_mm2'],stock_mm=nominal+trim,seconds=p['worker_seconds'])))


if __name__=='__main__':run()
