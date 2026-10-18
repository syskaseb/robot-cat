"""One shared cross-module gate after complete first-wire preflight passes.

Distance is evidence of air gap, not positive overlap volume. This gate does
not qualify intrinsic supplier mating, new root stacks, tools, walls or motion.
"""
import json
import time
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from plan_feline_central_pi_wedge import packed
from feline_current_scene import load
from check_feline_all_current_lands import near


def main():
    tick=time.monotonic();src=OUT/'n01-coupled-clocked-joints.json';dest=OUT/'n01-coupled-world-static.json'
    assert not dest.exists();p,candidate,rows=packed(src)
    wirefile=OUT/'n01-clocked-wire-gate.json';wireproof=json.loads(wirefile.read_text())
    assert wireproof['status']=='WIRE_SNAPSHOT_CLEAR_WORLD_GATE_OPEN' and not wireproof['errors']
    assert wireproof['source_sha256'][src.relative_to(ROOT).as_posix()]==sha(src)
    for n,h in p['source_sha256'].items():assert sha(ROOT/n)==h,n
    scene,meta,_,_,pins,_=load()
    original_MAIN_strip=scene['StructureReserve:UpperStrip-1']
    assert candidate['RetainedMAINCutForeCap'].cut(original_MAIN_strip).Volume<1e-8, 'Not an inherited subset'
    for n in p['retired_parts']:assert n in scene,n;scene.pop(n);meta.pop(n)
    assert len(scene)==p['retained_base_part_count']
    fixed={n:s for n,s in scene.items() if not meta[n].get('role','').startswith('leg:')}
    curves=[n for n,s in candidate.items() if not s.Solids]
    actual={n:s for n,s in candidate.items() if s.Solids};world={**fixed,**actual}
    bounds={n:s.BoundBox for n,s in world.items()}
    source_map=OUT/'n01-whole-constraint-map.json';mapdata=json.loads(source_map.read_text())
    validity={r['name']:r['valid'] for r in mapdata['parts']}
    def owner(n):
        if n in rows:return rows[n]['group']
        role=meta[n].get('role','')
        return 'TailElectrical' if role in ('TailMechanicalCore','RetainedTailMechanism') else 'retained'
    def kind(n):
        if n in rows:return rows[n]['kind']
        r=meta[n];return 'reservation' if 'reservation' in r.get('kind','') or r.get('role')=='ScaffoldPlanning' else 'material'
    def iswire(n):
        return bool(rows[n].get('wire_owner')) if n in rows else n.startswith(('End:','BankFullPrefix:','Factory:')) or meta[n].get('kind')=='actual_wire' or n in ('W043','W077','W078')
    result=dict(status='RUNNING_ONE_COUPLED_WORLD_STATIC_GATE',selected=False,N01_complete=False,physical_pass=False,
        completed_queries=[],actual_geometry_clearance_failures=[],reservation_holds=[],known_invalid_source_holds=[],
        errors=[],pairs=0,unchanged_source_curves_not_qualified_as_full_jackets=curves,
        intrinsic_module_and_mount_holds=['Flipped Pi spacer/washer/nut stack and own ports/tools not qualified by this cross-module test',
            'PWM full header/power mating source budget remains provisional, not blanket manufacturer geometry',
            'Head+35 was inherited from rejected fore-Pi proposal; do not automatically select this changed head/root pose now that Pi is central',
            'Native root/anchor ownership, all tools/removal, shared corridor capacities and actual walls still OPEN'],
        retained_cut_MAIN_cap_subset_scope='Candidate cap is only a subtraction from unchanged cut MAIN strip. No worse relation to unchanged fixed parts; inherited structural union/root holds remain OPEN, new neighbours checked.',
        source_sha256={**pins,src.relative_to(ROOT).as_posix():sha(src),wirefile.relative_to(ROOT).as_posix():sha(wirefile),
            source_map.relative_to(ROOT).as_posix():sha(source_map),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        whole_wiring_motion_tools_mounts_skin_qualified=False)
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    def known_mouth(n,m):
        if n.startswith('Station:') and not n.endswith(':grip') and rows[m]['group']==rows[n]['group'] and not rows[m].get('wire_owner'):return True
        if n.startswith('PiGPIO:') and not n.endswith(':grip') and m in ('PiBudget:GPIO1992OccupiedHousing','PiBudget:GPIO_header'):return True
        if n=='PiUSBData' and m=='PiBudget:USB_A_data_boot':return True
        if n in ('PiPower:W079','PiPower:W080') and m=='PiBudget:RetainedK1474Boot':return True
        if n.startswith('PWMEnd:') and not n.endswith(':grip') and m=='PWMFullOccupiedHeaderBudget':return True
        if n.endswith(':factory') and rows[n]['group'] in ('F_HY','F_HP','F_TY') and m==rows[n]['group']+':case':return True
        return n.startswith('F_PWM:') and n.endswith('_first_bend') and m=='F_PWM:case'
    seen=set();save()
    try:
        for n,s in actual.items():
            for m,t in world.items():
                if n==m or not near(bounds[n],bounds[m],1.25):continue
                if m in actual:
                    if iswire(n) and iswire(m):continue # Closed by the pinned complete wire preflight.
                    if owner(n)==owner(m) and not iswire(n) and not iswire(m):continue # Intrinsic stack is an explicit OPEN hold, not a PASS.
                    if iswire(m) and not iswire(n):continue # The reverse iteration tests it once.
                    if iswire(n) and known_mouth(n,m):continue
                elif n=='RetainedMAINCutForeCap':continue # Exact inherited subset, not a rebuilt box.
                if owner(n)==owner(m) and owner(n)=='TailElectrical':continue # Selected unchanged local mechanical mates.
                pair=tuple(sorted((n,m)))
                if pair in seen:continue
                seen.add(pair)
                if time.monotonic()-tick>240:raise TimeoutError('240s shared gate; preserve every completed query')
                if not validity.get(m,True) or not t.isValid():
                    result['known_invalid_source_holds'].append(dict(a=n,b=m,not_clearance=True));continue
                minimum=.2 if iswire(n) and iswire(m) else 1.25
                gap=s.distToShape(t)[0];result['pairs']+=1
                row=dict(a=n,b=m,gap_mm=gap,minimum_mm=minimum,group_a=owner(n),group_b=owner(m),positive_overlap_volume_not_claimed=True)
                result['completed_queries'].append(row)
                if gap<minimum-1e-5:
                    (result['reservation_holds'] if 'reservation' in kind(n) or 'reservation' in kind(m) else result['actual_geometry_clearance_failures']).append(row)
                if result['pairs']%10==0:save()
            print('Received',n,'pairs',result['pairs'],'material',len(result['actual_geometry_clearance_failures']),
                'reserved',len(result['reservation_holds']),flush=True);save()
        result['status']='COUPLED_WORLD_STATIC_REJECTED_NO_MOTION_GATE' if result['actual_geometry_clearance_failures'] or result['reservation_holds'] or result['known_invalid_source_holds'] or result['errors'] else 'COUPLED_CROSS_MODULE_STATIC_CLEAR_INTRINSIC_ROOTS_TOOLS_WALLS_OPEN'
    except Exception as e:result['status']='PARTIAL_COUPLED_WORLD_STATIC_GATE';result['errors'].append(repr(e))
    save();print(json.dumps(dict(status=result['status'],pairs=result['pairs'],material_failures=len(result['actual_geometry_clearance_failures']),
        reservation_holds=len(result['reservation_holds']),invalid_holds=len(result['known_invalid_source_holds']),
        errors=result['errors'],seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
