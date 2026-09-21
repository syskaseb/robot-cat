"""Verify audit provenance/completeness, NOT mechanical print readiness."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'hardware/skorupa/v26'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
jsonsha=lambda p:hashlib.sha256(json.dumps(read(p),sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()

def main():
    source=ROOT/'hardware/skorupa/v25/Kot_v25_DOMOWA_OSLONA.FCStd'
    expected='eccb5daf8d0c2585dec01bffd7f92717699270447b693a546e1d37b7360bcb5b'
    assert sha(source)==expected,'The audited source changed'
    service=read(OUT/'supplier-service-probe.json')
    fit=read(OUT/'supplier-fit.json')
    assert service['source_sha256']==fit['source_sha256']==expected
    assert len(fit['solids'])==117 and fit['solids'][0]['valid']
    assert [s['index'] for s in fit['solids'] if not s['valid']]==[25]
    assert len(fit['pcb_mount_holes_step_mm'])==4
    assert len(fit['grove_mount_holes_mm'])==5
    assert all(h['diameter']==2.2 for h in fit['grove_mount_holes_mm'])
    assert fit['fit_status']=='not_run' and not fit['fit_samples'],'Update audit conclusions if running full fit'
    assert set(h['obstacle'] for h in service['battery_hits'])=={'SideLeft22','SideRight22'}
    assert any(h['part']=='BatteryCarrier23' and h['dz']==1 for h in service['battery_hits'])
    archives={
        'waveshare-bus-servo-adapter-a':'59f239a112e9efa91d5eb6d353e95b3ce7a4ccf7cd2500eacc8d7c389877e9d2',
        'grove-pca9685':'ca73ab055bf7f847a4f5efef3a9ca8094eb16b75ce68b70c06fc69ebdc387e2f',
    }
    for folder,digest in archives.items():
        assert sha(ROOT/'hardware/reference'/folder/'source.zip')==digest
    files=['supplier-service-probe.json','supplier-fit.json','head-tail-audit.json']
    result=dict(audit_integrity_passed=True,mechanical_release=False,
        source_sha256=expected,exact_supplier_fit_completed=False,
        files_canonical_json_sha256={n:jsonsha(OUT/n) for n in files},archives_sha256=archives)
    (OUT/'audit-integrity.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result))

if __name__=='__main__':main()
