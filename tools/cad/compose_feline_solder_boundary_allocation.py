"""Transport seven selected PCA bare/jacket interfaces into REV3 exactly.

No guessed stripping length/core size and no treating PCB pads as jacket exits.
This is a source datum allocation, NOT whole wire or cross-module acceptance.
"""
import hashlib
import json
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT=BASE/'feline-enclosure'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def compose():
    tick=time.monotonic()
    files={k:p for k,p in dict(boundary=OUT/'n01-component-boundary-contract.json',
        plan=OUT/'n01-coupled-allocation-plan.json',
        source=BASE/'body-harness-checkpoint/u1-common-wiring-plan.json').items()}
    docs={k:json.loads(p.read_text()) for k,p in files.items()}
    p=docs['plan']['PWM9685'];assert docs['plan']['profile_revision']==3
    assert p['rotation_about_world_Y_degrees']==90
    a=p['source_PCB_bottom_datum_mm'];b=p['target_PCB_bottom_datum_mm']
    def point(q):
        # Exact proper Ry90: x'=z,z'=-x; no second placement of saved geometry.
        d=[q[i]-a[i] for i in range(3)]
        return [b[0]+d[2],b[1]+d[1],b[2]-d[0]]
    def direction(q):return [q[2],q[1],-q[0]]
    rows=[]
    for e in docs['boundary']['seven_PCA_solder_pads']:
        w=e['wire'];side=e['side'];source=docs['source'];r=source['routes'][w]
        bare=source['bare'][w+'/'+side];prefix=r['ends'][side]
        assert bare['ends_on_source_pad']==e['physical_interface']==prefix['physical_terminal']
        assert r['source']['OD_project_upper_mm']==e['nominal_OD_project_upper_mm']
        assert r['source']['project_radius_mm']==e['minimum_fixed_project_R_mm']
        offset=[e['current_point_mm'][i]-e['source_point_mm'][i] for i in range(3)]
        def current(q):return point([q[i]+offset[i] for i in range(3)])
        segments=[dict(s,**{k:current(s[k]) for k in ('start','end','mid') if k in s}) for s in bare['parts']]
        source_jacket=prefix['parts'][0]['start'];jacket=current(source_jacket)
        assert sum((segments[-1]['end'][i]-jacket[i])**2 for i in range(3))<1e-14
        pad=point(e['current_point_mm']);standoff=jacket[0]-pad[0]
        assert abs(standoff-(.5 if w.startswith('XS') else 1))<1e-7
        rows.append(dict(wire=w,side=side,physical_interface=e['physical_interface'],
            selected_source=r['source'],pad_world_mm=pad,jacket_mouth_world_mm=jacket,
            jacket_departure_axis=direction([0,0,1]),
            bare_segments=segments,bare_radius_project_mm=bare['radius'],
            source_nominal_strip_mm=bare['stripped_nominal_mm'],
            copper_radius_is_project_equivalent_not_supplier_bundle_measurement=True,
            insulation_stop_above_pad_project_mm=standoff,
            first_jacket_radius_mm=e['nominal_OD_project_upper_mm']/2,
            minimum_fixed_project_R_mm=e['minimum_fixed_project_R_mm'],
            inherited_solder_assembly_instruction=bare['instruction'],
            unchanged_pad_electrical_identity=True,
            intended_bare_PCB_hole_mate_not_a_general_collision_exemption=True,
            required_new=['Current actual hole/fillet fit and neighbours',
                'Independent jacket grip OUTSIDE bare portion',
                'Full changed jacket path/other six wires/retention/tools']))
    assert len(rows)==7
    return dict(status='SEVEN_SOURCE_BARE_TO_JACKET_DATUMS_ALLOCATED_NO_GEOMETRY_PASS',
        selected=False,N01_complete=False,physical_pass=False,ends=rows,
        notes=['Source bare passes through the named pad; jacket begins ABOVE the pad, not at the opposite bare tip',
            'All seven actual source jacket departure axes become +X after current Ry90',
            'Do not transfer old full routes or their neighbours to moved PWM',
            'Current selected conductor/core data retained; no new pinout/SKU/strip assumption'],
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in (*files.values(),Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,4))


if __name__=='__main__':
    dest=OUT/'n01-solder-boundary-allocation.json';assert not dest.exists();p=compose()
    dest.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=p['status'],ends=len(p['ends']),seconds=p['worker_seconds'])))
