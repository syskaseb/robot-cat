"""Bind the TEN occupied feed ends to real existing straight insulation.

No rerouting or invented terminal coordinates. The short fixed lacing grip
remains a proposal until common-material/native/stock gates close.
"""
import copy,hashlib,json,math,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint'

def straight_at(point,axis,segments):
    for si,segment in enumerate(segments):
        for pi,p in enumerate(segment['parts']):
            if p['kind']!='line':continue
            delta=[b-a for a,b in zip(p['start'],p['end'])];length=math.sqrt(sum(x*x for x in delta))
            if length<8.5:continue
            direction=[x/length for x in delta]
            if abs(abs(sum(a*b for a,b in zip(direction,axis)))-1)>1e-7:continue
            # Entire reserved3mm land is between terminal+5.5 and+8.5mm.
            for offset in (5.5,8.5):
                q=[a+offset*b for a,b in zip(point,axis)]
                t=sum((x-a)*d for x,a,d in zip(q,p['start'],direction))
                projected=[a+t*d for a,d in zip(p['start'],direction)]
                if t<-1e-6 or t>length+1e-6 or math.dist(q,projected)>1e-6:break
            else:return dict(segment_index=si,part_index=pi,existing_straight=copy.deepcopy(p))
    return None

def prepare():
    tick=time.monotonic();pins={}
    def read(p):
        pins[p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
        return json.loads(p.read_text())
    selected=read(OUT/'receiver-joint-selection.json');domains=read(ROOT/selected['domain_receipt'])['qualified_options']
    if selected['override_receipt']:domains.update(read(ROOT/selected['override_receipt'])['replacement_options'])
    inventory=read(OUT/'retained-body-guides-inventory.json')['guides']
    bindings=read(OUT/'retained19-current-end-bindings.json')['bindings']
    facts=read(ROOT/'hardware/reference/alpha-802534b-2026-10-12/dimensions.json')
    records=[];missing=[]
    for name,index in selected['selected_options'].items():
        group=domains[name][index]
        if group['kind']!='triple':continue
        axis=[-x for x in group['lands'][0]['axis']]
        for feed in group['feeds']:
            wire=feed['wire'];point=feed['point_world_mm'];guide=inventory[wire]
            assert min(math.dist(point,e['point_world_mm']) for e in bindings[wire]['ends'])<1e-6,(name,wire)
            land=straight_at(point,axis,guide['segments'])
            r=dict(group=name,wire=wire,owner=group['owner'],terminal_world_mm=point,
                outward_axis=axis,project_wire_radius_mm=feed['radius_mm'],
                short_fixed_land_mm=3,land_from_terminal_mm=[5.5,8.5],
                centre_world_mm=[x+7*a for x,a in zip(point,axis)],
                existing_route_recipe=guide['recipe_file'],land=land,
                integral_into_existing_print=True,new_separate_prints=0,new_screws=0,
                lacing_blank_mm=150,lacing_candidate_part=facts['part'],
                lacing_section_max_mm=[facts['project_max_thickness_mm'],facts['project_max_width_mm']],
                independent_of_WAGO_glue_and_feed_clearance_hole=True)
            records.append(r)
            if land is None:missing.append(dict(group=name,wire=wire,reason='No real straight covers the proposed insulation land'))
    assert len(records)==10
    pins[Path(__file__).relative_to(ROOT).as_posix()]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result=dict(status='TEN_FEED_LANDS_BOUND_COMMON_MATERIAL_NATIVE_STOCK_OPEN' if not missing else 'TEN_FEED_LAND_BINDING_OPEN',
        restraints=records,missing=missing,quantities=dict(feed_ends=10,additional_separate_prints=0,additional_screws=0,
            lacing_blanks=10,lacing_nominal_total_mm=1500,practice_allowance_not_selected=True),
        source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False,
        open=['Full common body/band clearance and integration into rooted carrier',
            'Selected lacing stock;500yard spool is not selected',
            'Native editability/export/mounting sequence',
            'Unpowered delivered grip/insulation/creep trial;3mm is NOT a9mm pressure land'])
    return result

if __name__=='__main__':
    p=prepare();assert not p['missing'],p['missing']
    (OUT/'retained-feed-restraints-plan.json').write_text(json.dumps(p,indent=2)+'\n')
    print(json.dumps({k:p[k] for k in ('status','quantities','worker_seconds')}))
