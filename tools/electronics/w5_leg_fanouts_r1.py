"""One coupled 12-loom/36-core body fan-out, not a new splice or release.

Factory cables remain continuous. Reuse selected fuse exit spans and preserve
electrical labels when several cages share one potential. Saved nominal CAD
datums are not measurements of the delivered plugs, copper or insulation.
"""
from datetime import datetime, timezone
from pathlib import Path
import json, math, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'tools/electronics'), str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save, sha
OUT = ROOT/'hardware/electronics/full-cat/w5-leg-fanouts-r1'
PITCH = 6.75
CORE_OD = 2.4
BUNDLE_OD = 5.5
RADIUS = 10.0
CAGE_ORDER = {
    'D_FL': [1,2,3,4,5], 'D_FR': [1,2,3,4,5],
    'D_RL': [1,2,3,4,5], 'D_RR': [3,2,1,4,5],
    'FL_G': [1,2,3,4,5], 'FR_G': [2,1,3,4,5],
    'RL_G': [1,2,3,4,5], 'RR_G': [3,2,1,4,5],
}


def wago_datum(logical, bounds):
    block, suffix = logical.rsplit('.',1)
    slot = CAGE_ORDER[block].index(int(suffix))
    b = bounds[block+'_design']
    side = 1 if b[1] > 0 else -1
    return [b[0]+1.5+PITCH*slot, side*30.5,113.5], -side


def termination(role, wire, body_end):
    if role == 'V':
        return dict(wire=wire, body_end=body_end, part='TE2-520184-2',
                    copper_mm2_range=[.32,.82], tool='TE58628-1',
                    strip_mm=None, end_allowance_assumption_mm=10,
                    strip_source_pending=True,
                    local_bank_exit_is_not_a_splice=True)
    return dict(wire=wire, body_end=body_end, part='WAGO221-415',
                copper_mm2_range=[.14,4], strip_mm=11,
                one_untinned_core_per_cage=True, ferrule=False)


def main():
    import FreeCAD as A
    import Part
    from w5_leg_corridors_r1 import fillet_path
    from w5_selected_owners_r52 import cached
    import w5_bus_restraints_r3 as bus
    started=datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists(), 'Preserve completed attempts'
    OUT.mkdir(parents=True,exist_ok=True)
    paths = {
        'corridors': ROOT/'hardware/electronics/full-cat/w5-leg-corridors-r3/intent.json',
        'corridor_checks': ROOT/'hardware/electronics/full-cat/w5-leg-corridors-r3/checks.json',
        'map': ROOT/'hardware/electronics/full-cat/w5-leg-source-map-r1/interface.json',
        'owners': ROOT/'hardware/electronics/full-cat/w5-installed-r52/owners.json',
        'ends': ROOT/'hardware/electronics/full-cat/servo-fuse-bank-electrical-r2/interface.json',
        'selection': ROOT/'hardware/manufacturing/one-batch-prototype-r53/selection.json',
        'cable': ROOT/'hardware/reference/leg-cable-2026-10-04/facts.json',
    }
    data={key:json.loads(p.read_text(encoding='utf-8')) for key,p in paths.items()}
    assert data['corridor_checks']['status']=='LEG_CORRIDORS_STATIC_CLEAR_FULL_LOOMS_OPEN'
    selected=data['selection']; assert selected['BUS_local_complete'] and not selected['W5_complete']
    bounds={r['key']:r['bounds_mm'] for r in data['owners']['rows']}
    ends={r['id']:r for r in data['ends']['ends'] if r['id'].endswith('.out')}
    old_lengths={r['loom']:r['path_mm'] for r in data['corridor_checks']['routes']}
    bank_lengths=json.loads((ROOT/'hardware/electronics/full-cat/servo-fuse-bank-outputs-r1/checks.json').read_text(encoding='utf-8'))
    bank_lengths={r['id']:r['local_path_mm'] for r in bank_lengths['lengths']}
    assert CORE_OD*(1+2/math.sqrt(3)) <= BUNDLE_OD
    # Three touching core centres form an equilateral triangle. The shared
    # breakout is a location in a continuous loom, never an electrical part.
    offsets={'D':[-CORE_OD/math.sqrt(3),0],
             'G':[CORE_OD/(2*math.sqrt(3)),CORE_OD/2],
             'V':[CORE_OD/(2*math.sqrt(3)),-CORE_OD/2]}
    planned=[]
    for row in data['corridors']['routes']:
        loom=row['loom']; leg=loom[:2]; n=int(loom[2]); side=1 if leg.endswith('L') else -1
        breakout=row['fixed_breakout_provisional_mm']
        for role in ('D','G','V'):
            spec=row['wire_roles'][role]; dx,dy=offsets[role]
            tail=[breakout[0]+dx,breakout[1]+dy,breakout[2]]
            if role=='V':
                end=ends[spec['body_end']]['local_exit_mm']; direction=side
                level=115+6*n; lane=side*(168+12*n)
                points=[end,[end[0],lane,end[2]],[end[0],lane,level],
                        [tail[0],lane,level],[tail[0],tail[1],level],tail]
            else:
                end,direction=wago_datum(spec['body_end'],bounds)
                level=(130 if role=='D' else 158)+6*n
                lane=side*10.5
                points=[end,[end[0],lane,end[2]],[end[0],lane,level],
                        [tail[0],lane,level],[tail[0],tail[1],level],tail]
            planned.append(dict(loom=loom,role=role,wire=spec['wire'],
                servo_end=spec['servo_end'],body_end=spec['body_end'],
                waypoints_mm=points,body_entry_tangent=[0,direction,0],
                termination=termination(role,spec['wire'],spec['body_end']),
                bank_local_path_mm=bank_lengths[spec['wire']] if role=='V' else 0,
                moving_candidate_length_mm=old_lengths[loom]))
    assert len(planned)==36 and len({r['wire'] for r in planned})==36
    save(OUT/'intent.json',dict(status='COUPLED_36_CORE_INTENT_SAVED',routes=planned,
        cable_candidate='Waveshare34172; 900mm, six cables per pack; two packs not selected',
        continuous_factory_looms=12,new_splices=0,second_servo_sockets='NC',
        individual_fuses_retained=12,nominal_core_OD_mm=CORE_OD,
        nominal_bundle_OD_mm=BUNDLE_OD,static_radius_assumption_mm=RADIUS,
        bundle_revision_note='R3 OD5 is insufficient for three OD2.4 cores; OD5.5 needs changed-envelope checks.',
        actual_copper_mm2=None,actual_insulation_OD_mm=None,actual_dynamic_radius_mm=None,
        trim_after_unpowered_fit=True,selected=False,grips_complete=False,
        motion_qualified=False,W5_complete=False,physical_pass=False))
    owners,cache=cached()
    for key in bus.removed_owners(): del owners[key]
    deck=ROOT/selected['current_deck_world']; owners['CandidateDeck']=Part.read(str(deck))
    bus_intent=ROOT/'hardware/electronics/full-cat/w5-bus-pair-r52-r4/intent.json'
    bi=json.loads(bus_intent.read_text(encoding='utf-8'))
    sx=sum(bi['source_lead_datums'][k][0] for k in ('W002','W003'))/2
    owners.update({'R53BUS/'+k:s for k,s in bus.restraints(A,Part,sx).items()})
    for wire in ('W002','W003'): owners['R53BUS/'+wire]=Part.read(str(bus_intent.parent/(wire+'_DESIGN.brep')))
    hits=[];errors=[];pairs=0;built=[];geometries=[];centerlines=[]
    def check(wire,shape,key,other):
        nonlocal pairs
        if not shape.BoundBox.intersect(other.BoundBox):return
        pairs+=1
        try:
            witness=shape.common(other)
            if witness.Volume>1e-5:
                b=witness.BoundBox
                hits.append(dict(wire=wire,owner=key,mm3=witness.Volume,
                    bounds_mm=[getattr(b,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
        except Exception as exc:errors.append(dict(wire=wire,owner=key,error=str(exc)))
    for row in planned:
        try:
            path=fillet_path(A,Part,[A.Vector(*p) for p in row['waypoints_mm']],RADIUS)
            pieces=[Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(CORE_OD/2,
                e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False) for e in path.Edges]
            assert all(s.isValid() and len(s.Solids)==1 for s in pieces)
            shape=Part.makeCompound(pieces)
            for piece in pieces:
                for key,other in owners.items():check(row['wire'],piece,key,other)
            length=path.Length+row['moving_candidate_length_mm']+row['bank_local_path_mm']
            strip=row['termination']['strip_mm']
            if strip is None: strip=row['termination']['end_allowance_assumption_mm']
            blank=math.ceil((length+strip+30)/10)*10
            built.append(dict(wire=row['wire'],loom=row['loom'],role=row['role'],
                body_fanout_mm=path.Length,continuous_external_design_mm=length,
                provisional_far_end_blank_mm=blank,fits_nominal_900_candidate=blank<=900,
                factory_plug_consumed_length_unknown=True))
            geometries.append(shape);centerlines.append(path)
            print('FANOUT',row['wire'],round(path.Length,1),'blank',blank,'hits',len(hits),flush=True)
        except Exception as exc:
            errors.append(dict(wire=row['wire'],stage='build',error=str(exc)))
            print('FANOUT_BUILD_ERROR',row['wire'],str(exc),flush=True)
    for i,shape in enumerate(geometries):
        for j,other in enumerate(geometries[i+1:],i+1):check(built[i]['wire'],shape,built[j]['wire'],other)
    # The bundle diameter changes: inherited OD5 checks cannot approve OD5.5.
    bundles=[]
    for row in data['corridors']['routes']:
        path=fillet_path(A,Part,[A.Vector(*p) for p in row['waypoints_mm']],RADIUS)
        pieces=[Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(BUNDLE_OD/2,
            e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])],True,False) for e in path.Edges]
        bundle=Part.makeCompound(pieces);bundles.append(bundle)
        for piece in pieces:
            for key,other in owners.items():check(row['loom']+'_BUNDLE',piece,key,other)
        for info,shape in zip(built,geometries):
            if info['loom']!=row['loom']:check(row['loom']+'_BUNDLE',bundle,info['wire'],shape)
    for i,bundle in enumerate(bundles):
        for j,other in enumerate(bundles[i+1:],i+1):
            check(data['corridors']['routes'][i]['loom']+'_BUNDLE',bundle,
                  data['corridors']['routes'][j]['loom']+'_BUNDLE',other)
    files=[]
    for name,shapes in [('FANOUTS_WORLD.brep',geometries),('CENTERLINES_WORLD.brep',centerlines),('BUNDLES_WORLD.brep',bundles)]:
        if shapes:
            file=OUT/name;Part.makeCompound(shapes).exportBrep(str(file));files.append(file)
    finished=datetime.now(timezone.utc)
    pins=list(paths.values())+[Path(__file__),ROOT/'tools/electronics/w5_leg_corridors_r1.py',
        ROOT/'tools/electronics/w5_bus_restraints_r3.py',deck,
        ROOT/'hardware/electronics/full-cat/servo-fuse-bank-outputs-r1/checks.json',
        ROOT/'hardware/electronics/full-cat/w5-installed-r52/installed.brep',bus_intent]
    save(OUT/'checks.json',dict(status='COUPLED_LEG_FANOUT_REJECTED' if hits or errors or len(built)!=36 else 'STATIC_FANOUT_ONLY_GRIPS_AND_MOTION_OPEN',
        routes=built,hits=hits,errors=errors,pairs=pairs,
        candidate_900_complete= len(built)==36 and all(r['fits_nominal_900_candidate'] for r in built),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in pins},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in files+[OUT/'intent.json']},
        started_utc=started.isoformat(),finished_utc=finished.isoformat(),
        worker_wall_seconds=(finished-started).total_seconds(),selected=False,
        grips_complete=False,motion_qualified=False,W5_complete=False,physical_pass=False))
    print('FANOUT_RESULT',len(built),len(hits),len(errors),flush=True)


if __name__=='__main__':main()
