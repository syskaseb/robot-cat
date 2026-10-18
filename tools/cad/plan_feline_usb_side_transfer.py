"""One side-transfer USB topology, reusing rejected central-curve evidence.

Both exits and full factory-length allowance are solved together. An allocated
side waypoint/tangent separates the route from lower U1; it is NOT a mount.
All candidates and completed exact pairs are saved for bounded continuation.
"""
import json
import math
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT
from feline_rev3_query_scene import build
from feline_tangent_routes import biarc,quarter_prefix,reverse,samples,length,min_radius,dot,sub,norm
from plan_feline_joint_usb_route import wire
from check_feline_all_current_lands import near


def main():
    tick=time.monotonic();dest=OUT/'n01-usb-side-transfer.json';assert not dest.exists()
    previousfile=OUT/'n01-joint-usb-route.json';previous=json.loads(previousfile.read_text())
    assert previous['accepted_route'] is None
    report=dict(status='RUNNING_SHARED_SIDE_TRANSFER_USB',selected=False,N01_complete=False,physical_pass=False,
        catalog_mm=500,project_outside_allowance_mm=452,allowance_not_supplier_guarantee=True,
        predecessor=previousfile.relative_to(ROOT).as_posix(),predecessor_seconds=180.016,
        topology_change='Four middle arcs via shared side-transfer tangent, not two central arcs through U1; same Pi/BUS/selected cable',
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (previousfile,Path(__file__),Path(__file__).with_name('feline_tangent_routes.py'),Path(__file__).with_name('plan_feline_joint_usb_route.py'))},
        math_queries=0,domains_completed=0,candidates=[],exact=[],errors=[],chosen_curve=None,
        complete_wire_or_native_mounts_qualified=False,search_not_exhaustive=True)
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    save();scene,meta,pins,bus=build();report['source_sha256'].update(pins)
    reader=SavedShapes();envfile=OUT/'central-cassette-envelope/FelineLayoutEnvelope.FCStd';outer=reader.shape(envfile,'TorsoEnvelope');surface=Part.makeCompound(outer.Faces)
    assert outer.isValid();report['source_sha256'].update(reader.hashes)
    start=previous['start_mm'];end=previous['end_mm'];ratios=[2**(i/2) for i in range(-8,9)]
    # Search domains are functional side-lane nodes, NOT another component-offset trial.
    nodes=[(x,-69,z) for x in (-40,0,40) for z in (60,90)]
    def make(ia,ib,node,it,rho):
        a=ia*math.pi/12;b=ib*math.pi/12;t=it*math.pi/6
        pre=quarter_prefix(start,(-1,0,0),(0,math.cos(a),math.sin(a)))
        post=quarter_prefix(end,(0,-1,0),(math.cos(b),0,math.sin(b)))
        tangent=(math.cos(t),0,math.sin(t))
        a0=biarc(pre[-1]['end'],(0,math.cos(a),math.sin(a)),node,tangent,rho)
        a1=biarc(node,tangent,post[-1]['end'],(-math.cos(b),0,-math.sin(b)),1/rho)
        return pre+a0+a1+[reverse(s) for s in post[::-1]]
    stop=False
    for ia in (12,14,16,18,20,22,0):
        for ib in (12,14,16,18,20,22):
            for node in nodes:
                for it in range(12):
                    prev=None
                    for rho in ratios:
                        if time.monotonic()-tick>100:stop=True;break
                        try:parts=make(ia,ib,node,it,rho)
                        except ValueError:prev=None;continue
                        L=length(parts);report['math_queries']+=1
                        if prev and (L-452)*(prev[1]-452)<=0:
                            lo,hi=prev[0],rho;lv=prev[1]-452
                            try:
                                for _ in range(31):
                                    r=(lo+hi)/2;trial=make(ia,ib,node,it,r);v=length(trial)-452
                                    if lv*v<=0:hi=r
                                    else:lo=r;lv=v
                                trial=make(ia,ib,node,it,(lo+hi)/2)
                                if min_radius(trial)>=30-1e-7:
                                    pts=[q for s in trial for q in samples(s,5)]
                                    if all(-141.5<q[0]<183.5 and abs(q[1])<98 and -48<q[2]<112 for q in pts):
                                        # Ranking only: actual source geometry decides clearance below.
                                        score=max(abs(q[1]) for q in pts)+max(0,40-min(q[2] for q in pts))*2
                                        report['candidates'].append(dict(ia=ia,ib=ib,node=list(node),it=it,rho=(lo+hi)/2,score=score,parts=trial,length_mm=length(trial),min_R_mm=min_radius(trial)))
                            except ValueError:pass
                        prev=(rho,L)
                    report['domains_completed']+=1
                    if stop:break
                if stop:break
            if stop:break
        print('Side domains',ia,'math',report['math_queries'],'candidates',len(report['candidates']),flush=True);save()
        if stop:break
    # Every stored candidate can be resumed without rerunning the math search.
    boxes={n:s.BoundBox for n,s in scene.items()};valid={};save()
    priority=lambda n: 0 if ('PWM1608' in n or 'U1_Adapter' in n) else 1 if n.startswith('REV3:PCA:') else 2
    ordered=sorted(scene,key=priority)
    for ci,c in sorted(enumerate(report['candidates']),key=lambda x:x[1]['score'])[:50]:
        if time.monotonic()-tick>230:break
        pts=[q for s in c['parts'] for q in samples(s,5)]
        row=dict(candidate_index=ci,completed_queries=[],failures=[],holds=[],self_queries=[])
        if not all(outer.isInside(A.Vector(*q),1e-6,True) for q in pts):
            row['failures'].append(dict(outer='Actual source sample outside'));report['exact'].append(row);save();continue
        w=wire(c['parts']);gap=w.distToShape(surface)[0];row['outer_gap_mm']=gap
        if gap<5.75-1e-6:row['failures'].append(dict(outer_gap_mm=gap,required_mm=5.75))
        # Nonadjacent edges: 5mm jacket plus0.2mm air. Adjacent tangent mates
        # share an endpoint intentionally; radius30 prevents local folding.
        if not row['failures']:
            offsets=[sum(s['length'] for s in c['parts'][:i]) for i in range(len(c['parts']))]
            def intrinsic(i,point):
                s=c['parts'][i];v=sub(list(point),s['start'])
                if s['kind']=='line':return offsets[i]+norm(v)
                a=math.atan2(dot(v,s['tangent']),s['radius']-dot(v,s['bend']))
                return offsets[i]+s['radius']*a
            for i,s in enumerate(w.Edges):
                for j in range(i+2,len(w.Edges)):
                    t=w.Edges[j]
                    if not near(s.BoundBox,t.BoundBox,5.2):continue
                    d,witnesses,_=s.distToShape(t)
                    separated=any(abs(intrinsic(i,p)-intrinsic(j,q))>8 for p,q in witnesses)
                    row['self_queries'].append(dict(i=i,j=j,gap_mm=d,required_mm=5.2,nonlocal_witness=separated,intrinsic_local_neighbour_budget_mm=8))
                    if separated and d<5.2-1e-6:row['failures'].append(dict(self_edges=[i,j],gap_mm=d));break
                if row['failures']:break
        if not row['failures']:
            for n in ordered:
                s=scene[n]
                if not s.Solids or not near(w.BoundBox,boxes[n],3.75):continue
                if time.monotonic()-tick>230:row['holds'].append('Time cap; exact completed queries saved');break
                ownboot=n in ('PiBudget:USB_A_data_boot','CurrentBUS:USB_C_Overmould')
                test=wire(c['parts'][1:-1]) if ownboot else w
                required=2.5 if ownboot else 2.7 if ('wire' in meta[n].get('kind','') or n.startswith(('End:','BankFullPrefix:','Factory:'))) else 3.75
                if n==bus['name']:
                    inv=test.copy();inv.Placement=bus['inverse']*inv.Placement
                    d=inv.distToShape(bus['original'])[0];method=bus['method']
                else:
                    if n not in valid:valid[n]=s.isValid()
                    if not valid[n]:row['holds'].append(n);continue
                    d=test.distToShape(s)[0];method='Current actual saved source'
                query=dict(name=n,gap_mm=d,required_mm=required,method=method,reservation='reservation' in meta[n].get('kind',''))
                row['completed_queries'].append(query)
                if d<required-1e-6:row['failures'].append(query);break
                if len(row['completed_queries'])%20==0:
                    report['in_progress']=row;save()
        report.pop('in_progress',None);report['exact'].append(row);save()
        print('Side exact',ci,'pairs',len(row['completed_queries']),'fail',row['failures'][:1],'holds',row['holds'],flush=True)
        if not row['failures'] and not row['holds']:
            report['chosen_curve']=dict(candidate_index=ci,parts=c['parts'],scope='Current query only; roots/tools/full middles/motion stillOPEN')
            bundle=dest.with_suffix('.zip')
            with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('USB_curve.brep',w.exportBrepToString().encode())
            report.update(bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle));break
    report['status']='SIDE_USB_CURVE_CURRENT_QUERY_CLEAR_ROOTS_FULL_HARNESS_MOTION_OPEN' if report['chosen_curve'] else 'BOUNDED_SIDE_TRANSFER_NO_QUALIFIED_ROUTE_NOT_INFEASIBILITY_PROOF'
    report['open']=['No full123wire/motion/roots/tools or source mating guarantees',
        'Same452outside allowance still depends on delivered mould/cable fit',
        'Whole space acceptance and all retained factory paths remain N01 gate']
    save();print(json.dumps(dict(status=report['status'],math=report['math_queries'],candidates=len(report['candidates']),exact=len(report['exact']),seconds=report['worker_seconds'])),flush=True)


if __name__=='__main__':main()
