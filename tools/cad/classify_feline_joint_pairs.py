"""Classify a saved endpoint result without repeating its expensive Booleans.

Only exact archived GE/horn mating identities are separated. Their failed
Booleans remain OPEN; this cannot authorize a servo travel or physical motion.
"""
import json
import re
import time
import zipfile
from pathlib import Path
from check_main_p0_placement import ROOT, sha

BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT=BASE/'feline-enclosure'


def main():
    tick=time.monotonic()
    raw_path=OUT/'leg-body-endpoints.json'
    raw=json.loads(raw_path.read_text())
    motion=json.loads((OUT/'motion-layout.json').read_text())
    labels={p['object']:p['label'].split('/')[0].removeprefix('P0_') for p in motion['inventory']}
    archive=ROOT/'hardware/simulation/v35/inputs.zip'
    with zipfile.ZipFile(archive) as z: geometry=json.loads(z.read('geometry.json'))
    original={r['name']:r for r in geometry['components']}
    axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
    allowed={}
    for axis in axes:
        horn=original[axis['horn']]
        suffix=re.fullmatch(r'HornDisc_Drive_v(\d*)',horn['label'])
        assert suffix, horn
        # First imported supplier component has its original GE_27 label;
        # duplicated components use the matching three-digit suffix.
        gear_label='GE_27' if horn['label']=='HornDisc_Drive_v2' else 'GE_'+suffix[1]
        gear=[r for r in original.values() if r['label']==gear_label]
        assert len(gear)==1,(gear_label,gear)
        allowed[frozenset((axis['horn'],gear[0]['name']))]=axis['name']
    def joint(row):
        if 'a' not in row or 'b' not in row:return None
        return allowed.get(frozenset((labels[row['a']],labels[row['b']])) )
    supplier=[dict(row,joint=joint(row)) for row in raw['errors']+raw['new_contacts'] if joint(row)]
    errors=[row for row in raw['errors'] if not joint(row)]
    contacts=[row for row in raw['new_contacts'] if not joint(row)]
    result=dict(status='EXTERNAL_ENDPOINT_SCREEN_CLEAR_SUPPLIER_JOINT_MODEL_OPEN' if not errors and not contacts else 'EXTERNAL_ENDPOINT_SCREEN_REJECTED',
        selected=False,physical_pass=False,
        scope='Only external retained P0/leg/battery interfaces at two poses. Known twelve GE-to-drive-horn mating pairs are listed separately, not declared clear.',
        raw_result_sha256=sha(raw_path),current_datums=motion['current_horn_datums_verified'],
        poses=raw['poses'],pairs=raw['pairs'],external_contacts=contacts,external_errors=errors,
        supplier_joint_model_open=supplier,approved_joint_limits=False,continuous_sweep_verified=False,
        floor_and_pads_exact_checked=False,
        source_sha256={raw_path.relative_to(ROOT).as_posix():sha(raw_path),archive.relative_to(ROOT).as_posix():sha(archive),
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        qualification_seconds=round(time.monotonic()-tick,3),raw_worker_seconds=raw['worker_seconds'],
        correction='A failed baseline intersection is unknown, not zero. Eight raw NEW-contact labels concern these same GE/horn supplier pairs and are reclassified OPEN. No geometry changed or new Boolean attempted.')
    (OUT/'leg-body-endpoints-qualified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(result['status'],'supplier rows',len(supplier),'external errors',len(errors),'external contacts',len(contacts))


if __name__=='__main__':main()
