"""One MAIN planning unit: seated bought M2, formed insulated necks, grip/root.

Explicit project nominal jacket OD2.1 is not the larger Pi capacity envelope.
No supplier guarantee, native manufacturing, final cut or N01 completion.
"""
import gzip,hashlib,json,math,os,sys,time,zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_cuff_composed_context import compose
from compose_feline_cuff_boundaries import current
from plan_feline_n01_shared import pipe
from receive_feline_underplate_return_gallery import bend,forward,minimum_for
from receive_feline_global_case_candidates import placement
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from plan_feline_pi_root_access import profile_gap
from plan_feline_usb_service_bight import outer_margin
from feline_atomic_save import save_json

BOARD='Ref_Material_MAIN_CurrentMainSupplierReference_0_0'
BED='CurrentFoundation:BankBedCurrent:-1'


def local_inputs():
    parts={};pins={}
    for filename,field,prefix in [('n01-six-source-current-core.json','parts',''),('n01-channelled-foundation-static.json','geometry','CurrentFoundation:')]:
        f=OUT/filename;r=json.loads(f.read_text());arc=ROOT/r['bundle'];assert sha(arc)==r['bundle_sha256']
        pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (f,arc)})
        with zipfile.ZipFile(arc) as z:
            for row in r[field]:
                n=prefix+row['name']
                if not (n==BED or n.startswith(('Ref_Material_MAIN_','MAINNew','End:W060/','End:W078/','End:W079/','End:W080/'))):continue
                raw=z.read(row['entry']);assert hashlib.sha256(raw).hexdigest()==row['sha256']
                s=Part.Shape();s.importBrepFromString(raw.decode());parts[n]=s
    return parts,pins


def neck(p):
    q=np.array(p,float);d=np.array([0.,0.,-1.]);normal=np.array([0.,1.,0.])
    rows=[];q=forward(rows,q,d,.5);R=2.2;angle=math.acos(1-4/(2*R))
    q,h=bend(rows,q,d,normal,R,angle)
    normal=d-h*float(d@h);normal/=np.linalg.norm(normal)
    q,h=bend(rows,q,h,normal,R,angle);q=forward(rows,q,h,.5)
    assert np.linalg.norm(h-d)<1e-6
    return rows,q,1+2*R*angle


def cylinder(a,b,r):
    a=A.Vector(*a);b=A.Vector(*b);v=b-a
    return Part.makeCylinder(r,v.Length,a,v)


def construct(parts,ends):
    actors={};kinds={};recipes={};retired=[]
    for n,s in parts.items():
        if n.startswith('Ref_Material_MAIN_') or n.startswith(('MAINNew','End:MAIN:')):
            retired.append(n)
    rows=sorted((e for e in ends if e['group']=='MAIN'),key=lambda e:e['point_mm'][0]);assert len(rows)==4
    for e in rows:
        # MAIN source producer explicitly names these by endpoint id; unlike
        # received cuff overlays it has no prefix_geometry_owner property.
        n='End:'+e['id'];assert n in parts
        if n not in retired:retired.append(n)
    board=parts[BOARD].copy()
    # Supplier compound includes underside components: whole bbox ZMin is
    # NOT the PCB mounting plane. Recover the two largest horizontal faces.
    planes=sorted((f for f in board.Faces if type(f.Surface).__name__=='Plane' and f.BoundBox.ZLength<1e-4),key=lambda f:f.Area,reverse=True)[:2]
    assert sorted(round(f.BoundBox.ZMin,4) for f in planes)==[101.25,102.8248]
    board.translate(A.Vector(0,0,-2));actors[BOARD]=board;kinds[BOARD]=dict(kind='actual_source')
    # Reverse the PCB SIDE, not the row's front/back. Y-axis half-turn keeps
    # the four outlets on the outside bank edge; components face upward.
    pivot=A.Vector(-20,-76,100.0374);rot=A.Rotation(A.Vector(0,1,0),180)
    board.Placement=A.Placement(pivot-rot.multVec(pivot),rot)*board.Placement
    bottom=99.25;top=100.8248;washer_top=91.25;xs=[]
    for i in (0,1):
        names=[f'Ref_Material_MAIN_{i}_{p}_0_0' for p in ('head','shaft','lower_washer','nut')]
        head=parts[names[0]];delta=top-head.BoundBox.ZMin;xs.append(head.BoundBox.Center.x)
        for n in names:
            s=parts[n].copy();s.translate(A.Vector(0,0,delta));actors[n]=s;kinds[n]=dict(kind='actual_source')
        assert abs(actors[names[0]].BoundBox.ZMin-top)<1e-5
        assert abs(actors[names[2]].BoundBox.ZMax-washer_top)<1e-4
        assert abs(actors[names[1]].BoundBox.ZMax-top)<1e-4
    collars=[];wires=[];jacketends=[]
    for e in rows:
        x=-40-e['point_mm'][0];p=[x,-87.049,bottom];path,q,L=neck(p)
        # Sleeve starts .25 below PCB, leaving a solder/fillet fit gate.
        sleeve_path=[dict(path[0],start=[x,p[1],bottom-.25],length_mm=.25),*path[1:]]
        sleeve_tail=16-(L-.25);assert 14.4-(L-.25)>=6
        forward(sleeve_path,q,[0,0,-1],sleeve_tail)
        sleeve=pipe(sleeve_path,1.75).cut(pipe(sleeve_path,1.05)).removeSplitter()
        grip_start=q[2]-sleeve_tail-.25;grip_end=grip_start-9
        jacket=cylinder(q,[q[0],q[1],grip_end],1.05);bare=pipe(path,math.sqrt(.823/math.pi))
        for suffix,s,kind in [('bare',bare,'bare_conductor'),('sleeve',sleeve,'insulation'),('jacket',jacket,'wire')]:
            n='MainSupported:'+e['id']+':'+suffix;actors[n]=s;kinds[n]=dict(kind=kind,wire_owner=e['wire'])
        collars.append(sleeve);wires.append(jacket);jacketends.append([q[0],q[1],grip_end])
        recipes[e['id']]=dict(source_pad_mm=p,jacket_start_mm=q.tolist(),PCB_side_reversed_180Y=True,physical_through_pad_role_preserved=True,
            source_neck_parts=path,bare_neck_mm=L,project_bare_form_R_mm=2.2,sleeve_raw_mm=16,
            sleeve_min_recovered_mm=14.4,min_recovered_intact_overlap_mm=14.4-(L-.25),
            jacket_nominal_project_radius_mm=1.05,sleeve_outer_conservative_radius_mm=1.75,
            routing_exit_mm=jacketends[-1],routing_exit_axis=[0,0,-1],grip_start_Z_mm=grip_start,full_individual_grip_mm=9,
            delivered_solder_strip_form_and_sleeve_recovery_fit_gate=True,selected_SKU_unchanged=True)
    y=jacketends[0][1];z=jacketends[0][2];lo=min(p[0] for p in jacketends)-3.25;hi=max(p[0] for p in jacketends)+3.25
    comb=Part.makeBox(hi-lo,5.5,9,A.Vector(lo,y-1.25,z))
    for p in jacketends:
        comb=comb.cut(Part.makeCylinder(1.25,11,A.Vector(p[0],y,z-1))).cut(Part.makeBox(2.5,3,11,A.Vector(p[0]-1.25,y-3,z-1)))
    outer=Part.makeBox(hi-lo+2.8,8.3,2.5,A.Vector(lo-1.4,y-2.65,z+3.25))
    inner=Part.makeBox(hi-lo+.4,5.9,4.5,A.Vector(lo-.2,y-1.45,z+2.25))
    band=outer.cut(inner);head=Part.makeBox(4.3,5.3,5,A.Vector(hi+1.4,y-.65,z+2))
    actors['MainSupported:comb']=comb.removeSplitter();kinds['MainSupported:comb']=dict(kind='proposal_material')
    for suffix,s in [('band',band),('head',head)]:
        actors['MainSupported:'+suffix]=s;kinds['MainSupported:'+suffix]=dict(kind='project_stock_reservation',material_role='selected_T18I_nylon_budget')
    stem_y=-72.25
    root=Part.makeCylinder(2,95.25-(parts[BED].BoundBox.ZMax-.5),A.Vector(-20,stem_y,parts[BED].BoundBox.ZMax-.5))
    root=root.fuse(Part.makeCylinder(3,3,A.Vector(-20,stem_y,parts[BED].BoundBox.ZMax-.5)))
    for x in xs:
        boss=Part.makeCylinder(3.2,8,A.Vector(x,-89.081,washer_top))
        a=[x,-89.081,95.25];b=[x,stem_y,95.25];c=[-20,stem_y,95.25]
        root=root.fuse(boss).fuse(cylinder(a,b,1.5)).fuse(Part.makeSphere(1.5,A.Vector(*b))).fuse(cylinder(b,c,1.5))
    # Enter above the full tie layer, not through its closed rear strap.
    root=root.fuse(cylinder([-20,stem_y,z+8],[-20,y+3.5,z+8],1.5)).fuse(Part.makeSphere(1.5,A.Vector(-20,y+3.5,z+8)))
    for x in xs:root=root.cut(Part.makeCylinder(1.2,60,A.Vector(x,-89.081,50)))
    # Open inward-facing fork seats, not four thick cylindrical walls pressed
    # into the source neck. Retain the outer bearing ring and 2mm back wall.
    for x in xs:
        start=x+1.2 if x<-20 else x-7.2
        root=root.cut(Part.makeBox(6,6.5,8.2,A.Vector(start,-92.331,91.15)))
    root=root.removeSplitter();actors['MainSupported:root']=root;kinds['MainSupported:root']=dict(kind='proposal_material')
    assert root.isValid() and len(root.Solids)==1
    assert root.common(parts[BED]).Volume>10
    assert root.common(comb).Volume>1
    for n,s in actors.items():assert s.isValid() and len(s.Solids)>0,n
    return actors,kinds,recipes,retired


def intrinsic(actors,original,kinds):
    checks={};names=list(actors)
    for i,n in enumerate(names):
        for m in names[i+1:]:
            a,b=actors[n],actors[m];minimum=minimum_for(n,kinds[n],m,kinds[m]);relation='inherited_typed_material_spacing'
            metal=lambda k:k.startswith('Ref_Material_MAIN_') and k!=BOARD
            samewire=kinds[n].get('wire_owner') and kinds[n].get('wire_owner')==kinds[m].get('wire_owner')
            if samewire:minimum=0;relation='same_wire_jacket_insulation_copper_interfaces'
            if kinds[n]['kind']=='bare_conductor' and kinds[m]['kind']=='insulation' or kinds[m]['kind']=='bare_conductor' and kinds[n]['kind']=='insulation':
                # Same four-pad assembly: soft dielectric, NOT adjacent live
                # conductor/metal. Bare/bare and bare/metal retain1.25mm.
                minimum=.2;relation='same_source_fan_copper_to_intact_dielectric_no_penetration_not_electrical_rating'
            if n==BOARD and metal(m) or m==BOARD and metal(n):minimum=0;relation='actual_M2_hole_shaft_or_head_seated_on_PCB'
            if n.endswith(':sleeve') and m.endswith(':sleeve'):minimum=0;relation='nominal_intact_insulation_contact_fit_gate'
            if n==BOARD and m.endswith(':bare') or m==BOARD and n.endswith(':bare'):minimum=0;relation='own_actual_solder_pad_face'
            if n==BOARD and m.endswith(':sleeve') or m==BOARD and n.endswith(':sleeve'):minimum=.25;relation='own_insulation_below_PCB'
            if n=='MainSupported:root' or m=='MainSupported:root':minimum=.25;relation='own_printed_carrier'
            if set((n,m))==set(('MainSupported:root',BOARD)):minimum=0;relation='own_PCB_standoff_bearing'
            if 'MainSupported:root' in (n,m) and (metal(n) or metal(m)):minimum=0;relation='own_M2_bore_and_washer_bearing'
            if 'MainSupported:comb' in (n,m):minimum=.2;relation='own_individual_jacket_channel'
            if set((n,m))==set(('MainSupported:root','MainSupported:comb')):
                v=a.common(b).Volume;checks[n+'|'+m]=dict(ok=v>1,intended_print_union_mm3=v);continue
            if set((n,m))==set(('MainSupported:band','MainSupported:head')):minimum=0;relation='one_selected_tie_head_band_contact'
            if bbox_lower_bound(a.BoundBox,b.BoundBox)>=minimum and minimum>0:continue
            gap=a.distToShape(b)[0];v=0
            if gap<1e-6:
                c=a.common(b);assert c.isNull() or c.isValid();v=c.Volume
            inherited=0
            if metal(n) and metal(m):
                old=original[n].common(original[m]);assert old.isNull() or old.isValid();inherited=old.Volume
                if n.split('_')[3]==m.split('_')[3]:minimum=0;relation='unchanged_same_fastener_nominal_mate'
            checks[n+'|'+m]=dict(ok=gap>=minimum-1e-6 and v<=inherited+1e-5,gap_mm=gap,minimum_mm=minimum,
                positive_common_mm3=v,inherited_same_fastener_mm3=inherited,contract=relation)
    return checks


def main():
    tick=time.monotonic();_,ends,files=current()
    if '--local-preflight' in sys.argv:
        parts,pins=local_inputs();actors,kinds,recipes,retired=construct(parts,ends)
        pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (*files,Path(__file__))})
        checks=intrinsic(actors,parts,kinds)
        from feline_channelled_foundation import bearing_area
        root=actors['MainSupported:root'];board=actors[BOARD]
        for i in (0,1):
            washer=actors[f'Ref_Material_MAIN_{i}_lower_washer_0_0']
            area=bearing_area(root,washer,91.25)
            checks['actual_fork_washer_bearing:'+str(i)]=dict(ok=area>10,area_mm2=area,project_minimum_area_mm2=10)
        area=bearing_area(root,board,99.25)
        checks['actual_fork_PCB_bearing']=dict(ok=area>20,area_mm2=area,project_minimum_area_mm2=20)
        failures={k:v for k,v in checks.items() if not v['ok']}
        result=dict(status='MAIN_LOCAL_INTRINSIC_HOLDS' if failures else 'MAIN_LOCAL_INTRINSIC_RECEIVED_EXTERNAL_OPEN',checks=checks,
            failures=failures,source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3),N01_complete=False,
            recipes=recipes,physical_pass=False)
        save_json(OUT/'n01-MAIN-component-up-local-intrinsic.json',result)
        print(result['status'],'checks',len(checks),'seconds',result['worker_seconds'],flush=True)
        print(json.dumps(failures,indent=2),flush=True);return
    prefile=OUT/'n01-MAIN-component-up-local-intrinsic.json';pre=json.loads(prefile.read_text())
    assert pre['status']=='MAIN_LOCAL_INTRINSIC_RECEIVED_EXTERNAL_OPEN' and not pre['failures']
    for p,h in pre['source_sha256'].items():assert sha(ROOT/p)==h,p
    world,parts,meta,pins,docs=compose()
    actors,kinds,recipes,retired=construct(parts,ends)
    fixed={n:s for n,s in parts.items() if n not in retired}
    dest=OUT/'n01-MAIN-supported-unit.json';arc=dest.with_suffix('.breps.zip');pf=dest.with_suffix('.pairs.json.gz')
    assert not dest.exists(),'Receive existing MAIN candidate; do not repeat unchanged'
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (*files,prefile,Path(__file__),ROOT/'tools/cad/plan_current_main_neck_insulation.py',ROOT/'hardware/electronics/power-platform/MAIN-INPUT-P0.md')})
    geometry=[]
    with zipfile.ZipFile(arc,'w',zipfile.ZIP_DEFLATED) as z:
        for i,(n,s) in enumerate(actors.items()):
            raw=s.exportBrepToString().encode();entry=str(i)+'.brep';z.writestr(entry,raw)
            geometry.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest(),**kinds[n]))
    checks={'intrinsic:'+k:v for k,v in pre['checks'].items()};r=dict(status='RUNNING_MAIN_SUPPORTED_WHOLE_UNIT',source_sha256=pins,bundle=arc.relative_to(ROOT).as_posix(),bundle_sha256=sha(arc),geometry=geometry,
        recipes=recipes,retired=retired,N01_complete=False,physical_pass=False,native_changed=False,completed_static=[],completed_motion=[],
        PCB_and_all8_M2_changed_as_one_unit=True,bought_parts_unchanged=True,nominal_jacket_not_capacity_envelope=True,
        layer_datum_mm=dict(PCB_bottom=99.25,PCB_top=100.8248,head_top=102.8248,washer_top=91.25,standoff=8),
        root_to_bankbed_positive_union_mm3=actors['MainSupported:root'].common(parts[BED]).Volume,
        root_to_comb_positive_union_mm3=actors['MainSupported:root'].common(actors['MainSupported:comb']).Volume,
        assembly_tool_pull_strength_and_delivery_gates_OPEN=True)
    def save():
        pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
        r.update(checks=len(checks),failures=[k for k,v in checks.items() if not v['ok']],pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),worker_seconds=round(time.monotonic()-tick,3));save_json(dest,r)
    query=SolidQueries();save()
    for n,s in actors.items():
        checks[n+'|outer']=outer_margin(s,docs['outer'])
        for m,t in {**fixed,**actors}.items():
            if m==n:continue
            key='|'.join(sorted((n,m))) if m in actors else n+'|'+m
            if key in checks:continue
            minimum=minimum_for(n,kinds[n],m,kinds.get(m,meta.get(m,{})))
            if m in actors:
                # Source-unit intrinsic contacts are measured separately, not waived globally.
                continue
            if m==BED and n=='MainSupported:root':
                checks[key]=dict(ok=True,intended_print_union_mm3=r['root_to_bankbed_positive_union_mm3']);continue
            if bbox_lower_bound(s.BoundBox,t.BoundBox)>=minimum:continue
            a=s
            if m==world.bus['name']:
                a=s.copy();a.Placement=docs['inverse']*a.Placement;t=world.bus['original']
            checks[key]=dict(ok=(gap:=query.distance(a,t))>=minimum-1e-6,gap_mm=gap,minimum_mm=minimum) if t.Solids else profile_gap(a,t,meta[m].get('nominal_profile_radius_mm') or meta[m].get('radius_mm'),minimum)
        r['completed_static'].append(n);save();print('MAIN external',n,'holds',len(r['failures']),flush=True)
        if time.monotonic()-tick>220:r['status']='PARTIAL_MAIN_EXTERNAL_GATE';save();return
    if not r['failures']:
        for n,s in actors.items():
            for pose in world.motion:
                if bbox_lower_bound(s.BoundBox,A.BoundBox(*pose['bounds'][0],*pose['bounds'][1]))>=1.25:continue
                a=s.copy();a.Placement=placement(pose['r'],pose['t']).inverse()*a.Placement
                gap=query.distance(a,world.rest[pose['name']]);checks[n+'|motion:'+pose['name']+':'+str(pose['pose'])]=dict(ok=gap>=1.25-1e-6,gap_mm=gap,minimum_mm=1.25)
            r['completed_motion'].append(n);save()
    r['status']='MAIN_WHOLE_UNIT_HOLDS' if r['failures'] else 'MAIN_INTRINSIC_STATIC36_RECEIVED_TOOLS_OPEN'
    save();print(r['status'],len(r['failures']),r['worker_seconds'],flush=True)


if __name__=='__main__':print('WORKER_PID',os.getpid(),flush=True);main()
