"""Complete the 24 D/G fanouts; inherit twelve accepted V continuations.

Increase the single inner-mouth run to25mm, so adjacent R10 bends do not
overlap. Do not retest unchanged V paths or the OD5.5 moving corridors.
"""
from pathlib import Path
import w5_leg_fanouts_r1 as M
source=Path(M.__file__).read_text(encoding='utf-8')


def replace_once(old,new):
    global source
    assert source.count(old)==1,old
    source=source.replace(old,new)


replace_once("w5-leg-fanouts-r1'", "w5-leg-fanouts-r2'")
replace_once('lane=side*10.5','lane=side*5.5')
replace_once("strip_mm=None, end_allowance_assumption_mm=10,\n                    strip_source_pending=True,",
             "strip_mm=7.14, strip_tolerance_mm=.38, strip_source_pending=False,\n                    max_insulation_guide_clearance_mm=3.43,\n                    process_source='hardware/reference/leg-cable-2026-10-04/TE-output-process.json',")
replace_once('    started=datetime.now(timezone.utc)', '''    started=datetime.now(timezone.utc)
    prior_folder=ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r1'
    prior=json.loads((prior_folder/'checks.json').read_text(encoding='utf-8'))
    assert not prior['hits'] and len(prior['routes'])==12 and len(prior['errors'])==24
    assert all(r['role']=='V' for r in prior['routes'])
    assert all(sha(ROOT/k)==v for k,v in {**prior['source_sha256'],**prior['files']}.items())
    previous_shapes=Part.read(str(prior_folder/'FANOUTS_WORLD.brep')).childShapes()
    previous_paths=Part.read(str(prior_folder/'CENTERLINES_WORLD.brep')).childShapes()
    inherited={r['wire']:(r,s,p) for r,s,p in zip(prior['routes'],previous_shapes,previous_paths)}
    assert len(inherited)==12''')
replace_once('        try:\n            path=fillet_path(A,Part,[A.Vector(*p) for p in row[\'waypoints_mm\']],RADIUS)', '''        if row['role']=='V':
            previous,shape,path=inherited[row['wire']]
            previous=dict(previous)
            previous['provisional_far_end_blank_mm']=math.ceil((previous['continuous_external_design_mm']+7.52+30)/10)*10
            built.append(previous);geometries.append(shape);centerlines.append(path)
            print('INHERITED_V',row['wire'],flush=True)
            continue
        try:
            path=fillet_path(A,Part,[A.Vector(*p) for p in row['waypoints_mm']],RADIUS)''')
replace_once("for j,other in enumerate(geometries[i+1:],i+1):check(built[i]['wire'],shape,built[j]['wire'],other)",
             "for j,other in enumerate(geometries[i+1:],i+1):\n            if built[i]['role']=='V' and built[j]['role']=='V':continue\n            check(built[i]['wire'],shape,built[j]['wire'],other)")
begin=source.index('    # The bundle diameter changes:')
end=source.index('    files=[]',begin)
source=source[:begin]+'''    bundles=Part.read(str(prior_folder/'BUNDLES_WORLD.brep')).childShapes()
    assert len(bundles)==12
    for row,bundle in zip(data['corridors']['routes'],bundles):
        for info,shape in zip(built,geometries):
            if info['role']!='V' and info['loom']!=row['loom']:
                check(row['loom']+'_BUNDLE',bundle,info['wire'],shape)
''' +source[end:]
replace_once('    save(OUT/\'checks.json\',dict(status=', '''    pins += [Path(M.__file__),prior_folder/'checks.json',
        ROOT/'hardware/reference/leg-cable-2026-10-04/TE-output-process.json',
        ROOT/'hardware/reference/servo-holder-p0-2026-09-24/114-2123-current-TE.pdf']
    pins += [prior_folder/n for n in ('intent.json','FANOUTS_WORLD.brep','CENTERLINES_WORLD.brep','BUNDLES_WORLD.brep')]
    save(OUT/'checks.json',dict(inherited_unchanged='Twelve V body paths, OD5.5 bundle owner checks and bundle-to-bundle checks from R1',status=''')
exec(compile(source,str(Path(__file__).resolve()),'exec'))
