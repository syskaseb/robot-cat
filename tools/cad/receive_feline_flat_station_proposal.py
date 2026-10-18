"""Exact mandatory flat-unit receipt before repeating a blocked common CSP.

Uses the SAME fixed scene as whole20 field (identity-context P_SYS is owned
by this unit). Planned boxes/clamps are valid planning BReps, not native CAD
features or manufacturer internals. Preserves all known earlier holds.
"""
import hashlib
import json
import math
import sys
import time
import zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_candidate_collision_scene import Scene
from feline_flat_station_templates import build,self_wire_gap,shared_rail_bounds
from feline_solid_distance import distance
from check_feline_all_current_lands import near


def restore(scene,proof):
    retired=set(proof['old_station_parts_retired'])|set(proof['conditional_frame_replacement'])
    for n in retired:scene.parts.pop(n,None);scene.meta.pop(n,None)
    for filename,groups in (('n01-fore-service-macro.json',{'S1Rigid','F_HP','F_TY'}),('n01-fore-topology.json',{'ForeFHAC'})):
        doc=json.loads((OUT/filename).read_text());bundle=ROOT/doc['bundle'];assert sha(bundle)==doc['bundle_sha256']
        with zipfile.ZipFile(bundle) as z:
            for r in doc['parts']:
                if r['group'] not in groups or '_S1_ring_' in r['name']:continue
                raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
                s=Part.Shape();s.importBrepFromString(raw.decode('utf-8'));assert s.isValid() and s.Solids
                scene.parts[r['name']]=s;scene.meta[r['name']]=dict(kind='wire' if r['wire'] else 'material')
    assert set(scene.parts)=={r['source'] for r in proof['material_clouds']},'Fixed scene must match whole field EXACTLY'
    scene.bounds={n:s.BoundBox for n,s in scene.parts.items()}


def makebox(bounds):
    lo,hi=bounds
    return Part.makeBox(*(hi-lo),A.Vector(*lo))


def wire_shape(w):
    q=A.Vector(*w['point_mm']);d=A.Vector(*w['departure_axis']);b=A.Vector(*w['bend_unit']);R=w['R_mm']
    a=q+d*w['first_mm'];mid=a+d*(R/2**.5)+b*(R*(1-1/2**.5));end=a+d*R+b*R
    curve=Part.Wire([Part.makeLine(q,a),Part.Arc(a,mid,end).toShape(),Part.makeLine(end,end+b*9)])
    result=curve.makePipeShell([Part.Wire([Part.makeCircle(w['radius'],q,d)])],True,False)
    assert result.isValid() and len(result.Solids)==1
    return result


def main():
    tick=time.monotonic();ref='P_SYS';r2=any(a in sys.argv for a in ('--owner-r2','--owner-complete'));suffix='-owned' if '--owner-complete' in sys.argv else '-r2' if r2 else ''
    dest=OUT/f'n01-flat20-mandatory-{ref}{suffix}.json';assert not dest.exists()
    planfile=OUT/'n01-flat-station-architecture.json';plan=json.loads(planfile.read_text())
    proofpath=OUT/('n01-flat20-field'+suffix+'.json');proof=json.loads(proofpath.read_text())
    for n,h in proof['source_sha256'].items():assert sha(ROOT/n)==h,n
    station=next(s for s in plan['stations'] if s['ref']==ref);module=build(station,'inner',1,-1)
    assert module['fixed_identity'] and self_wire_gap(module)>=-1e-6
    scene=Scene();owned_case=scene.parts[station['case_name']].copy();restore(scene,proof)
    proposal={};rows={}
    for w in module['wires']:
        n='Flat:'+w['endpoint'];proposal[n]=wire_shape(w);rows[n]=dict(wire=True,kind='wire',recipe={k:v for k,v in w.items() if k!='points'})
    for r in module['boxes']:
        n='Flat:'+ref+':'+r['name'];s=makebox(r['bounds'])
        if r['name']=='source_case':
            bb=owned_case.BoundBox;assert np.allclose([bb.XMin,bb.YMin,bb.ZMin],r['bounds'][0],atol=1e-5)
            assert abs(owned_case.Volume-s.Volume)<1e-5
            s=owned_case
        if r['name']=='common_channelled_cap_exterior':
            for w in module['wires']+module.get('reused_jacket_lands',[]):
                q=A.Vector(*w['point_mm']);d=A.Vector(*w['departure_axis'])
                s=s.cut(Part.makeCylinder(w['radius'],11,q-d,d))
            assert s.isValid() and s.Solids
        proposal[n]=s;rows[n]=dict(wire=False,kind=('identity_case' if r['kind']==0 else 'planned_carrier_root' if r['kind']==3 else 'planned_clamp'))
    for side,bounds in zip((-1,1),shared_rail_bounds()):
        n='SharedRail:'+str(side);proposal[n]=makebox(bounds)
        rows[n]=dict(wire=False,kind='planned_common_rail_root_not_approved')
    pins={**proof['source_sha256'],**scene.pins}
    for p in (planfile,proofpath,Path(__file__),Path(__file__).with_name('feline_flat_station_templates.py')):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    result=dict(status='RUNNING_EXACT_MANDATORY_FLAT_UNIT',selected=False,N01_complete=False,physical_pass=False,
        source_sha256=pins,station=ref,case_identity_unchanged=True,protected_W043_not_rerouted=True,
        actual_world_solid_children_gap_method=True,source_concentric_fans_self_preflight_clear=True,
        conditional_frame_replacement_remains_OPEN=True,old_fore_ring_wall_and_S1_operator_holds_NOT_cleared=True,
        full_other19stations_S1all8HELU123portions246ends_tools_stock_OPEN=True,
        frame_family=module['frame_family'],all4_P_SYS_jackets_in_replacement=True,
        receipts=[],failures=[],errors=[],bundle=None)
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    save()
    try:
        for n,s in proposal.items():
            if time.monotonic()-tick>180:raise TimeoutError('180s one mandatory unit, preserve completed exact receipts')
            if rows[n]['kind']=='identity_case':
                result['receipts'].append(dict(part=n,unchanged_identity_case_not_requeried=True));continue
            mate=None
            if r2 and n=='Flat:P_SYS:common_channelled_cap_exterior':
                oldwire=scene.parts['W043'];q=A.Vector(4.55,4,48.5);d=A.Vector(-1,0,0)
                faces=[f for f in oldwire.Faces if type(f.Surface).__name__=='Cylinder'
                    and abs(f.Surface.Radius-1.7)<1e-5 and abs(f.Surface.Axis.x)>.999
                    and (q-f.Surface.Center).cross(f.Surface.Axis).Length<1e-5
                    and f.BoundBox.XMin<=-4.45+1e-5 and f.BoundBox.XMax>=4.55-1e-5]
                assert faces,'Verify actual saved W043 straight/cylinder BEFORE declaring the clamp mate'
                volume=s.common(oldwire).Volume;assert volume<1e-5,'No conductor/jacket material penetration'
                bb=s.BoundBox;throat=Part.makeBox(bb.XLength+5,500,500,A.Vector(bb.XMin-2.5,-250,-250))
                remaining=oldwire.cut(throat);assert remaining.isValid() and remaining.Solids
                g=distance(s,remaining);assert g>=1.25-1e-5
                mate=dict(wire='W043',source_radius_mm=1.7,actual_source_cylinder_verified=True,
                    nominal_grip_mm=9,source_straight_mm=module['reused_jacket_lands'][0]['source_straight_length_mm'],
                    positive_overlap_mm3=volume,remaining_wire_airgap_mm=g,
                    only_declared_channel_and2_5mm_exit_throat_exempt_from_foreign_airgap=True)
                # Only this one cap intentionally mates to this one unchanged
                # jacket. Every other piece still sees the entire W043.
                scene.parts.pop('W043');savedmeta=scene.meta.pop('W043');savedbound=scene.bounds.pop('W043')
                try:failure,queries=scene.receive(s,wire=False)
                finally:scene.parts['W043']=oldwire;scene.meta['W043']=savedmeta;scene.bounds['W043']=savedbound
            else:failure,queries=scene.receive(s,wire=rows[n]['wire'])
            result['receipts'].append(dict(part=n,failure=failure,completed_queries=queries,intentional_wire_mate=mate))
            if failure:result['failures'].append(dict(part=n,**failure))
            save();print(n,'CLEAR' if not failure else failure,flush=True)
        result['status']='EXACT_MANDATORY_FLAT_UNIT_REJECTED' if result['failures'] else 'EXACT_MANDATORY_FLAT_UNIT_EXTERNAL_SPACE_CLEAR_WHOLE20_OPEN'
    except Exception as e:result['errors'].append(repr(e));result['status']='PARTIAL_EXACT_MANDATORY_FLAT_UNIT'
    bundle=OUT/f'n01-flat20-mandatory-{ref}{suffix}.breps.zip'
    with zipfile.ZipFile(bundle,'w',compression=zipfile.ZIP_DEFLATED) as z:
        result['parts']=[]
        for i,(n,s) in enumerate(proposal.items()):
            assert s.isValid() and s.Solids,n
            blob=s.exportBrepToString().encode();entry=f'{i:04}.brep';z.writestr(entry,blob)
            result['parts'].append(dict(name=n,entry=entry,sha256=hashlib.sha256(blob).hexdigest(),**rows[n]))
    result['bundle']=bundle.relative_to(ROOT).as_posix();result['bundle_sha256']=sha(bundle);save()
    print(json.dumps({k:result[k] for k in ('status','worker_seconds','failures','errors')}),flush=True)


if __name__=='__main__':main()
