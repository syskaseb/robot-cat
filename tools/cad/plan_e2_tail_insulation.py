"""Two E2 solder tails: place insulation transitions at separated source exits.

Use the already planned Temflex165, not a new connector/tubing family. Copper
has R1; a2.8mm tube would self-intersect. Two-layer0.33mm radial wrap allowance
is a PROJECT envelope, not a guaranteed supplier thickness or physical PASS.
"""
import copy,json,math,time
from pathlib import Path
import FreeCAD as A
import Part
import plan_u1_power_grips as P
import plan_current_main_pi_wiring as M
from plan_u1_socket_passives import trim
from check_u1_service_departures import clipped_own_join
ROOT,OUT,SHA=P.ROOT,P.OUT,P.SHA
TAPE_SOURCE='https://multimedia.3m.com/mws/media/2145173O/3m-temflex-vinyl-electrical-tape-165-datasheet-en-ner.pdf'


def tube_envelope(parts,radius):
    w=P.wire(parts);edge=w.Edges[0];at=edge.FirstParameter
    profile=Part.Wire([Part.makeCircle(radius,edge.valueAt(at),edge.tangentAt(at))])
    result=w.makePipeShell([profile],True,False)
    assert result.isValid() and len(result.Solids)==1 and not result.check(True)
    return result


def allocation():
    f=OUT/'u1-socket-passives-resolved.json';old=json.loads(f.read_text())['changed_E2_routes']
    routes=copy.deepcopy(old);envelopes={};rows={}
    # Local jacket wraps failed in the2mm horizontal belt; a77mm tier hits
    # the carrier and board band. Preserve ALL copper paths/receiving parts.
    # Put thick transitions at source exits separated3mm in Z instead.
    # Downstream Cu+0.33wrap is thinner than the old0.925 jacket reservation.
    for n in ('XP02_module','XP03_module'):
        insulated=routes[n];bare=routes[n+'_bare'];cu=bare['radius'];jacket=insulated['radius']
        original=copy.deepcopy(insulated['parts']);first=original[0]
        assert first['kind']=='line' and P.wire([first]).Length>=9
        # Both complete9mm grip lands stay intact. Begin the thick overlap
        # AFTER the jaws, on the first free source bend, not under Module2.
        source_bend=P.wire([original[1]]);cut_distance=3.5
        def arc_piece(lo,hi):
            e=trim(source_bend,lo,hi).Edges[0]
            return dict(kind='arc',start=list(e.valueAt(e.FirstParameter)),
                mid=list(e.valueAt(e.getParameterByLength(e.Length/2))),
                end=list(e.valueAt(e.LastParameter)),length_mm=e.Length)
        prefix=arc_piece(0,cut_distance);suffix=arc_piece(cut_distance,source_bend.Length)
        newtip=prefix['end'];axis=A.Vector(*suffix['mid'])-A.Vector(*newtip)
        downstream=[suffix]+original[2:]
        stripped=P.wire(downstream).Length
        insulated['parts']=original[:1]+[prefix]
        bare['parts']=downstream+bare['parts']
        for route in (insulated,bare):route['guide_mm']=P.wire(route['parts']).Length
        transition=.5;overlap_length=3
        overlap_parts=[arc_piece(cut_distance-overlap_length,cut_distance+transition)]
        overlap_start=overlap_parts[0]['start']
        bare_shape=P.wire(bare['parts']);covered=trim(bare_shape,transition,bare_shape.Length-(85.8202-82.52))
        first_edge=covered.Edges[0]
        profile=Part.Wire([Part.makeCircle(cu+.33,first_edge.valueAt(first_edge.FirstParameter),first_edge.tangentAt(first_edge.FirstParameter))])
        cover=covered.makePipeShell([profile],True,False)
        # Conservative large-radius transition follows the actual R11.1
        # curve, NOT a straight cone intersecting a bend. Both paths share
        # one exact cross-section, so this reserves any real tapered wrap.
        transition_path=P.wire(overlap_parts)
        edge=transition_path.Edges[0]
        thick_profile=Part.Wire([Part.makeCircle(jacket+.33,edge.valueAt(edge.FirstParameter),edge.tangentAt(edge.FirstParameter))])
        overlap=transition_path.makePipeShell([thick_profile],True,False)
        envelope=overlap.fuse(cover).removeSplitter()
        assert envelope.isValid() and len(envelope.Solids)==1 and not envelope.check(True),n
        envelopes[n+'_BoardInsulation']=envelope
        rows[n]=dict(extra_strip_mm=stripped,overlap_mm=overlap_length,transition_mm=transition,
                     jacket_cut_point_world_mm=newtip,overlap_start_world_mm=overlap_start,
                     overlap_parts=overlap_parts,departure_axis_mm=list(edge.tangentAt(edge.FirstParameter)),
                     wrap_stop_world_Z_mm=82.52,PCB_bottom_world_Z_mm=82.7202,
                     project_two_layers_added_radius_mm=.33,nominal_copper_radius_mm=cu,
                     maximum_jacket_wrap_OD_mm=2*(jacket+.33),formed_wrap_OD_mm=2*(cu+.33),
                     raw_tape_strip_mm=[300,10],actual_cut_mm=None)
    return dict(routes=routes,envelopes=envelopes,rows=rows,source=f)


def run():
    tick=time.monotonic();p=allocation();reader,pins,targets,curves=P.latest_scene();pins.add(p['source'])
    receipt=OUT/'u1-power-grips-native.json';r=json.loads(receipt.read_text());model=ROOT/r['native']
    assert SHA(model)==r['native_sha256'];pins.update((receipt,model))
    for n in ('LowerCarrier001','E2Fixture','MAINGrip'):targets[n]=reader.shape(model,n)
    targets.update({'Power/'+n:s for n,s in P.allocation()['bands'].items()});targets.update(P.main_hardware())
    sf=OUT/'u1-service-departures-plan.json';service=json.loads(sf.read_text());pins.add(sf)
    for n,r in service['replacements'].items():curves[n]=(P.wire(r['parts']),r['radius'])
    for n,r in p['routes'].items():
        curves['pwm-branch-checkpoint/'+n]=(P.wire(r['parts']),r['radius'])
    result=dict(status='PENDING',pairs=0,contacts=[],errors=[],selected=False,physical_pass=False,
                scope='Only changed E2 jacket/copper interface and its complete insulation envelope; no new grips or power acceptance.')
    def near(s,t,r=0):
        b=s.BoundBox;b.enlarge(r);return b.intersect(t.BoundBox)
    for n,s in p['envelopes'].items():
        owner=n.replace('_BoardInsulation','')
        for m,t in {**targets,**p['envelopes']}.items():
            if m==n or m in p['envelopes'] and m<n or not near(s,t):continue
            result['pairs']+=1
            try:
                assert t.isValid(),m
                v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids)
                if v>1e-5:result['contacts'].append(dict(a=n,b=m,volume_mm3=v))
            except Exception as e:result['errors'].append(dict(a=n,b=m,error=str(e)))
        for m,(c,rr) in curves.items():
            # Envelope necessarily contains ONLY its own two continuous regions.
            if m in ('pwm-branch-checkpoint/'+owner,'pwm-branch-checkpoint/'+owner+'_bare'):continue
            if not near(s,c,rr):continue
            result['pairs']+=1
            try:
                gap=c.distToShape(s)[0]
                if gap<rr-1e-5:result['contacts'].append(dict(a=n,b=m,distance_mm=gap,required_mm=rr))
            except Exception as e:result['errors'].append(dict(a=n,b=m,error=str(e)))
        print('E2 wrap',n,result['pairs'],len(result['contacts']),round(time.monotonic()-tick,3),flush=True)
        print(json.dumps(result['contacts']),flush=True)
    # Entire changed insulation/copper split checked; no old jacket implicitly
    # remains below the cut, and no reduced metal cross-section invented.
    for name in ('XP02_module','XP02_module_bare','XP03_module','XP03_module_bare'):
        route=p['routes'][name];c=P.wire(route['parts']);radius=route['radius']
        owner=name.removesuffix('_bare')
        for other,s in targets.items():
            if not near(c,s,radius):continue
            result['pairs']+=1
            try:
                assert s.isValid(),other;gap=c.distToShape(s)[0]
                if gap<radius-1e-5:result['contacts'].append(dict(a=name,b=other,distance_mm=gap,required_mm=radius))
            except Exception as e:result['errors'].append(dict(a=name,b=other,error=str(e)))
        for other,(w,rr) in curves.items():
            if other=='pwm-branch-checkpoint/'+name:continue
            if other=='pwm-branch-checkpoint/'+owner+'_bare' and name==owner:
                cc=trim(c,0,c.Length-(radius+rr+.02))
            elif other=='pwm-branch-checkpoint/'+owner and name==owner+'_bare':continue
            else:cc=c
            if not near(cc,w,radius+rr):continue
            result['pairs']+=1
            try:
                gap=cc.distToShape(w)[0]
                if gap<radius+rr-1e-5:result['contacts'].append(dict(a=name,b=other,distance_mm=gap,required_mm=radius+rr))
            except Exception as e:result['errors'].append(dict(a=name,b=other,error=str(e)))
        print('E2 complete changed section',name,result['pairs'],len(result['contacts']),round(time.monotonic()-tick,3),flush=True)
    result.update(status='CHANGED_E2_TAIL_INSULATION_NOMINAL_CLEAR_NATIVE_OPEN' if not result['contacts'] and not result['errors'] else 'E2_TAIL_INSULATION_REJECTED',
                  rows=p['rows'],routes=p['routes'],supplier_source=TAPE_SOURCE,
                  mutual_wrap_gap_mm=min(a.distToShape(b)[0] for i,a in enumerate(p['envelopes'].values()) for b in list(p['envelopes'].values())[i+1:]),
                  catalogue='Temflex165 nominal0.15mm electrical insulating PVC tape; this is NOT guaranteed radial build after wrapping.',
                  project_assumptions=['Two layers with <=0.33mm total radial build; no folded seam exceeding envelope.',
                      'Both complete copper paths, original81/79mm tiers and>=9mm source jacket grip lands retained. Thick overlaps are on the free source bends AFTER the jaws.',
                      'Prepare long jacket strip before forming; retain every strand. Two-layer wrap covers entire stripped region, with3mm intact jacket overlap.',
                      'Continuous wrap stops0.2002mm below PCB; solder joint inspection remains mandatory.',
                      'Insulation-to-insulation touching is allowed without pinching; tiny nominal gap is NOT a guaranteed manufacturing clearance.',
                      'Two300x10mm cut strips, plus retained third E2 wrap and practice/waste; final whole stock still OPEN.',
                      'Wrap is insulation only, never strain relief. Actual adhesion/coverage/creep/fit checked unpowered in phase2.'],
                  native_open=True,source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in pins|{Path(__file__),ROOT/'tools/cad/check_u1_service_departures.py'}}},
                  worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'e2-tail-insulation-current.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('routes','source_sha256')}),flush=True)


if __name__=='__main__':run()
