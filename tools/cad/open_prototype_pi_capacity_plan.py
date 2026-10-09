"""Bounded capacity allocation before one next CAD family, no native variants.

Conservative rectangular exclusions are a search restriction, NOT evidence
of material collision. Approximate sampled torso capacity is NOT full shape
acceptance. A shortlist requires the actual changed-interface BRep gate.
This enumerates rigid SYS/PI families with all ports, input, both exits and
covered joint together, rather than another manually guessed scalar pose.
"""
from datetime import datetime,timezone
from pathlib import Path
import itertools,json,math,time
import open_prototype_source_receiving_family as F
import open_prototype_source_group as B
from open_prototype_path_preflight import samples

OUT=F.OUT;ROOT=F.ROOT;DEST=OUT/'pi-family-capacity.json'

def bounds(c,size):return [c[i]-size[i]/2 for i in range(3)]+[c[i]+size[i]/2 for i in range(3)]
def overlap(a,b,margin=.5):
    return all(a[i]<b[i+3]+margin and b[i]<a[i+3]+margin for i in range(3))
def distance_squared(q,b):return sum(max(b[i]-q[i],0,q[i]-b[i+3])**2 for i in range(3))
def rotate(q,turn):
    x,y,z=q
    return ([x,y,z],[-y,x,z],[-x,-y,z],[y,-x,z])[turn]

def family(base,goal,turn,outdir):
    old=next(s for s in base['stations'] if s['role']=='P_SYS')
    pi=next(s for s in base['holders'] if s['role']=='F_PI')
    def point(q):return B.add(goal,rotate(B.sub(q,old['centre_mm']),turn))
    def path(parts):return [{k:point(v) if k in ('start','mid','end') else v for k,v in s.items()} for s in parts]
    swap=lambda size:[size[1],size[0],size[2]] if turn%2 else size
    start=point(pi['output_mm']);a=B.add(start,[0,0,-3])
    q=B.quarter(a,B.DOWN,outdir,6)
    parts=[B.line(start,a),q,B.line(q['end'],B.add(q['end'],B.mul(outdir,18)))]
    cut=parts[-1]['end']
    return dict(SYS=dict(centre_mm=goal,size_mm=swap(old['size_mm'])),
        PI=dict(centre_mm=point(pi['centre_mm']),size_mm=swap(pi['size_mm'])),
        input_segments=path(pi['input_segments']),output_segments=parts,
        sleeve_start_mm=B.sub(cut,B.mul(outdir,17.25)),sleeve_end_mm=B.add(cut,B.mul(outdir,9.25)),
        new_insulation_end_mm=B.add(cut,B.mul(outdir,18.25)),
        whole_pair_turns_z=turn,output_direction=outdir,
        all_SYS_ports={f'P_SYS.{n}':dict(point_mm=point(base['ports'][f'P_SYS.{n}']['point_mm']),
            departure=rotate(base['ports'][f'P_SYS.{n}']['departure'],turn)) for n in range(1,6)})

def main():
    assert not DEST.exists(),'Use received capacity, no unchanged enumeration'
    tick=time.monotonic();base=F.build();records=B.read(OUT/'obstacle-map-current.json')['objects']
    prior=B.read(OUT/'pi-family-space.json')
    assert prior['contacts'] and not prior['errors'],'Capacity follows received rejection'
    exclusions=[dict(name=r['role'],bounds=bounds(r['centre_mm'],r['size_mm']),
        basis='Current nominal rectangular component reservation') for r in base['stations']+base['mta']+base['holders'] if r['role'] not in ('P_SYS','F_PI')]
    for r in records:
        if r['basis'].startswith('Canonical whole-component/reference envelope') or r['name']=='U1UnknownModuleReservation' or r['name'].startswith('F_') and '_CP2' in r['name']:
            exclusions.append(dict(name=r['name'],bounds=r['bounds_mm'],basis='Conservative search exclusion; real BRep required, bbox NOT collision verdict'))
    # Complete transformed S1 body and external operator reservation, not
    # the old vertical module left at its historical placement.
    exclusions += [dict(name='S1/body',bounds=[114.2,-21,89,138.2,21,126],basis='Current whole S1 reservation'),
        dict(name='S1/external_control',bounds=[112.2,-14,126,140.2,14,160],basis='External manual operator search allowance, not internal-shell gate')]
    space=B.read(OUT/'routing-space-map.json')['samples']
    def sampled_capacity(bb):
        for x,y in itertools.product((bb[0],bb[3]),(bb[1],bb[4])):
            r=min(space,key=lambda r:(r['x_mm']-x)**2+(r['y_mm']-y)**2)
            spans=r['torso_z_intervals_mm']
            if not spans or bb[2]<min(s[0] for s in spans)+.5 or bb[5]>max(s[1] for s in spans)-.5:return False
        return True
    counts=dict(whole_pairs=0,case_capacity_exclusions=0,case_budget_exclusions=0,
        complete_prefix_choices=0,prefix_budget_exclusions=0,shortlisted=0)
    choices=[]
    for goal,turn in itertools.product(itertools.product(range(-90,131,10),range(-60,61,10),(125,130,135,140,145,148)),range(4)):
        goal=list(goal);counts['whole_pairs']+=1
        candidate=family(base,goal,turn,B.NORTH)
        cb={n:bounds(candidate[n]['centre_mm'],candidate[n]['size_mm']) for n in ('SYS','PI')}
        if not all(sampled_capacity(b) for b in cb.values()):counts['case_capacity_exclusions']+=1;continue
        if any(overlap(b,e['bounds']) for b in cb.values() for e in exclusions):counts['case_budget_exclusions']+=1;continue
        for outdir in (B.NORTH,B.SOUTH,B.EAST,B.WEST):
            counts['complete_prefix_choices']+=1;c=family(base,goal,turn,outdir)
            paths=[('input',c['input_segments'],2),('output',c['output_segments'],2),
                ('sleeve',[B.line(c['sleeve_start_mm'],c['sleeve_end_mm'])],3),
                ('new_insulation',[B.line(c['output_segments'][-1]['end'],c['new_insulation_end_mm'])],1.05)]
            blocked=False
            for name,parts,radius in paths:
                for segment,q in samples(parts,step=3):
                    if any(distance_squared(q,e['bounds'])<(radius+.5)**2 for e in exclusions):blocked=True;break
                    # Own rectangular case caps only; no hidden route return.
                    for own in ('SYS','PI'):
                        if name=='input' and ((own=='PI' and math.dist(q,parts[0]['start'])<=radius+1e-5) or (own=='SYS' and math.dist(q,parts[-1]['end'])<=radius+1e-5)):continue
                        if name=='output' and own=='PI' and math.dist(q,parts[0]['start'])<=radius+1e-5:continue
                        if distance_squared(q,cb[own])<radius**2:blocked=True;break
                    if blocked:break
                if blocked:break
            if blocked:counts['prefix_budget_exclusions']+=1;continue
            B.check_path(c['input_segments'],min_radius=6);B.check_path(c['output_segments'],min_radius=6)
            c['score']=round(math.dist(goal,[20,0,148])+5*(turn!=1),6)
            choices.append(c)
    choices.sort(key=lambda c:c['score']);counts['shortlisted']=len(choices)
    files=[Path(__file__),Path(F.__file__),OUT/'source-receiving-family-plan.json',
        OUT/'pi-family-space.json',OUT/'obstacle-map-current.json',OUT/'routing-space-map.json']
    result=dict(status='BOUNDED_CAPACITY_SHORTLIST_REQUIRES_ACTUAL_BREP' if choices else 'NO_CAPACITY_IN_CONSERVATIVE_SUBSET_NOT_PROOF_OF_IMPOSSIBILITY',
        counts=counts,shortlist=choices[:3],no_native_variants_generated=True,
        estimated_torso_sections_not_containment_proof=True,
        bbox_search_exclusion_NOT_actual_collision=True,wire_samples_NOT_full_tube=True,
        full_wiring_open=True,selected=False,stage_completed=False,physical_pass=False,
        next='One chosen full family must pass actual changed-case/material/boundary gate; do not enumerate another native variant loop. If none found, change module topology rather than finer grid.',
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())
    DEST.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=result['status'],counts=counts,shortlist=[dict(SYS=c['SYS'],PI=c['PI'],turn=c['whole_pair_turns_z'],output=c['output_direction']) for c in result['shortlist']],seconds=result['worker_seconds'])),flush=True)

if __name__=='__main__':main()
