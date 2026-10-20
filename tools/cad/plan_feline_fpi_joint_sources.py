"""One coupled four-land F_PI/splice gate, not another placement catalogue.

Keep both complete factory paths and the existing splice. Full9 may be on
the existing arc. Nominal .15 jacket fit and adjustable T18I are delivery
gates; selected bought geometry, foreign margins and wire lengths stay fixed.
"""
import gzip,hashlib,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_source_saddles import segment
from plan_feline_u1_common_restraints import open_seat
from plan_feline_n01_shared import pipe
from feline_fore_power_pair import SolidQueries
from receive_feline_aux_vertical_unit import material_spacing
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap


def construct(curved_output=False):
    f=OUT/'n01-central-spine-power-plan-r4.json';p=json.loads(f.read_text())
    from feline_selected_piece_contract import load
    contract,cf=load();routes={r['wire']:r for r in p['routes']}
    new={};meta={};lands={}
    choices=(('F_PI.in','W043',0,1.25,[0,1,0]),
             ('F_PI.out','W077',1,0.,[0,.28,.96]),
             ('SPLICE_PI.16','W077',3,0.,[0,1,0]),
             ('SPLICE_PI.18','W078',0,16.,[0,1,0]))
    for role,w,idx,start,side in choices:
        if curved_output and role=='F_PI.out':side=[0,-.28,-.96]
        r=next(v for v in contract['portions'].values() if v['wire']==w)
        radius=r['project_radius_mm'];row=routes[w]['parts'][idx];edge=segment(row)
        assert start+9<=edge.Length+1e-6
        param=lambda s:edge.FirstParameter+(edge.LastParameter-edge.FirstParameter)*s/edge.Length
        q=edge.valueAt(param(start));t=edge.tangentAt(param(start));u=A.Vector(*side);v=t.cross(u)
        assert abs(t.dot(u))<1e-6 and abs(v.Length-1)<1e-6
        cap=radius+.15
        kit=open_seat(list(q),list(t),side,cap)
        path=Part.Wire([edge.Curve.toShape(param(start),param(start+9))])
        corners=[q+u*y+v*z for y,z in ((cap,-cap),(cap+2,-cap),(cap+2,cap),(cap,cap),(cap,-cap))]
        kit['pad']=path.makePipeShell([Part.Wire(Part.makePolygon(corners).Edges)],True,False)
        centre=edge.valueAt(param(start+4.5));axis=edge.tangentAt(param(start+4.5))
        # Tie is straight locally at its own centre; the9mm printed land
        # follows the unchanged arc. No extra straight after that arc.
        tie=open_seat(list(centre-axis*4.5),list(axis),side,cap)
        kit.update(band=tie['band'],head=tie['head'])
        if curved_output and role=='F_PI.out':
            # A flexible band follows its actual arc, not a straight box
            # intersecting the curved pad. Opposite closure side clears
            # the measured S0 body above, without moving the source wire.
            def swept_rect(a,b,y0,y1,z0,z1):
                p0=edge.valueAt(param(a));t0=edge.tangentAt(param(a));v0=t0.cross(u)
                cs=[p0+u*y+v0*z for y,z in ((y0,z0),(y1,z0),(y1,z1),(y0,z1),(y0,z0))]
                path0=Part.Wire([edge.Curve.toShape(param(a),param(b))])
                return path0.makePipeShell([Part.Wire(Part.makePolygon(cs).Edges)],True,False)
            kit['band']=swept_rect(start+3.25,start+5.75,-cap-1.2,cap+3.2,-cap-1.2,cap+1.2).cut(
                swept_rect(start+3.15,start+5.85,-cap,cap+2,-cap,cap))
        if curved_output:
            assert kit['pad'].copy().common(kit['band'].copy()).Volume<1e-5,role
            assert kit['band'].fuse(kit['head']).isValid() and len(kit['band'].fuse(kit['head']).Solids)==1,role
        for suffix,s in kit.items():
            assert s.isValid() and len(s.Solids)==1,(role,suffix)
            n='FPIJoint:'+role+':'+suffix;new[n]=s
            meta[n]=dict(kind='PETG' if suffix=='pad' else 'T18I',role=role)
        lands[role]=dict(wire=w,selected_sku=r['selected_sku'],radius_mm=radius,
            minimum_R_mm=r['minimum_project_R_mm'],source_part_index=idx,
            full9_arclength_mm=[start,start+9],start_mm=list(q),end_mm=list(edge.valueAt(param(start+9))),
            axis_at_start=list(t),side=side,nominal_fit_clearance_mm=.15,extra_wire_mm=0)
    for w in ('W043','W077'):
        r=contract['portions']['W043/single' if w=='W043' else 'W077/retained0']
        assert r['project_radius_mm']==2.
        assert min(x['radius_mm'] for x in routes[w]['parts'] if x['kind']=='arc')>=r['minimum_project_R_mm']
        new[w]=pipe(routes[w]['parts'],2.);meta[w]=dict(kind='wire',wire=w)
    return new,meta,lands,{str(x.relative_to(ROOT)):sha(x) for x in (f,cf,Path(__file__))}


def receive(world,fixed,metadata,pins,stem='n01-FPI-four-source-joint',parent=None,curved_output=False):
    tick=time.monotonic();new,meta,lands,inputs=construct(curved_output);dest=OUT/(stem+'.json');assert not dest.exists()
    targets={n:s for n,s in fixed.items() if n not in ('W043','W077','SpliceClip')}
    bounds={n:s.BoundBox for n,s in targets.items()};checks={};q=SolidQueries()
    report=dict(status='RUNNING_FPI_FOUR_SOURCE_STATIC',lands=lands,geometry=[],
        source_sha256={**pins,**inputs},completed_static=[],failures=[],N01_complete=False,
        physical_pass=False,native_changed=False,paths_and_selected_SKUs_unchanged=True,
        roots_case_retention_tools_and_motion_OPEN=True,old_SpliceClip_reservation_retired=True)
    oldraw={};changed=set(new)
    if parent:
        old=json.loads((OUT/parent).read_text());assert curved_output
        assert old['status']=='FPI_FOUR_GRIPS_CURRENT_STATIC_HOLD'
        for path,h in old['source_sha256'].items():
            if path.replace('\\','/')!=Path(__file__).relative_to(ROOT).as_posix():assert sha(ROOT/path)==h,path
        changed={n for n in new if n.startswith('FPIJoint:F_PI.out:')}
        for role,row in old['lands'].items():
            if role!='F_PI.out':assert row==lands[role]
        with zipfile.ZipFile(ROOT/old['bundle']) as z:
            for row in old['geometry']:
                n=row['name']
                if n in changed:continue
                raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
                s=Part.Shape();s.importBrepFromString(raw.decode());new[n]=s;oldraw[n]=raw
        prior=json.loads(gzip.decompress((ROOT/old['pair_rows']).read_bytes()))
        checks.update({k:v for k,v in prior.items() if k.split('|')[0] not in changed})
        assert all(v['ok'] for v in checks.values())
        report.update(unchanged_pairs_reused=len(checks),changed_geometry=sorted(changed),
            parent_static=parent,source_sha256={**report['source_sha256'],str((OUT/parent).relative_to(ROOT)):sha(OUT/parent)})
        report['completed_static']=[n for n in old['completed_static'] if n not in changed]
    bundle=dest.with_suffix('.breps.zip')
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in new.items():
            raw=oldraw[n] if n in oldraw else s.exportBrepToString().encode();entry=str(len(report['geometry']))+'.brep';z.writestr(entry,raw)
            report['geometry'].append(dict(meta[n],name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    report.update(bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle))
    def save():
        pf=dest.with_suffix('.pairs.json.gz');pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        report.update(pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),checks=len(checks),
            failures=[k for k,v in checks.items() if not v['ok']],worker_seconds=round(time.monotonic()-tick,3))
        save_json(dest,report)
    # Receive all12 full grips against current material, not only one
    # first witness. The2 typed paths remain separately explicit OPEN:
    # their nominal casing/splice mates need interface-specific treatment.
    for n,s in new.items():
        if n in ('W043','W077') or n not in changed:continue
        own=lands[meta[n]['role']]['wire']
        for b,t in {**targets,**{k:v for k,v in new.items() if k in ('W043','W077')}}.items():
            limit=.15 if b==own else material_spacing(n,meta[n],b,metadata.get(b,meta.get(b,{})))
            if bbox_lower_bound(s.BoundBox,bounds.get(b,t.BoundBox))>=limit+1e-6:continue
            a=s;other=t
            if b==world.bus['name']:a=s.copy();a.Placement=world.bus['inverse']*a.Placement;other=world.bus['original']
            row=profile_gap(a,other,metadata.get(b,{}).get('nominal_profile_radius_mm'),limit) if not other.Solids else dict(gap_mm=q.distance(a,other))
            if 'gap_mm' in row:row.update(ok=row['gap_mm']>=limit-1e-6,minimum_mm=limit)
            checks[n+'|'+b]=row
        report['completed_static'].append(n);save()
    report['status']='FPI_FOUR_GRIPS_CURRENT_STATIC_HOLD' if report['failures'] else 'FPI_FOUR_GRIPS_CURRENT_STATIC_RECEIVED_ROOTS_MOTION_TOOLS_OPEN'
    save();print(report['status'],report['checks'],report['failures'],report['worker_seconds'],flush=True)
    return report
