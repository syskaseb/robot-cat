"""One combined four-ground-block/24-core replacement on selected R53.

Preserve twelve V branches and the moving OD5.5 proofs. Changed block
placements need native supports and a release selection AFTER clean checks.
No moved block or moved DATA tie is silently treated as installed hardware.
"""
from pathlib import Path
import runpy

definition = runpy.run_path(str(Path(__file__).with_name('w5_leg_fanouts_r3.py')),
                           run_name='r3_definitions_only')
M = definition['M']
source = definition['source']


def replace(old,new):
    global source
    assert source.count(old)==1,old
    source=source.replace(old,new)


replace("w5-leg-fanouts-r3'","w5-leg-fanouts-r4'")
replace('    assert len(planned)==36 and len({r[\'wire\'] for r in planned})==36',
        '''    from w5_leg_fanout_layout import changed_plan, GROUND_DX, GROUND_DY
    planned=changed_plan(planned)
    assert len(planned)==36 and len({r['wire'] for r in planned})==36''')
replace("    hits=[];errors=[];pairs=0;built=[];geometries=[];centerlines=[]", '''    accepted_v_folder=ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r3'
    r3=json.loads((accepted_v_folder/'checks.json').read_text(encoding='utf-8'))
    assert r3['status']=='COUPLED_LEG_FANOUT_REJECTED' and len(r3['routes'])==36 and not r3['errors']
    assert not any(h['wire'] in {r['wire'] for r in r3['routes'] if r['role']=='V'} for h in r3['hits'])
    assert all(sha(ROOT/k)==v for k,v in {**r3['source_sha256'],**r3['files']}.items())
    v_shapes=Part.read(str(accepted_v_folder/'FANOUTS_WORLD.brep')).childShapes()
    v_paths=Part.read(str(accepted_v_folder/'CENTERLINES_WORLD.brep')).childShapes()
    inherited_v={r['wire']:(r,s,p) for r,s,p in zip(r3['routes'],v_shapes,v_paths) if r['role']=='V'}
    assert len(inherited_v)==12
    new_mount_owners={}
    for leg in ('FL','FR','RL','RR'):
        key=leg+'_G_design';shape=owners[key].copy()
        b=shape.BoundBox;side=1 if leg.endswith('L') else -1
        shape.rotate(A.Vector((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2),A.Vector(0,0,1),180)
        shape.translate(A.Vector(GROUND_DX,side*GROUND_DY,0))
        owners[key]=shape;new_mount_owners[key]=shape
    # Shift only along existing straight DATA spans, not perpendicular to them.
    # Actual grip seating and native Deck slots still need reconstruction.
    tie_shifts={'DATA_tie/W007/1/':-2.5,'DATA_tie/W012/0/':1.5}
    for prefix,dx in tie_shifts.items():
        keys=[k for k in owners if k.startswith(prefix)]
        assert len(keys)==5
        for key in keys:
            shape=owners[key].copy();shape.translate(A.Vector(dx,0,0))
            owners[key]=shape;new_mount_owners[key]=shape
    hits=[];errors=[];pairs=0;built=[];geometries=[];centerlines=[]''')
replace('    for row in planned:\n        try:', '''    placement_hits_start=len(hits)
    for key,shape in new_mount_owners.items():
        if key.startswith('DATA_tie/'):continue  # wire/grip seating is a separate construction gate
        for other_key,other in owners.items():
            if key!=other_key:check('RELOCATED/'+key,shape,other_key,other)
        for wire,(_,other,_) in inherited_v.items():check('RELOCATED/'+key,shape,wire,other)
    placement_hits=hits[placement_hits_start:].copy()
    for row in planned:
        if row['role']=='V':
            previous,shape,path=inherited_v[row['wire']]
            for key,other in new_mount_owners.items():check(row['wire'],shape,key,other)
            built.append(previous);geometries.append(shape);centerlines.append(path)
            print('INHERITED_V',row['wire'],flush=True)
            continue
        try:''')
replace("for j,other in enumerate(geometries[i+1:],i+1):\n            check(built[i]['wire'],shape,built[j]['wire'],other)",
        "for j,other in enumerate(geometries[i+1:],i+1):\n            if built[i]['role']=='V' and built[j]['role']=='V':continue\n            check(built[i]['wire'],shape,built[j]['wire'],other)")
replace("if info['loom']!=row['loom']:","if info['role']!='V' and info['loom']!=row['loom']:")
replace("    pins += [ROOT/chosen_carrier['stl']]", '''    mounts=OUT/'RELOCATED_OWNERS_WORLD.brep'
    Part.makeCompound(list(new_mount_owners.values())).exportBrep(str(mounts));files.append(mounts)
    pins += [accepted_v_folder/'checks.json',accepted_v_folder/'intent.json',
             accepted_v_folder/'FANOUTS_WORLD.brep',accepted_v_folder/'CENTERLINES_WORLD.brep',
             ROOT/'tools/electronics/w5_leg_fanout_layout.py',ROOT/'tools/electronics/w5_leg_fanouts_r3.py']
    pins += [ROOT/chosen_carrier['stl']]''')
replace("dict(omitted_retired_carrier_aliases=omitted_carrier_aliases,inherited_unchanged=",
        "dict(changed_mounts=list(new_mount_owners),relocated_block_hits=placement_hits, native_supports_ready=False, omitted_retired_carrier_aliases=omitted_carrier_aliases,inherited_unchanged=")
replace("'Only OD5.5 moving corridor owner and mutual checks from R1; all36 body core branches changed'",
        "'OD5.5 moving corridor owner/mutual checks from R1; twelve unchanged V branches from R3. All24 D/G and moved owners rechecked'")
exec(compile(source,str(Path(__file__).resolve()),'exec'))
