"""One coordinated branch/coil separation; cheap full-path screen first.

Not scalar re-runs of the rejected front S1 island. Preserve the S1 body,
separate opposite front approaches, lift the entire SYS coil and reorient
the AUX holder with its whole source/output approach and same-bus bindings.
"""
from pathlib import Path
import json, math, time
from datetime import datetime, timezone
import open_prototype_source_group as B
from open_prototype_path_preflight import screen
from open_prototype_distribution_allocation import input_recipe
from open_prototype_entry_chambers import occupancy

ROOT=B.ROOT;OUT=B.OUT
PLAN=OUT/'source-group-separated-plan.json'
PROOF=OUT/'source-group-separated-gate.json'
EAST=B.EAST;WEST=B.WEST;UP=B.UP;DOWN=B.DOWN;NORTH=B.NORTH;SOUTH=B.SOUTH
line=B.line;check_path=B.check_path;read=B.read;sha=B.sha

def build(aux_family=False):
    tick=time.monotonic();p=B.build()
    for bus,values in [('P_FRONT',[5,2,1,4,3]),('P_AUX',[1,4,3,2,5])]:
        p['permutation'].update({f'{bus}.{i}':f'{bus}.{v}' for i,v in enumerate(values,1)})
    if aux_family:
        p['permutation'].update({f'P_REAR.{i}':f'P_REAR.{v}' for i,v in enumerate([5,1,4,2,3],1)})
    for end in p['body_ends']:
        role=p['permutation'].get(end['original_role'],end['original_role'])
        end.update(current_role=role,datum=p['ports'].get(role))
    loads=occupancy(read(OUT/'routing-scope-plan.json'),p['permutation'])
    assert sum(bool(loads[k]) for k in p['ports'])==86 and all(len(loads[k])<=1 for k in p['ports'])
    m=next(r for r in p['mta'] if r['role']=='MTA_FL')
    m.update(centre_mm=[-25,21,117],source_exit_mm=[-25,3.5,117],output_exit_mm=[-25,38.5,117])
    for r in p['tails']:
        if r['wire']=='W041':
            r['target']='P_FRONT.2'
            r['segments']=B.compose([-25,3.5,117],[('line',[-25,-5.5,117]),
                ('quarter',SOUTH,EAST,6),('line',[-17,-11.5,117]),('quarter',EAST,UP,6),
                ('line',[-11,-11.5,125]),('quarter',UP,NORTH,6),('line',[-11,7.5,131]),
                ('quarter',NORTH,WEST,6),('line',[-38,13.5,131])])
        elif r['wire']=='W026':r['segments']=input_recipe(m['output_exit_mm'],p['ports'][r['target']]['point_mm'],NORTH,7.5)['segments']
        elif r['wire']=='W042':
            r['target']='P_FRONT.1'
            r['segments']=B.compose([0,3.5,117],[('line',[0,.5,117]),('quarter',SOUTH,WEST,6),
                ('line',[-17,-5.5,117]),('quarter',WEST,UP,6),('line',[-23,-5.5,125]),
                ('quarter',UP,NORTH,6),('line',[-23,1,131]),('quarter',NORTH,WEST,6),('line',[-38,7,131])])
        elif aux_family and r['wire']=='W052':
            r['target']='P_REAR.4'
            prebend=[88.3,36.5,117]
            parts=input_recipe(r['segments'][0]['start'],B.add(prebend,[0,6,0]),NORTH,6)['segments']
            parts[-1]['end']=prebend
            q=B.quarter(prebend,NORTH,UP,6)
            r['segments']=parts+[q,line(q['end'],p['ports'][r['target']]['point_mm'])]
        d=check_path(r['segments'],end=p['ports'][r['target']]['point_mm'],min_radius=r['min_radius_mm'])
        r.update(centreline_mm=d,required_blank_mm=d+r['strip_allowance_mm'])
        assert r['required_blank_mm']<=100,(r['wire'],r['required_blank_mm'])
        assert any(e['wire']==r['wire'] and e['current_role']==r['target'] for e in p['body_ends'])
    for r in p['s1_routes']:
        if aux_family and r['wire']=='W064':
            r.update(barrel_mm=[120.2,33,50.877],barrel_direction=DOWN)
            r['segments']=B.compose(r['barrel_mm'],[('line',[120.2,33,41.877]),('half',DOWN,[-50.4,16,0])])
            r['segments']+=input_recipe(r['segments'][-1]['end'],[81.8,51.9,124.123],UP,25.2)['segments']
            q=B.quarter(r['segments'][-1]['end'],UP,WEST,25.2);r['segments'].append(q)
            r['segments']+=input_recipe(q['end'],p['ports'][r['target']]['point_mm'],WEST,25.2)['segments']
        elif r['wire']=='W065':
            if aux_family:r['target']='P_REAR.5'
            r['segments']=B.compose(r['barrel_mm'],[('line',[132.2,33,41.877]),('half',DOWN,[-50.4,6.3,0])])
            r['segments']+=input_recipe(r['segments'][-1]['end'],p['ports'][r['target']]['point_mm'],UP,25.2)['segments']
        elif r['wire']=='W067':
            r['segments']=B.compose(r['barrel_mm'],[('line',[81.077,33,85]),('quarter',WEST,NORTH,25.2),
                ('line',[55.877,68.2,85]),('quarter',NORTH,WEST,25.2),('line',[11.2,93.4,85]),
                ('quarter',WEST,SOUTH,25.2),('quarter',SOUTH,UP,25.2),('line',[-14,43,124.123]),
                ('quarter',UP,EAST,25.2),('half',EAST,[0,-58.4,0])])
            r['segments']+=input_recipe(r['segments'][-1]['end'],p['ports'][r['target']]['point_mm'],WEST,25.2)['segments']
        r['centreline_mm']=check_path(r['segments'],r['barrel_mm'],p['ports'][r['target']]['point_mm'],25.2)
    for h in p['holders']:
        if h['role'] in ('F_HY','F_TY'):
            h['input_target']='P_AUX.4' if h['role']=='F_HY' else 'P_AUX.2'
            h['input_segments']=input_recipe(h['input_mm'],p['ports'][h['input_target']]['point_mm'],EAST,6)['segments']
        if h['role']=='F_AUX':
            # Three millimetres before a bend is NOT the final9mm WAGO grip.
            # The final UP entry still has its own full9mm straight.
            start=[63,42.5,115.5] if aux_family else [66.5,47,115.5]
            if aux_family:h['input_target']='P_REAR.3'
            prebend=[75.8,42.5,117] if aux_family else [82.3,42.5,117]
            virtual=B.add(prebend,[6,0,0])
            parts=input_recipe(start,virtual,EAST,6)['segments']
            parts[-1]['end']=prebend
            q=B.quarter(prebend,EAST,UP,6)
            parts+=[q,line(q['end'],p['ports'][h['input_target']]['point_mm'])]
            output=[12,42.5,115.5] if aux_family else [15.5,47,115.5]
            if aux_family:
                out=B.compose(output,[('line',[9,42.5,115.5]),('quarter',WEST,DOWN,6),('line',[3,42.5,91.5])])
                direction=DOWN
            else:out=[line(output,B.add(output,[-18,0,0]))];direction=WEST
            cut=out[-1]['end']
            h.update(input_mm=start,output_mm=output,axis=WEST,centre_mm=[37.5,42.5,116.5] if aux_family else [41,47,116.5],size_mm=[51,20.25,22],
                input_segments=parts,output_segments=out,output_prefix_mm=check_path(out),
                sleeve_start_mm=B.sub(cut,B.mul(direction,17.25)),sleeve_end_mm=B.add(cut,B.mul(direction,9.25)),
                new_insulation_end_mm=B.add(cut,B.mul(direction,18.25)))
        strip=14 if h['role'] in ('F_PI','F_AUX') else 11
        h['input_blank_mm']=check_path(h['input_segments'],h['input_mm'],p['ports'][h['input_target']]['point_mm'],6)+strip
        assert h['input_blank_mm']<=(50 if strip==14 else 84.5),(h['role'],h['input_blank_mm'])
        check_path(h['output_segments'],h['output_mm'],min_radius=6)
    # Entry directions as well as endpoint IDs are mandatory. A sideways
    # arrival at a downward-facing port is not an acceptable curve recipe.
    for r in p['tails']+p['s1_routes']:
        tangent=B.segment_geometry(r['segments'][-1])[2]
        assert B.dot(tangent,p['ports'][r['target']]['departure'])<-1+1e-7,(r['wire'],'entry direction')
    for h in p['holders']:
        tangent=B.segment_geometry(h['input_segments'][-1])[2]
        assert B.dot(tangent,p['ports'][h['input_target']]['departure'])<-1+1e-7,h['role']
    p.update(changed_cause=('Full lower3 terminal/roof source corridor and reordered REAR supply approaches release the whole WEST-facing AUX input and downward output; source bodies retained'
        if aux_family else 'Coupled complementary front branches, diagonally offset lower S1 coil and lifted full SYS return, sorted AUX bus ports and whole WEST-facing AUX holder; S1/F0/bearings retained'),
        status='SEPARATED_SOURCE_GROUP_NOT_GEOMETRY_ACCEPTANCE',
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in (Path(__file__),Path(B.__file__),
            OUT/'endpoint-plan.json',OUT/'routing-scope-plan.json',OUT/'obstacle-map-current.json')},
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    return p

if __name__=='__main__':
    import sys
    current='--aux-family' in sys.argv
    if current:PLAN=OUT/'source-group-current-plan.json'
    p=build(current);result=screen(p);assert not PLAN.exists(),'No unchanged repeat'
    p['mutual_path_preflight']=result
    PLAN.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],tails=[(r['wire'],round(r['required_blank_mm'],3)) for r in p['tails']],
        inputs=[(h['role'],round(h['input_blank_mm'],3)) for h in p['holders']],
        near_pairs=[{k:r[k] for k in ('a','b','sampled_distance_mm','status')} for r in result['near_pairs']],
        seconds=p['worker_seconds']+result['worker_seconds'])),flush=True)
