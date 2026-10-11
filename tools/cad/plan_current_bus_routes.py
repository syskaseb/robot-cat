"""Both BUS cores in the same nominal free-space plan as all48 leg paths.

H5 splits into two upward returns BEFORE crossing the existing low wire belt.
One factory keyed plug is retained and V is removed. Cable selection, actual
plug/copper and native passage/grips remain gates, not implied supplier facts.
"""
import json,time,math,itertools
from pathlib import Path
from route_current_leg_fanouts import ROOT,OUT,SHA,Space,search,sampling_parts
from plan_current_joined_leg_looms import leave_port,reverse_parts,exact_quarter
from plan_current_mta_interfaces import line,add,mul
from screen_current_remaining_routes import route_rows
from screen_current_leg_fanout_channels import rows_for
from screen_current_moving_looms import only_new_pairs
from open_prototype_path_preflight import samples
U=[0,0,1];W=[-1,0,0];S=[0,-1,0];N=[0,1,0];E=[1,0,0]

class ReservedSpace(Space):
    """Chosen functional keepouts, not bbox claims of material collision."""
    def __init__(self):super().__init__();self.reservations=[];self.material_grid={};self.face_cell=12
    def load_faces(self,rows):
        for index,row in enumerate(rows):
            b=row['bounds_mm'];b=[v+(-1 if i<3 else 1) for i,v in enumerate(b)]
            ranges=[range(math.floor(b[j]/self.face_cell),math.floor(b[j+3]/self.face_cell)+1) for j in range(3)]
            for key in itertools.product(*ranges):self.material_grid.setdefault(key,[]).append(b)
    def clear(self,parts,ignore=(),margin=.7,root=None):
        for _,point in samples(sampling_parts(parts),step=1):
            if any(all(b[j]-1-margin<point[j]<b[j+3]+1+margin for j in range(3)) for b in self.reservations):return False
            key=tuple(math.floor(v/self.face_cell) for v in point)
            if any(all(b[j]+1e-8<point[j]<b[j+3]-1e-8 for j in range(3)) for b in self.material_grid.get(key,())):return False
        return super().clear(parts,ignore,margin,root)

def run():
    tick=time.monotonic();bf=OUT/'BUS-port-binding.json';ports=json.loads(bf.read_text())
    for n,h in ports['source_sha256'].items():assert SHA(ROOT/n)==h,n
    cf=OUT/'leg-fanout-channels-plan.json';channels=json.loads(cf.read_text())
    lf=OUT/'joined-leg-looms-plan.json';looms=json.loads(lf.read_text())
    sf=OUT/'leg-fanout-channels-screen.json';gate=json.loads(sf.read_text())
    assert not gate['rejected']
    for q in (channels,looms,gate):
        for n,h in q['source_sha256'].items():assert SHA(ROOT/n)==h,n
    fixed,pins=route_rows(tuple(OUT/(t+'-plan.json') for t in ('ground-tree','data-bridges','positive-source','s0-in-extension')))
    hf=OUT/'head-wire-screen-reference.json';heads=json.loads(hf.read_text())
    legrows,_=rows_for(looms['looms'],channels['routes']);old=list(fixed.values())+heads['rows']+legrows
    space=ReservedSpace()
    for row in old:space.insert(row)
    ef=OUT/'harness-interfaces-plan.json';ends={r['id']:r for r in json.loads(ef.read_text())['body_conductors']}
    cols={r['role']:r['world_header_top_reference_mm'] for r in ports['ports']['H5']['pin_columns']}
    routes={};errors=[];prefixes={};receiving={}
    for wid,role in [('W002','D'),('W003','G')]:
        end=next(e for e in ends[wid]['current_ends'] if not e['role'].startswith('BUS'))
        x,y,z=cols[role];a=[x,y,z+14.05]
        # The Z79..81 XS23/XP02 belt blocks horizontal WEST and EAST runs.
        # Rise through separate return corridors BEFORE crossing this belt.
        # These are free cores, not a fictional unbroken two-core jacket.
        # Common SOUTH-WEST direction preserves perpendicular spacing of
        # the5mm-separated free cores (unlike a shared SOUTH straight).
        direction=[-2**-.5,-2**-.5,0]
        p=[exact_quarter(a,U,direction,10)]
        p.append(exact_quarter(p[-1]['end'],direction,U,10))
        p.append(line(p[-1]['end'],add(p[-1]['end'],mul(U,9))))
        if role=='D':target=leave_port(end['point_mm'],end['departure'],N)
        else:
            target=[line(end['point_mm'],add(end['point_mm'],mul(E,9)))]
            target.append(exact_quarter(target[-1]['end'],E,U,10))
        prefixes[wid]=p;receiving[wid]=target
        if not space.clear(p,margin=0):errors.append(dict(wire=wid,cause='BUS_COMMON_PREFIX_OCCUPIED'))
        if not space.clear(target,margin=0):errors.append(dict(wire=wid,cause='RECEIVING_PREFIX_OCCUPIED'))
    # Reserve both complete end approaches before either middle is routed.
    prefixrows=[]
    for wid in prefixes:
        for suffix,p in [('source',prefixes[wid]),('receiver',receiving[wid])]:
            row=dict(wire=wid+'/'+suffix,OD_mm=2,segments=p);prefixrows.append(row);space.insert(row)
    for hit in only_new_pairs([],prefixrows):
        if hit['status']=='REJECT_PLANNING_PROXIMITY':errors.append(dict(cause='BUS_PREFIX_PAIR_OCCUPIED',pair=hit))
    if not errors:
        vf=OUT/'BUS-material-routing-space.json';spatial=json.loads(vf.read_text());pins.add(vf)
        assert spatial['status']=='CURRENT_MATERIAL_SURFACE_ROUTING_RESERVATIONS_ONLY'
        assert spatial['geometry_recipe']['source_prefix_first_three']=={n:q[:3] for n,q in prefixes.items()}
        for n,h in spatial['source_sha256'].items():assert SHA(ROOT/n)==h,n
        space.load_faces(spatial['boxes'])
        mf=OUT/'mta-interface-plan.json';mta=json.loads(mf.read_text());pins.add(mf)
        pf=OUT/'main-source-plan.json';sources=json.loads(pf.read_text());pins.add(pf)
        space.reservations=[[4,-50,114,142,24,174],sources['P_FRONT']['casing_mm']]
        space.reservations.extend(q['casing_mm'] for q in mta['holders']+mta['joints'])
        for wid in prefixes:
            fixedlength=sum(q['length_mm'] for q in prefixes[wid]+receiving[wid])
            middle,states=search(space,prefixes[wid][-1]['end'],receiving[wid][-1]['end'],
                900-50-14.05-21-fixedlength,0,(wid+'/source',wid+'/receiver'))
            if middle is None:errors.append(dict(wire=wid,cause='NO_COMMON_FREE_BUS_CHANNEL',states=states));break
            whole=prefixes[wid]+middle+reverse_parts(receiving[wid]);length=sum(q['length_mm'] for q in whole)
            routes[wid]=dict(parts=whole,guide_mm=length,radius_mm=1,project_R_mm=10,search_states=states,
                minimum_factory_blank_project_mm=length+14.05+21,
                three_hundred_mm_recipe_fits=length+14.05+21<=300,
                endpoints=['BUS.H5.'+('D' if wid=='W002' else 'G'),ends[wid]['roles'][1]],
                actual_cut_mm=None,selected=False)
            space.insert(dict(wire=wid,OD_mm=2,segments=whole))
    near=only_new_pairs(old,[dict(wire=n,OD_mm=2,segments=sampling_parts(r['parts'])) for n,r in routes.items()]) if routes else only_new_pairs(old,prefixrows)
    errors.extend(dict(cause='WHOLE_PLAN_PROXIMITY',pair=q) for q in near if q['status']=='REJECT_PLANNING_PROXIMITY')
    result=dict(status='REJECTED_BUS_SHARED_PLAN' if errors else 'BUS_SHARED_NOMINAL_CHANNELS_ONLY',
        routes=routes,rejected=errors,near_pairs=near,source_prefixes=prefixes,receiving_prefixes=receiving,
        native_passage='UpperCarrier H5 two upward-return corridors, dimensions after actual material gate',
        functional_search_reservations_mm=space.reservations,
        reservations_are_conservative_planning_not_material_collision_evidence=True,
        rejected_architecture='H3 WEST hits upper hardware; H5 horizontal WEST and EAST cross the complete XS23/XP02 low wire belt. Split the free cores and rise BEFORE crossing that belt, not more horizontal offsets.',
        delivery_gates=['H5 keyed plug and received D/V/G continuity','Remove V contact AND entire V wire',
          'Project OD2/R10/14.05plug allowance are NOT catalog data','Actual Cu compatible with221-415; no tinned tips',
          '34171/300mm current recipe may not fit;34172/900mm only unselected candidate',
          'Shared independent cable grips, passage, service and material gate OPEN'],
        factory_cables_installed=1,bought_pack_qty=None,selected=False,W5_complete=False,physical_pass=False,
        worker_seconds=time.monotonic()-tick,
        source_sha256={q.relative_to(ROOT).as_posix():SHA(q) for q in pins|{bf,cf,lf,sf,hf,ef,Path(__file__),ROOT/'tools/cad/route_current_leg_fanouts.py'}})
    (OUT/'BUS-routes-plan.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],routes={n:r['guide_mm'] for n,r in routes.items()},rejected=errors,seconds=result['worker_seconds'])),flush=True)
    return result

if __name__=='__main__':run()
