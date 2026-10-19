"""Whole six-mouth spatial allocation BEFORE another rigid-core gate.

Current fore pose is rejected analytically for W064. One coupled fore-lane
proposal keeps every purchased part and fixes the reason: full bend space,
not a sub-mm witness offset. Native manufacture/whole N01 are not claimed.
"""
import hashlib
import itertools
import json
import math
import sys
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed
from feline_s1_flexible_fans import mouth_curve,wire_shape,saddle_shapes
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement


def allocation():
    src=OUT/'n01-fore-receivers-supported.json';doc,parts,rows=packed(src)
    assert doc['all_current_blockers']['status']=='ALL_CURRENT_POWER_BLOCKERS_RECEIVED_NOT_N01'
    assert not doc['all_current_blockers']['errors']
    core=json.loads((OUT/'n01-supported-fore-layout.json').read_text())
    source=json.loads((OUT/'n01-intrinsic-s1-whole-pose.json').read_text())
    pose=core['S1_changed_pose'];r=np.array(pose['rotation_rows']);mouths=[]
    for e in source['recipes']:
        q=r@(np.array(e['point_mm'])-source['centre_mm'])+pose['centre_mm']
        mouths.append(dict(ref=e['ref'],q=q,d=r@e['departure_axis'],normal=[1,0,0],
            ring='Ref_Material_current_S1_ring_'+{'W064':'3','W065':'6','W067':'2','W068':'5'}[e['ref'].split('/')[0]]+'_0_0',group='S1'))
    for e in core['source_S0_mouths']:
        mouths.append(dict(ref=e['endpoint'],q=np.array(e['new_point_mm']),d=np.array(e['new_departure']),
            normal=[1,0,0],ring=e['source_ring'],group='S0'))
    # Source casing ends before the fixed mount's FULL fore plane plus3mm.
    # The body-wide rail height was not a valid floor in this fore/outboard
    # bay. Reallocate the WHOLE10partS1 lower/fore with all6fans first.
    # S0/Pi/FHY stay unchanged; two opposite-lane hypotheses were rejected
    # cheaply by source/USB/root witnesses before any whole-world run.
    s1delta=np.array([-6.2,0.,-9.]);s0delta=np.zeros(3)
    for n,s in parts.items():
        group=rows[n]['group']
        if group in ('S0','S1'):s.translate(A.Vector(*(s0delta if group=='S0' else s1delta)))
    current_counts={};proposed={}
    for m in mouths:
        old=profiles(m);current_counts[m['ref']]=len(old)
        m['q']=m['q']+(s0delta if m['group']=='S0' else s1delta)
        proposed[m['ref']]=profiles(m)
    return src,doc,parts,rows,mouths,proposed,dict(current_absolute_domains=current_counts,
        current_W064_outer_domain_empty=True,coupled_S1_translation_mm=s1delta.tolist(),coupled_S0_translation_mm=s0delta.tolist(),
        mandatory_straight3_was_project_assumption_not_supplier_data=True,
        S1_bend_starts_tangent_at_actual_barrel_cap_no_insulation_or_R_reduction=True,
        reason='Fullsixmouths beforecore; S1fore/outboardfloor fromactualP0mount not globalrailheight; S0PiFHYunchanged',
        purchased_source_bodies_and_ring_relative_geometry_preserved=True)


def profiles(m):
    candidates=[]
    for sweep,bend in itertools.product((30,45,60,75,90,120,150),range(-180,180,30)):
        row=mouth_curve(m['ref'],m['q'],m['d'],m['normal'],bend,sweep,first=0 if m['group']=='S1' else 3)
        if row['sample_inside_absolute_envelope']:candidates.append(row)
    # Short profiles first; alternatives change full bend plane, not position.
    return candidates


def main():
    tick=time.monotonic();src,parent,parts,rows,mouths,choices,facts=allocation()
    dest=OUT/'n01-six-source-shared-lanes.json';archive=dest.with_suffix('.breps.zip')
    if '--screen' in sys.argv:
        print(json.dumps(dict(**facts,proposed_absolute_domains={n:len(v) for n,v in choices.items()})));return
    assert not dest.exists(),'Receive saved six-source calculation; never duplicate'
    result=dict(status='RUNNING_SIX_SOURCE_WHOLE_SPACE',N01_complete=False,physical_pass=False,selected=False,
        source_sha256={src.relative_to(ROOT).as_posix():sha(src),parent['bundle']:parent['bundle_sha256'],
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
            'tools/cad/feline_s1_flexible_fans.py':sha(ROOT/'tools/cad/feline_s1_flexible_fans.py')},
        **facts,proposed_absolute_domains={n:len(v) for n,v in choices.items()},domains={},rejected={},pairs=0,errors=[],complete_ports=[],parts=[],
        open=['47remainingjointkits','All123portions246ends/4MTA/factorylengths','Roots/tools/assembly/truecontour','N03native'])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    save()
    if any(not v for v in choices.values()):
        result['status']='SIX_SOURCE_ABSOLUTE_DOMAIN_EMPTY_NO_OCC_STARTED';save();return
    from feline_shared_fore_outline import contour,STATIONS
    outerproof=json.loads((OUT/'n01-supported-fore-outline.json').read_text())
    assert sha(ROOT/outerproof['brep'])==outerproof['brep_sha256']
    oldouter=Part.Shape();oldouter.read(str(ROOT/outerproof['brep']))
    stations=[(x,200 if w==196 else w) for x,w in STATIONS]
    outer=contour(stations);surface=Part.makeCompound(outer.Shells)
    outside=oldouter.cut(outer);assert outside.isNull() or outside.isValid()
    assert outside.Volume<1e-5,'Retained107 contour must be a true subset'
    outerpath=dest.with_suffix('.outer.brep');outer.exportBrep(str(outerpath))
    result['outer']=dict(brep=outerpath.relative_to(ROOT).as_posix(),sha256=sha(outerpath),
        dimensions_mm=[325,200,160],stations=stations,old196_outer_subset_mm3=outside.Volume,
        within_approved200_width_NOT_new_body_expansion=True,skin2_plus_air1p25_budget_unchanged=True)
    result['outer_preflight']={};preflight={};qcache=SolidQueries()
    def outer_clear(s):
        assert s.isValid() and s.Solids
        c=s.cut(outer);assert c.isNull() or c.isValid()
        return c.Volume<1e-5 and s.distToShape(surface)[0]>=3.25-1e-5
    for m in mouths:
        ref=m['ref'];preflight[ref]=[];bad={}
        for row in choices[ref]:
            wire=wire_shape(row)
            if not outer_clear(wire):bad['wire_outer']=bad.get('wire_outer',0)+1;continue
            for normal,head in itertools.product((0,90,180,270),(0,90,180,270)):
                kit=saddle_shapes(row,normal,head)
                if qcache.distance(wire,kit['head_budget'])<.2 or qcache.distance(kit['saddle'],kit['head_budget'])<.2:continue
                if any(wire.common(s).Volume>1e-5 for k,s in kit.items() if k!='head_budget'):continue
                if not all(outer_clear(s) for s in kit.values()):bad['kit_outer']=bad.get('kit_outer',0)+1;continue
                preflight[ref].append(dict(row=row,normal=normal,head=head));break
            if len(preflight[ref])>=3:break
        result['outer_preflight'][ref]=dict(full_wire_saddle_tie_head_choices=len(preflight[ref]),rejected=bad)
        save();print('Whole outer first',ref,len(preflight[ref]),flush=True)
    if any(not v for v in preflight.values()):
        result['status']='SIX_SOURCE_FULL_KIT_OUTER_EMPTY_NO_LARGE_WORLD_STARTED';save();return
    from feline_candidate_collision_scene import Scene
    world=Scene()
    for file,groups in (('n01-fore-service-macro.json',{'F_HP','F_TY'}),('n01-fore-topology.json',{'ForeFHAC'})):
        _,extra,rr=packed(OUT/file)
        for n,s in extra.items():
            if rr[n]['group'] in groups:world.parts[n]=s;world.meta[n]=rr[n]
    proof=json.loads((OUT/'n01-flat20-field-modulejoint.json').read_text())
    retired=set(parent['retired_whole_owners'])
    fixed={r['source']:world.parts[r['source']] for r in proof['material_clouds'] if r['category']!='S1_mating_context' and r['source'] not in retired}
    meta={n:world.meta[n] for n in fixed};fixed.update(parts);meta.update(rows)
    _,pwm,pwmrows=packed(OUT/'n01-pwm-board-shelf.json')
    for n,s in pwm.items():
        if n not in fixed:fixed[n]=s;meta[n]=pwmrows[n]
    result['source_sha256'].update(world.pins)
    def budget():
        if time.monotonic()-tick>240:raise TimeoutError('Atomic pair budget; retain completed domains, no whole-source gate from partial')
    def receive(s,m,iswire):
        budget();kind={'kind':'proposal_wire' if iswire else 'proposal_material'}
        outside=s.cut(outer);assert outside.isNull() or outside.isValid()
        if outside.Volume>1e-5 or s.distToShape(surface)[0]<3.25-1e-5:return 'true_outer'
        for n,t in fixed.items():
            minimum=pair_spacing('SourceFan:wire' if iswire else 'SourceFan:saddle',kind,n,meta[n])
            mate=iswire and n==m['ring']
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum and not mate:continue
            budget();qq=s
            if n==world.bus['name']:
                qq=s.copy();qq.Placement=world.bus['inverse']*qq.Placement;t=world.bus['original']
            gap=qcache.distance(qq,t);result['pairs']+=1
            if mate:
                c=qq.common(t);assert c.isNull() or c.isValid()
                if c.Volume>1e-5:return 'own_barrel_penetration:'+n
            elif gap<minimum-1e-6:return 'static:'+n
        for p in world.motion:
            if bbox_lower_bound(s.BoundBox,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
            budget();qq=s.copy();qq.Placement=placement(p['r'],p['t']).inverse()*qq.Placement
            result['pairs']+=1
            if qcache.distance(qq,world.rest[p['name']])<1.25-1e-6:return 'motion:'+p['name']
        return None
    try:
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for m in mouths:
                ref=m['ref'];accepted=[];rejected={};result['domains'][ref]=accepted;result['rejected'][ref]=rejected
                for option in preflight[ref]:
                    row=option['row']
                    wire=wire_shape(row);why=receive(wire,m,True)
                    if why:rejected[why]=rejected.get(why,0)+1;save();continue
                    for normal,head in ((option['normal'],option['head']),):
                        kit=saddle_shapes(row,normal,head)
                        if qcache.distance(wire,kit['head_budget'])<.2 or qcache.distance(kit['saddle'],kit['head_budget'])<.2:continue
                        if any(wire.common(s).Volume>1e-5 for k,s in kit.items() if k!='head_budget'):continue
                        why=next((w for s in kit.values() if (w:=receive(s,m,False))),None)
                        if why:rejected[why]=rejected.get(why,0)+1;continue
                        candidate=dict(row,normal_degrees=normal,head_degrees=head,parts=[])
                        for k,s in {'wire':wire,**kit}.items():
                            raw=s.exportBrepToString().encode();entry=f'{len(result["parts"]):04d}.brep';z.writestr(entry,raw)
                            record=dict(name=ref+':'+str(len(accepted))+':'+k,kind=k,entry=entry,sha256=hashlib.sha256(raw).hexdigest())
                            candidate['parts'].append(record);result['parts'].append(record)
                        accepted.append(candidate);save();break
                    if len(accepted)>=3:break
                result['complete_ports'].append(ref);save();print(ref,len(accepted),'full source-wire/saddle/tie candidates',flush=True)
                if not accepted:
                    result['status']='COUPLED_FORE_LANES_REQUIRED_PORT_EMPTY_REASSESS_CAUSE';break
            else:result['status']='SIX_DOMAINS_RECEIVED_MUTUAL_ASSIGNMENT_CORE_ROOTS_ACCESS_PENDING'
    except TimeoutError as e:result['status']='PARTIAL_SIX_SOURCE_SPACE';result['stop_note']=str(e)
    except Exception as e:result['status']='SIX_SOURCE_ERROR_NOT_CLEARANCE';result['errors'].append(repr(e))
    result.update(bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive));save()
    print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],domains={n:len(v) for n,v in result['domains'].items()},rejected=result['rejected'],errors=result['errors'])),flush=True)


if __name__=='__main__':
    import os
    print('WORKER_PID',os.getpid(),flush=True);main()
