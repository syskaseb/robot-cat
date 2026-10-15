"""One current source-support reference set, without copying old binaries.

Eight updated native/STL parts plus four unchanged qualified Knee parts.
This is NOT the complete wiring/print release or a new phase score point.
"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def run():
    tick=time.monotonic();files=[OUT/n for n in ('axial-moving-supports/manifest.json','fixed-source-supports/manifest.json','remaining-supports/manifest.json')]
    moving,fixed,legacy=[json.loads(p.read_text()) for p in files]
    assert moving['status']=='FOUR_AXIAL_MOVING_SUPPORTS_NATIVE_PREPARED_FULL_W5_OPEN'
    assert fixed['status']=='FOUR_FIXED_SOURCE_SUPPORTS_NATIVE_PREPARED_RECEIVERS_OPEN'
    for receipt in (moving,fixed,legacy):
        for n,h in receipt['source_sha256'].items():assert SHA(ROOT/n)==h,n
    rows=[];natives=[]
    for receipt,basename in ((moving,'AxialMovingSupports.FCStd'),(fixed,'FixedSourceSupports.FCStd')):
        native=next(n for n in receipt['source_sha256'] if Path(n).name==basename);natives.append(native)
        for row in receipt['parts']:
            assert row['parameter_restore_mm']==[4,4.2,4] and row['relocated_reopen']
            export=next(q for q in receipt['exports'] if q['part']==row['name'])
            assert SHA(ROOT/export['path'])==export['sha256'] and export['printing']['fits_with_5mm_brim']
            rows.append(dict(part=row['name'],native=native,native_object=row['object'],export=export,quantity=1,
                updated=True,received_native_validation_reused=True,selected=False))
    knee=next(q for q in legacy['native_documents'] if Path(q['path']).name=='KneeLoomCarriers.FCStd');natives.append(knee['path'])
    assert SHA(ROOT/knee['path'])==knee['sha256'] and legacy['parameter_restore_mm']==[4,4.2,4] and legacy['relocated_reopen']
    for export in legacy['exports']:
        if not export['part'].endswith('KneeCarrier'):continue
        assert SHA(ROOT/export['path'])==export['sha256'] and export['printing']['fits_with_5mm_brim']
        rows.append(dict(part=export['part'],native=knee['path'],native_object=export['part'],export=export,quantity=1,
            updated=False,received_native_validation_reused=True,selected=False))
    assert len(rows)==12 and len({r['part'] for r in rows})==12
    artifacts=[ROOT/n for n in natives]+[ROOT/r['export']['path'] for r in rows]
    result=dict(status='CURRENT12_SOURCE_SUPPORT_REFERENCES_ONLY_FULL_W5_OPEN',parts=rows,native_documents=natives,
        updated_parts=8,unchanged_parts=4,closed_STLs=12,native_validation_reused=True,
        full_phase1_result_count=12,fixed_phase1_total=20,full_phase1_percent=60,new_phase_points=0,
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in [*files,*artifacts,Path(__file__)]},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False,
        remaining=['Complete receiver layouts/roots and16 missing core middles.',
            '19 other body guide retention/full placement, lengths/stock, assembly and whole release.',
            'No cosmetic outside enclosure, powered test or slicer run is included.'])
    p=OUT/'current-source-supports.json';p.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],len(rows),'parts',len(natives),'native docs',result['worker_seconds'],'seconds')


if __name__=='__main__':run()
