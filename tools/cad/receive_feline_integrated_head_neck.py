"""Receive whole changed three-wire neck allocation, preserving every witness.

Static/36 adopted leg poses only. Current head motion, skin, source case/tie
fit and roots remain separate OPEN gates. No native or score mutation.
"""
import json,time,os,sys,zipfile,hashlib
from pathlib import Path
import FreeCAD as A
import Part
from feline_common_space_context import current,is_jacket
from feline_integrated_head_neck import candidates,positive_channel_candidates
from feline_fore_power_pair import SolidQueries,pair_spacing
from feline_solid_distance import bbox_lower_bound
from receive_feline_global_case_candidates import placement
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json


def bearing_area(a,b,z):
    """Nominal shared plane from FACE intersections, not solid/solid Common.

    Boolean Common of touching solids may omit lower-dimensional faces.
    Align copied nominal planes only within1e-6; source solids never move.
    """
    faces=lambda s:[f for f in s.Faces if abs(f.BoundBox.ZMin-z)<1e-6 and abs(f.BoundBox.ZMax-z)<1e-6]
    aa,bb=faces(a),faces(b);area=0.
    for f in aa:
        p=f.copy();p.translate(A.Vector(0,0,z-f.CenterOfMass.z))
        for g in bb:
            q=g.copy();q.translate(A.Vector(0,0,z-g.CenterOfMass.z));area+=p.common(q).Area
    return area


def rectangular_link(a,b,half_y=2.,half_z=1.1):
    """True ruled rectangular link; arm_box is only an axis-aligned bbox."""
    sections=[]
    for p in (a,b):
        pts=[A.Vector(p[0],p[1]+y,p[2]+z) for y,z in
            ((-half_y,-half_z),(half_y,-half_z),(half_y,half_z),(-half_y,half_z))]
        sections.append(Part.makePolygon(pts+[pts[0]]))
    s=Part.makeLoft(sections,True,True);assert s.isValid() and len(s.Solids)==1
    plug=Part.makeBox(4,2*half_y,2*half_z,A.Vector(b[0]-2,b[1]-half_y,b[2]-half_z))
    return s.fuse(plug).removeSplitter()


def main():
    fixture='--constructor-fixture' in sys.argv
    shared_plate='--shared-head-plate' in sys.argv
    rooted=shared_plate or '--whole-JR-kit' in sys.argv;upper=rooted or '--upper-positive-channel' in sys.argv
    tick=time.monotonic();dest=OUT/('n01-common-head-root-JR-neck-received.json' if shared_plate else 'n01-whole-JR-positive-neck-received.json' if rooted else 'n01-positive-channel-head-neck-received.json' if upper else 'n01-integrated-head-neck-received.json')
    if fixture:
        rows=[];mutual=[];world=None;meta={};pins={}
        source=OUT/'n01-full-material-scene.json';doc=json.loads(source.read_text());parts={}
        names={'Ref_Material_headref_0_Interface_FixedJR_0_0','Ref_Material_head_0_0_YawCarrier_0_0',
            'Ref_Material_headref_0_Interface_FixedJRBand_0_0','Ref_Material_headref_0_Interface_SourceLandBand_0_0','StructureReserve:HeadRootPlate'}
        with zipfile.ZipFile(ROOT/doc['bundle']) as z:
            for row in doc['parts']:
                if row['name'] not in names:continue
                raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256'];s=Part.Shape();s.importBrepFromString(raw.decode());parts[row['name']]=s
        assert set(parts)==names
    else:rows,mutual=(positive_channel_candidates(rooted) if upper else candidates());world,parts,meta,pins,docs=current()
    query=SolidQueries()
    root_report={}
    if rooted:
        from feline_common_retention_roots import face_entries
        from plan_axial_source_supports import arm_box
        jr='Ref_Material_headref_0_Interface_FixedJR_0_0';host='Ref_Material_head_0_0_YawCarrier_0_0'
        oldband='Ref_Material_headref_0_Interface_FixedJRBand_0_0';assert all(n in parts for n in (jr,host,oldband))
        bb=parts[jr].BoundBox;x0,x1,y0,y1=bb.XMin,bb.XMax,bb.YMin,bb.YMax;yc=(y0+y1)/2
        bottom=bb.ZMin-4.2;top=bb.ZMax
        def box(lo,hi):return Part.makeBox(*(b-a for a,b in zip(lo,hi)),A.Vector(*lo))
        seat=box([x0,y0,bottom],[x1,y1,bb.ZMin])
        root_host=parts[host];headplate=None;axes=[]
        if shared_plate:
            root_name='StructureReserve:HeadRootPlate';headplate=parts[root_name].copy()
            axes=sorted({(round(f.Surface.Center.x,6),round(f.Surface.Center.y,6)) for f in parts[host].Faces
                if type(f.Surface).__name__=='Cylinder' and abs(f.Surface.Axis.z)>.999 and abs(f.Surface.Radius-1.7)<1e-6})
            assert axes==[(-200.,-16.),(-200.,16.),(-184.,-16.),(-184.,16.)]
            for ax,ay in axes:headplate=headplate.cut(Part.makeCylinder(1.7,5,A.Vector(ax,ay,-22.48)))
            root_host=headplate
        entry=face_entries(root_host,[(x0+x1)/2,yc,bb.ZMin-2.1],1)[0]
        neck_y=y0+22.5 if shared_plate else yc
        nose=box([x1-2,neck_y-2,bottom],[x1+4,neck_y+2,bb.ZMin])
        beam=(rectangular_link([x1+2,neck_y,bb.ZMin-2.1],entry['point_mm']) if shared_plate else
            arm_box([x1+2,neck_y,bb.ZMin-2.1],entry['point_mm'],[2,2,2]))
        # Each jacket has its own full9mm cradle groove; common T18I closes
        # the comb, not a loose bundle. Native detail/pull qualification later.
        source_y0=y0-12;source_y1=y0-3
        comb=box([-244.19,source_y0,-17.2],[-233.01,source_y1,-10.])
        for x in (-241.14,-238.6,-236.06):
            comb=comb.cut(Part.makeCylinder(1.05,source_y1-source_y0+2,A.Vector(x,source_y0-1,-10),A.Vector(0,1,0)))
        neck=box([-242,source_y1-1,-17.2],[-235,y0+1,-15.])
        carrier=seat.fuse(nose).fuse(beam).fuse(comb).fuse(neck).removeSplitter();joint=carrier.copy().common(root_host.copy())
        assert carrier.isValid() and len(carrier.Solids)==1 and joint.Volume>1
        union=carrier.fuse(root_host).removeSplitter();assert union.isValid() and len(union.Solids)==1
        bearing_before=None
        if shared_plate:
            bearing=headplate.copy().common(parts[host].copy());assert bearing.isNull() or bearing.isValid()
            bearing_before=bearing_area(headplate,parts[host],parts[host].BoundBox.ZMin)
            assert bearing.Volume<1e-5 and bearing_before>9,(bearing.Volume,bearing.Area,bearing_before)
            carrier=union
            after=carrier.copy().common(parts[host].copy());assert after.isNull() or after.isValid()
            after_area=bearing_area(carrier,parts[host],parts[host].BoundBox.ZMin)
            assert after.Volume<1e-5 and abs(after_area-bearing_before)<1e-5,(after.Volume,after.Area,after_area,bearing_before)
            parts.pop(root_name)
        loop=box([x0-1.2,yc-1.25,bottom-1.2],[x1+1.2,yc+1.25,top+1.2]).cut(box([x0,yc-1.35,bottom],[x1,yc+1.35,top]))
        head=box([x0-1.2-4.3,yc-2.5,(bottom+top)/2-2.65],[x0-1.2,yc+2.5,(bottom+top)/2+2.65])
        strap=loop.fuse(head).removeSplitter();assert strap.isValid() and len(strap.Solids)==1
        sy=(source_y0+source_y1)/2
        source_loop=box([-245.39,sy-1.25,-18.4],[-231.81,sy+1.25,-7.75]).cut(box([-244.19,sy-1.35,-17.2],[-233.01,sy+1.35,-8.95]))
        source_head=box([-249.69,sy-2.5,-15.725],[-245.39,sy+2.5,-10.425])
        source_strap=source_loop.fuse(source_head).removeSplitter();assert source_strap.isValid() and len(source_strap.Solids)==1
        root_report=dict(host=host,root=entry,positive_host_joint_mm3=joint.Volume,
            carrier_union_one_solid=True,case_seat_bottom_mm=bottom,full_head_mm=[4.3,5.3,5.],
            existing_JR_case_unchanged=True,replaced_band=oldband,integral_extension_not_a_floating_separate_glued_bracket=True,
            independent_wire_grooves=3,full_each_grip_mm=9,shared_case_and_source_closures_not_loose_wire_bundle=True,
            source_grip_Y_range_mm=[source_y0,source_y1],native_parametric_owner_and_strength_not_qualified=True)
        if shared_plate:
            root_report.update(root_parent='StructureReserve:HeadRootPlate',root_plate_replaced_as_common_fixed_support=True,
                YawCarrier_material_unchanged=True,actual_observed_four_hole_axes_xy_mm=axes,bearing_preserved_mm2=bearing_before,
                preserved_planning_root_joint_owners=['StructureReserve:NeckWeb-1','StructureReserve:NeckWeb1'])
        parts.pop(oldband)
        oldsourceband='Ref_Material_headref_0_Interface_SourceLandBand_0_0';assert oldsourceband in parts;parts.pop(oldsourceband)
        root_report['replaced_source_band']=oldsourceband
        for name,shape,kind in (('HPJR:carrier',carrier,'proposal_material'),('HPJR:band_budget',strap,'project_stock_reservation'),('HPJR:source_band_budget',source_strap,'project_stock_reservation')):
            rows.append(dict(name=name,kind=kind,shape=shape,rooted_JR_kit=True))
        if fixture:
            print(json.dumps(dict(root=root_report,kit=[dict(name=r['name'],valid=r['shape'].isValid(),solids=len(r['shape'].Solids),volume=r['shape'].Volume) for r in rows],
                case_band_carrier_common_mm3=carrier.copy().common(strap.copy()).Volume,
                source_band_carrier_common_mm3=carrier.copy().common(source_strap.copy()).Volume)),flush=True);return
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (Path(__file__),Path(__file__).with_name('feline_integrated_head_neck.py'))})
    result=dict(status='RUNNING_INTEGRATED_SOURCE_TO_BODY_NECK',source_sha256=pins,checks={},failures=[],errors=[],
        transition_mutual_continuous=mutual,geometry=[],N01_complete=False,selected=False,physical_pass=False,
        current_head_sweeps_neck_skin_roots_and_JR_band_OPEN=True,proposed_JR_integral_carrier=root_report)
    if dest.exists():
        result=json.loads(dest.read_text());assert result['source_sha256']==pins
        result.setdefault('previous_worker_seconds',[]).append(result['worker_seconds'])
    else:
        archive=dest.with_suffix('.breps.zip')
        with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
            for i,row in enumerate(rows):
                raw=row['shape'].exportBrepToString().encode();entry=f'{i}.brep';z.writestr(entry,raw)
                result['geometry'].append(dict(name=row['name'],entry=entry,sha256=hashlib.sha256(raw).hexdigest(),
                    **{k:v for k,v in row.items() if k not in ('name','shape','transition_curvature','_axis_samples')}))
        result.update(bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive))
        if shared_plate:
            oldfile=OUT/'n01-whole-JR-positive-neck-received.json';old=json.loads(oldfile.read_text())
            own=Path(__file__).relative_to(ROOT).as_posix()
            assert all(p==own or pins[p]==h for p,h in old['source_sha256'].items())
            oldparts={r['name']:r for r in old['geometry']};identical={r['name'] for r in result['geometry']
                if r['name'] in oldparts and r['sha256']==oldparts[r['name']]['sha256']}
            for key,value in old['checks'].items():
                actor,target=key.split('|',1)
                if actor not in identical:continue
                if target.startswith('fixed:'):
                    other=target[6:]
                    if other not in parts or other.startswith('HPJR:'):continue
                result['checks'][key]=value
                if not value['ok']:result['failures'].append(dict(key=key,**value))
            result['unchanged_pair_reuse']=dict(source=oldfile.relative_to(ROOT).as_posix(),source_sha256=sha(oldfile),
                byte_identical_part_names=sorted(identical),pairs=len(result['checks']),
                changed_kit_pairs_not_reused=True,all_other_inputs_identical_except_explicit_controller_root_change=True)
    def save():result['worker_seconds']=round(time.monotonic()-tick,3);save_json(dest,result)
    def receive(key,op):
        if key in result['checks']:return
        if time.monotonic()-tick>230:raise TimeoutError('Whole completed exact pairs saved; not an infeasibility verdict')
        r=op();result['checks'][key]=r
        if not r['ok']:result['failures'].append(dict(key=key,**r))
        save()
    save()
    try:
        for row in rows:
            s=row['shape'];name=row['name']
            pieces=[A.BoundBox(*lo,*hi) for lo,hi in row.get('swept_piece_bounds_mm',[])]
            def near(target):
                # Every circular sweep point is within r of its axis. The
                # union of inflated EDGE bounds contains the WHOLE jacket;
                # avoid the huge empty middle of the full return's bbox.
                return bbox_lower_bound(s.BoundBox,target)<1.25 and (not pieces or any(bbox_lower_bound(b,target)<1.25 for b in pieces))
            targets={**parts,**{r['name']:r['shape'] for r in rows if r['name']!=name}}
            for n,t in targets.items():
                other_row=next((r for r in rows if r['name']==n),None)
                if rooted and row.get('wire') and other_row and other_row.get('wire'):continue # full continuous pair bound already received
                if not near(t.BoundBox):continue
                # Existing cosmetics are explicitly replaced by N08. All
                # mechanical carriers, other cables and stock stay in scope.
                if n.startswith('Ref_Material_head_0_0_') and any(n.endswith('_'+v+'_0_0') for v in ('Rear','FrontLeft','FrontRightPorted','Nose','EarL','EarR')):continue
                def exact(s=s,t=t,n=n,row=row):
                    mate_jr=n=='Ref_Material_headref_0_Interface_FixedJR_0_0'
                    mate_host=rooted and row['name']=='HPJR:carrier' and n==root_report['host']
                    if mate_host:
                        if shared_plate:return dict(ok=True,common_mm3=0.,bearing_preserved_mm2=root_report['bearing_preserved_mm2'],criterion='Unchanged bolted bearing face; actual4axes preserved, not air-gap interface')
                        return dict(ok=True,common_mm3=root_report['positive_host_joint_mm3'],criterion='Intended positive material union to actual carrier, not clearance')
                    if shared_plate and name=='HPJR:carrier' and n in root_report['preserved_planning_root_joint_owners']:
                        common=s.copy().common(t.copy());assert common.isNull() or common.isValid()
                        return dict(ok=common.Volume>1,common_mm3=common.Volume,criterion='Preserved same-fixed-frame head root plate/neck web material joint, not purchased interference')
                    source_mate=rooted and ((row.get('wire') and n in ('HPJR:carrier','HPJR:source_band_budget')) or (name in ('HPJR:carrier','HPJR:source_band_budget') and other_row and other_row.get('wire')))
                    if source_mate:
                        w=s if row.get('wire') else t;kit=t if row.get('wire') else s;wid=row.get('wire') or other_row['wire']
                        wx={'XB22':-238.6,'XB23':-241.14,'XS23':-236.06}[wid];ya,yb=root_report['source_grip_Y_range_mm']
                        zone=box([wx-1.3,ya-1.25,-11.3],[wx+1.3,yb+1.25,-8.7]);outside=w.copy().cut(zone)
                        common=w.copy().common(kit.copy());assert common.isNull() or common.isValid();assert outside.isValid() and outside.Solids
                        minimum=1.25 if 'carrier' in (name,n) or name=='HPJR:carrier' or n=='HPJR:carrier' else .2
                        gap=query.distance(outside,kit)
                        return dict(ok=common.Volume<1e-5 and gap>=minimum-1e-6,common_mm3=common.Volume,outside_grip_gap_mm=gap,minimum_mm=minimum,
                            criterion='Intentional full9mm individual cradle contact only; remainder keeps original clearance')
                    if rooted and name.startswith('HPJR:') and n.startswith('HPJR:'):
                        common=s.copy().common(t.copy());assert common.isNull() or common.isValid()
                        return dict(ok=common.Volume<1e-5,common_mm3=common.Volume,criterion='Whole band/cradle faces intentionally touch; no positive overlap')
                    if mate_jr:
                        common=s.copy().common(t.copy());assert common.isNull() or common.isValid()
                        return dict(ok=common.Volume<1e-5,common_mm3=common.Volume,criterion='Known source end face mate; no positive jacket/case overlap')
                    if not t.Solids:return dict(ok=False,reason='Curve-only existing jacket remains OPEN, not actual contact',wire_owner=meta.get(n,{}).get('wire_owner'))
                    q=s
                    if n==world.bus['name']:q=s.copy();q.Placement=world.bus['inverse']*q.Placement;t=world.bus['original']
                    minimum=pair_spacing(name,dict(kind='proposal_wire' if row.get('wire') else row['kind'],wire=row.get('wire')),n,
                        dict(kind='proposal_wire' if other_row.get('wire') else other_row['kind'],wire=other_row.get('wire')) if other_row else meta[n])
                    if rooted and row['kind']=='head_actual_source_nominal_jacket' and n=='Ref_Material_headref_0_Interface_SourceLandBand_0_0':minimum=.2
                    gap=query.distance(q,t)
                    return dict(ok=gap>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum)
                receive(name+'|fixed:'+n,exact)
            for p in world.motion:
                if not near(A.BoundBox(*p['bounds'][0],*p['bounds'][1])):continue
                def exact(s=s,p=p):
                    q=s.copy();q.Placement=placement(p['r'],p['t']).inverse()*q.Placement;gap=query.distance(q,world.rest[p['name']])
                    return dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
                receive(name+'|motion:'+p['name']+':'+str(p['pose']),exact)
            print('NECK_WHOLE',name,'pairs',len(result['checks']),'holds',len(result['failures']),flush=True)
        result['status']='INTEGRATED_NECK_SOURCE_CURVES_RECEIVED_OTHER_GATES_OPEN' if not result['failures'] else 'INTEGRATED_NECK_WHOLE_NAMED_INTERFACES_OPEN'
    except TimeoutError as exc:result.update(status='PARTIAL_INTEGRATED_NECK_RECEIPT',slice_note=str(exc))
    except Exception as exc:result['errors'].append(repr(exc));result['status']='INTEGRATED_NECK_RECEIPT_ERROR'
    save();print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'],pairs=len(result['checks']),holds=len(result['failures']),errors=result['errors'])),flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
