"""Receive ONLY unfinished frozen USB candidates; do not rerun failed ones.

Per-edge broadphase avoids testing every part inside the WHOLE cable bbox.
Reuse exact recorded pair distances when source pins are unchanged. Mixed
"purchased_or_complete_wire" metadata is NOT proof that a fuse is a wire.
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
from feline_tangent_routes import dot,sub,norm
from plan_feline_joint_usb_route import wire
from check_feline_all_current_lands import near


def main():
    tick=time.monotonic();src=OUT/'n01-usb-side-transfer.json';dest=OUT/'n01-usb-side-transfer-received.json';assert not dest.exists()
    parent=json.loads(src.read_text());assert parent['status']!='RUNNING_SHARED_SIDE_TRANSFER_USB'
    for p,h in parent['source_sha256'].items():assert sha(ROOT/p)==h,p
    report=dict(status='RUNNING_UNFINISHED_FROZEN_USB_RECEIVER',selected=False,N01_complete=False,physical_pass=False,
        source_sha256={src.relative_to(ROOT).as_posix():sha(src),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        rejected_parent_candidates_skipped=[],exact=[],chosen_curve=None,new_pairs=0,reused_pairs=0,errors=[],
        broadphase='Union of individual exact edge bounding boxes, not one whole cable bbox; bbox itself is never a contact verdict',
        scope='Same frozen source/curves only. No third routing family or component offset. Full wiring/roots/tools/motion OPEN')
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    save();scene,meta,pins,bus=build();report['source_sha256'].update(pins)
    reader=SavedShapes();outer=reader.shape(OUT/'central-cassette-envelope/FelineLayoutEnvelope.FCStd','TorsoEnvelope');surface=Part.makeCompound(outer.Faces)
    assert outer.isValid();report['source_sha256'].update(reader.hashes)
    old={r['candidate_index']:r for r in parent['exact']};boxes={n:s.BoundBox for n,s in scene.items()};valid={}
    ordered=sorted(scene,key=lambda n:0 if 'CP2_ATO' in n else 1 if n.startswith(('REV3:PCA:','Ref_Material_F_PI')) else 2 if ('PWM1608' in n or 'U1_Adapter' in n) else 3)
    for ci,c in sorted(enumerate(parent['candidates']),key=lambda x:x[1]['score']):
        if time.monotonic()-tick>180:break
        previous=old.get(ci,{})
        if previous.get('failures'):
            report['rejected_parent_candidates_skipped'].append(ci);continue
        parts=c['parts'];w=wire(parts);edges=w.Edges;bb=[e.BoundBox for e in edges]
        row=dict(candidate_index=ci,completed_queries=[],failures=[],holds=[],self_queries=[],reused_pair_count=0)
        gap=previous.get('outer_gap_mm')
        if gap is None:
            if not outer.isInside(A.Vector(*parts[0]['start']),1e-6,True):row['failures'].append(dict(outer='Start outside'))
            gap=w.distToShape(surface)[0]
        row['outer_gap_mm']=gap
        if gap<5.75-1e-6:row['failures'].append(dict(outer_gap_mm=gap,required_mm=5.75))
        if not row['failures']:
            if previous and not previous.get('failures'):
                row['self_queries']=previous['self_queries'];row['source_self_gate_reused']=True
            else:
                offsets=[sum(s['length'] for s in parts[:i]) for i in range(len(parts))]
                def intrinsic(i,point):
                    s=parts[i];v=sub(list(point),s['start'])
                    if s['kind']=='line':return offsets[i]+norm(v)
                    return offsets[i]+s['radius']*math.atan2(dot(v,s['tangent']),s['radius']-dot(v,s['bend']))
                for i,s in enumerate(edges):
                    for j in range(i+2,len(edges)):
                        if not near(bb[i],bb[j],5.2):continue
                        d,witnesses,_=s.distToShape(edges[j]);separated=any(abs(intrinsic(i,p)-intrinsic(j,q))>8 for p,q in witnesses)
                        row['self_queries'].append(dict(i=i,j=j,gap_mm=d,nonlocal_witness=separated,required_mm=5.2))
                        if separated and d<5.2-1e-6:row['failures'].append(dict(self_edges=[i,j],gap_mm=d));break
                    if row['failures']:break
        cache={r['name']:r for r in previous.get('completed_queries',[])}
        if not row['failures']:
            for n in ordered:
                s=scene[n]
                if not s.Solids or not any(near(b,boxes[n],3.75) for b in bb):continue
                if time.monotonic()-tick>180:row['holds'].append('Time cap; preserve exact completed pairs');break
                ownboot=n in ('PiBudget:USB_A_data_boot','CurrentBUS:USB_C_Overmould')
                actual_wire=(n.startswith(('End:','BankFullPrefix:','Factory:','REV3Station:','REV3:PCA:')) or n in ('W043','W077','W078') or meta[n].get('kind') in ('wire','actual_wire')) and not n.startswith('Ref_Material_')
                required=2.5 if ownboot else 2.7 if actual_wire else 3.75
                if n in cache:
                    d=cache[n]['gap_mm'];method=cache[n]['method'];row['reused_pair_count']+=1;report['reused_pairs']+=1
                else:
                    test=wire(parts[1:-1]) if ownboot else w
                    if n==bus['name']:
                        inv=test.copy();inv.Placement=bus['inverse']*inv.Placement;d=inv.distToShape(bus['original'])[0];method=bus['method']
                    else:
                        if n not in valid:valid[n]=s.isValid()
                        if not valid[n]:row['holds'].append(n);continue
                        d=test.distToShape(s)[0];method='Actual current source; per-edge broadphase'
                    report['new_pairs']+=1
                q=dict(name=n,gap_mm=d,required_mm=required,method=method,source_pair_reused=n in cache)
                row['completed_queries'].append(q)
                if d<required-1e-6:row['failures'].append(q);break
                if len(row['completed_queries'])%10==0:report['in_progress']=row;save()
        report.pop('in_progress',None);report['exact'].append(row);save()
        print('Frozen receiver',ci,'new',report['new_pairs'],'reused',report['reused_pairs'],'fail',row['failures'][:1],'holds',row['holds'],flush=True)
        if not row['failures'] and not row['holds']:
            report['chosen_curve']=dict(candidate_index=ci,parts=parts,length_mm=c['length_mm'],min_R_mm=c['min_R_mm'],current_query_only=True)
            bundle=dest.with_suffix('.zip')
            with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('USB_curve.brep',w.exportBrepToString().encode())
            report.update(bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle));break
    report['status']='FROZEN_USB_QUERY_CLEAR_FULL_WIRING_ROOTS_TOOLS_MOTION_OPEN' if report['chosen_curve'] else 'FROZEN_USB_RECEIVER_NO_QUALIFIED_CURVE_NOT_INFEASIBILITY_PROOF'
    report['open']=['F_PWM unplaced template/full123middles/allroots/tools/36poses not qualified by this query',
        'Factory500 and mould sizes remain nominal delivery fit assumptions, no physicalPASS']
    save();print(json.dumps(dict(status=report['status'],exact=len(report['exact']),new=report['new_pairs'],reused=report['reused_pairs'],skipped=len(report['rejected_parent_candidates_skipped']),seconds=report['worker_seconds'])),flush=True)


if __name__=='__main__':main()
