"""Cheap necessary entry gate before spending on a global route graph.

Proof applies ONLY to actual axis-aligned rectangular support primitives.
With starting tangent fixed, curvature<=1/R bounds transverse movement
before the curve first reaches a nearby solid face. Unknown is NOT clearance.
"""
import json,math,time
from pathlib import Path


def blocked(point,direction,radius,bounds):
    axes=[i for i,v in enumerate(direction) if abs(v)>1e-8]
    if len(axes)!=1 or abs(abs(direction[axes[0]])-1)>1e-8:return None
    axis=axes[0];sign=direction[axis]
    face=bounds[axis] if sign>0 else bounds[axis+3]
    depth=sign*(face-point[axis])+.001
    if not 0<depth<radius:return None
    margins=[min(point[j]-bounds[j],bounds[j+3]-point[j]) for j in range(3) if j!=axis]
    if min(margins)<=0:return None
    # For s<=R*asin(depth/R), axial drop is >=R*sin(s/R),
    # transverse travel <=R*(1-cos(s/R)). Thus the curve reaches
    # the actual face while still inside BOTH transverse intervals.
    lateral=radius-math.sqrt(radius*radius-depth*depth)
    if lateral>=min(margins):return None
    return dict(face_depth_mm=depth,maximum_transverse_before_face_mm=lateral,
                transverse_inside_margins_mm=margins,required_minimum_radius_mm=radius,
                basis='Bounded curvature and fixed tangent force centreline into this actual rectangular solid')


def run(direct=False):
    import FreeCAD as A
    from plan_body36_receiver_space import P
    from plan_axial_source_supports import arm_box
    from canonical_body_rows import normalize,selected_rows
    tick=time.monotonic();mf=P.OUT/'body36-shared-macro-layout.json';macro=json.loads(mf.read_text())
    basefile=P.OUT/'body36-recovery-layout.json';base=json.loads(basefile.read_text())
    selectionfile=P.OUT/'receiver-joint-selection.json'
    rows=normalize(macro,base,selected_rows(selectionfile,P.ROOT))
    if direct:
        from direct_terminal_approaches import simplify
        rows=simplify(rows,macro['remaining_wire_ids'])
    rf=P.OUT/'body36-receiver-support-reservations.json';roots=json.loads(rf.read_text());records=[]
    for name in macro['remaining_wire_ids']:
        row=rows[name]
        for side,point,axis in [('receiver',row['free_end'],row['receiver_outward_axis']),
                                ('source',row['free_start'],row.get('source_free_axis') or row['bodyward_bundle_tangent'])]:
            for group in roots['groups']:
                half=group['arm_half_widths_world_mm']
                for path in group['paths']:
                    for i,(a,b) in enumerate(zip(path['points_mm'],path['points_mm'][1:])):
                        bounds=[min(a[j],b[j])-half[j] for j in range(3)]+[max(a[j],b[j])+half[j] for j in range(3)]
                        proof=blocked(point,axis,10,bounds)
                        if proof is None:continue
                        actual=arm_box(a,b,half);rectangle=P.box(bounds)
                        assert actual.isValid() and len(actual.Solids)==1
                        assert max(actual.cut(rectangle).Volume,rectangle.cut(actual).Volume)<1e-6
                        records.append(dict(wire=name,side=side,point_mm=point,direction=axis,
                            owner=group['name'],group=group['wire'],segment=i,actual_bounds_mm=bounds,**proof))
    selection=json.loads(selectionfile.read_text())
    files=[mf,basefile,rf,selectionfile,P.ROOT/selection['domain_receipt'],Path(__file__),
           Path(__file__).with_name('plan_axial_source_supports.py')]
    if selection['override_receipt']:files.append(P.ROOT/selection['override_receipt'])
    if direct:files.append(Path(__file__).with_name('direct_terminal_approaches.py'))
    result=dict(status='FIXED_ENTRY_CHAMBER_BLOCK_PROVED' if records else 'NO_BOX_ENTRY_BLOCK_PROVED_NOT_CLEARANCE',
        blocked=records,source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False,
        scope='Required projectR10 and fixed tangent, actual rectangular arms ONLY; absence never qualifies a route.')
    (P.OUT/('receiver-entry-current-chambers.json' if direct else 'receiver-entry-chambers.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['blocked'],indent=2));print('seconds',result['worker_seconds'])


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--direct-lands',action='store_true')
    run(parser.parse_args().direct_lands)
