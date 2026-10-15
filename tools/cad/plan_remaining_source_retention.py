"""One shared allocation of remaining source ends from retained recipes.

No guessed roots, no new routes, no clamping the bare lap or its sleeve.
Actual structural attachment/common-material gate precedes native detail.
"""
import json,math,time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,OUT,SHA


def land(parts,index,length,offset=0):
    p=parts[index];assert p['kind']=='line' and length>=3 and offset>=0
    assert offset+length<=p['length_mm']+1e-6
    axis=[(b-a)/p['length_mm'] for a,b in zip(p['start'],p['end'])]
    centre=[a+u*(offset+length/2) for a,u in zip(p['start'],axis)]
    return dict(centre_world_mm=centre,axis=axis,land_mm=length,
                preceding_guide_mm=sum(q['length_mm'] for q in parts[:index])+offset,
                recipe_part_index=index,offset_on_part_mm=offset)


def run():
    tick=time.monotonic();f=OUT/'retained-body-guides-inventory.json';inv=json.loads(f.read_text())
    bf=OUT/'retained19-current-end-bindings.json';bindings=json.loads(bf.read_text())
    mp=OUT/'main-pi-plan.json';main=json.loads(mp.read_text())
    pins={f,bf,mp,Path(__file__)};groups=[]
    def add(wire,segment,index,length,ends,assembly,normal,offset=0):
        g=inv['guides'][wire];p=g['segments'][segment]
        pins.add(OUT/g['recipe_file'])
        q=land(p['parts'],index,length,offset)
        groups.append(dict(id=wire+'_'+str(segment)+'_'+str(index),wire=wire,segment=segment,
            source_recipe=g['recipe_file'],project_insulation_radius_mm=p['radius_mm'],
            bound_ends=ends,assembly_group=assembly,normal=normal,**q,
            project_lacing_blank_mm=150,structural_root=None,root_and_contacts_qualified=False,
            retention_creep_delivered_fit_gate_open=True))
    add('W001',0,0,3,['BAT.minus'],'LOWER_SOURCE_CARRIAGE',[0,-1,0])
    add('W075',0,0,9,['BAT.plus','F0.in'],'LOWER_SOURCE_CARRIAGE',[0,-1,0],8)
    add('W076',0,0,9,['F0.out'],'LOWER_SOURCE_CARRIAGE',[0,-1,0])
    add('W076',0,len(inv['guides']['W076']['segments'][0]['parts'])-1,9,
        ['POST_F0.1'],'LOWER_SOURCE_CARRIAGE',[0,-1,0],9)
    add('W076',1,0,9,['POST_F0.2'],'LOWER_SOURCE_CARRIAGE',[0,-1,0])
    add('W076',1,len(inv['guides']['W076']['segments'][1]['parts'])-1,9,
        ['S0.in'],'S0_SOURCE_MOUNT',[0,0,-1])
    parts=inv['guides']['W066']['segments'][0]['parts']
    first=next(i for i,p in enumerate(parts) if p['kind']=='line' and p['length_mm']>=9)
    add('W066',0,first,9,['S0.out'],'SOURCE_RECEIVING_CARRIER',[0,0,-1])
    add('W066',0,len(parts)-1,3,['P_SYS.1'],'SOURCE_RECEIVING_CARRIER',[0,0,-1])
    # Factory lead is short: one3mm insulated grip before its R6 bend
    # supports both fuse exit and the nearby protected lap, not a fictitious9mm.
    add('W077',0,0,3,['F_PI.out','SPLICE_PI.16'],'SOURCE_RECEIVING_CARRIER',[1,0,0])
    # The first8mm of W078 is the opposed bare lap. The20mm sleeve extends
    # toY66.589. Only its final3mm straight is outside the sleeve.
    sleeve=main['factory_custom_overlap']['sleeve_bounds_mm']
    parts=inv['guides']['W078']['segments'][0]['parts'];p=parts[0]
    assert abs(p['end'][1]-(sleeve[1]-3))<1e-6
    add('W078',0,0,3,['SPLICE_PI.18'],'SOURCE_RECEIVING_CARRIER',[1,0,0],p['length_mm']-3)
    custom=groups[-1];assert custom['centre_world_mm'][1]+1.5<=sleeve[1]+1e-6
    ends=[e for g in groups for e in g['bound_ends']]
    assert len(groups)==10 and len(ends)==len(set(ends))==12
    result=dict(status='REMAINING_SOURCE_SHARED_LANDS_ROOTS_AND_MATERIAL_GATE_OPEN',groups=groups,
        retained_outer_ends=10,inline_POST_F0_ends=2,lacing_candidate_blanks=10,lacing_candidate_total_mm=1500,
        architecture=['LOWER_SOURCE_CARRIAGE: one removable rigid support for BAT/F0/post-F0 joint and their insulation lands; attach to measured structural member, not electrical connector.',
                      'S0_SOURCE_MOUNT: retain known top mounting pattern, adjustable terminal/insulation interface with explicit delivery-fit gate; never carve nominal cylinder into an invented terminal bay.',
                      'SOURCE_RECEIVING_CARRIER: allocate P_SYS/F_PI cases, both source sides, short lap and all receiving feeds together; preserve Upper G1/G2 and complete36 routes.'],
        assembly=['Mount structural parents and the source carriers before wiring.',
                  'Install connector cases and intact factory leads; retain W075 as one unbroken prefuse segment.',
                  'Prepare protected lap and post-F0 joint on bench, then bind ONLY insulation outside bare/sleeve regions.',
                  'Lace remaining jackets; support terminals while opening levers. Remove via reverse assembly, not promised hot-swap.'],
        open=['Actual structural roots and one shared material/access check including full36/19/25 interfaces',
              'Native editable parts, hardware, stock and complete W5/M4 selection',
              'Delivered source terminal bay and retention checks, no power'],
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in pins},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    (OUT/'remaining-source-retention-plan.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(groups=len(groups),outer_ends=10,inline_ends=2,worker_seconds=result['worker_seconds'])))


if __name__=='__main__':run()
