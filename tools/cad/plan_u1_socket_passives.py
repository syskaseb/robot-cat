"""One common forming plan for all U1-module leads and fixed jumpers.

Manufacturer endpoints/body limits are retained; bends, sleeve OD, solder
extent and board thickness are explicit prototype acceptance assumptions.
This fast mutual-space check is not whole-robot or electrical acceptance.
"""
import json,math,time
from pathlib import Path
import FreeCAD as A
import Part
from plan_current_main_sources import ROOT,OUT,SHA
import plan_u1_socket_links as L

TOP=84.3202


def rounded(points,r=.5):
    pts=[A.Vector(*p) for p in points];edges=[];last=pts[0]
    for i,q in enumerate(pts[1:-1],1):
        a=q-pts[i-1];b=pts[i+1]-q;a.normalize();b.normalize()
        angle=math.acos(max(-1,min(1,a.dot(b))))
        if angle<1e-7:continue
        assert angle<math.pi-1e-6
        t=r*math.tan(angle/2)
        assert (q-pts[i-1]).Length>=t-1e-7 and (pts[i+1]-q).Length>=t-1e-7
        enter=q-a*t;leave=q+b*t;centre=enter+(b-a*a.dot(b)).normalize()*r
        mid=centre+((enter-centre)+(leave-centre)).normalize()*r
        if (enter-last).Length>1e-7:edges.append(Part.makeLine(last,enter))
        edges.append(Part.Arc(enter,mid,leave).toShape());last=leave
    if (pts[-1]-last).Length>1e-7:edges.append(Part.makeLine(last,pts[-1]))
    w=Part.Wire(edges);assert w.isValid();return w


def curves(p):
    result={}
    for q in p['leads']:
        w=rounded(q['vertices_mm'],q['bend_radius_project_mm'])
        if q.get('sleeve_candidate'):
            a=5 if q['part']=='U_PWM' else .8;b=w.Length-2.9
            assert a<b
            for label,lo,hi,rad in [('BodyBare',0,a,.3),('Sleeved',a,b,.6),('PadBare',b,w.Length,.3)]:
                result[q['ref']+'/'+label]=(trim(w,lo,hi),rad,q['net'])
        else:result[q['ref']]=(w,q['space_radius_mm'],q['net'])
    return result


def trim(w,lo,hi):
    edges=[];s=0
    for e in w.Edges:
        a=max(0,lo-s);b=min(e.Length,hi-s)
        if b-a>1e-7:edges.append(e.Curve.toShape(e.getParameterByLength(a),e.getParameterByLength(b)))
        s+=e.Length
    result=Part.Wire(edges);assert result.isValid()
    assert abs(result.Length-(hi-lo))<1e-5
    return result


def plan(p,m):
    terms={q['ref']:q for q in p['terminals']};rows=[]
    def lead(ref,net,points,stock,r=.5,sleeved=False,part=None):
        c=rounded(points,r)
        required=c.Length+.5
        rows.append(dict(ref=ref,part=part or ref.split('.')[0],net=net,vertices_mm=points,
            bend_radius_project_mm=r,guide_mm=c.Length,trim_reserve_mm=.5,
            required_lead_stock_mm=required,source_available_min_mm=stock,
            metal_diameter_project_mm=.6,space_radius_mm=.6 if sleeved else .3,
            sleeve_candidate='CR3042-000' if sleeved else None,
            sleeve_finished_OD_project_upper_mm=1.2 if sleeved else None,
            scope='Fixed component lead, not flexible cable, not cable strain relief'))
    for c in p['parts']:
        x,y,z=c['body_center_local_mm'];z+=TOP
        if c['ref'].startswith('R'):
            ends=[terms[n] for n in c['ends']];a,b=ends
            dx=b['x']-a['x'];dy=b['y']-a['y'];d=math.hypot(dx,dy);u=[dx/d,dy/d]
            for i,t in enumerate(ends):
                sign=-1 if i==0 else 1
                start=[91.59+x+sign*1.8*u[0],y+sign*1.8*u[1],z]
                xy=[91.59+t['x'],t['y']]
                lead(c['ref']+'.'+str(i+1),t['net'],[start,[*xy,z],[*xy,TOP-2.6]],29,
                     sleeved=c['ref'] in ('R15','R16'),part=c['ref'])
        elif c['ref'] in ('C_IN','C_OUT'):
            resin_bottom=z-c['body_size_mm'][2]/2
            for i,n in enumerate(c['ends'],1):
                t=terms[n];xx=91.59+t['x'];start=[xx,y,resin_bottom];end=[xx,t['y'],TOP-2.6]
                vv=[start,end] if abs(y-t['y'])<1e-6 else [start,[xx,y,TOP+1],[xx,t['y'],TOP+1],end]
                lead(c['ref']+'.'+str(i),t['net'],vv,7,part=c['ref'])
        elif c['ref']=='U_PWM':
            bottom=z-c['body_size_mm'][2]/2
            for pin,xx in ((1,x-1.27),(2,x),(3,x+1.27)):
                t=terms['U_PWM.'+str(pin)];a=[91.59+xx,y,bottom];b=[91.59+t['x'],t['y'],TOP-2.6]
                lead('U_PWM.'+str(pin),t['net'],[a,[a[0],a[1],bottom-3.6],
                    [b[0],b[1],bottom-5.6],b],12.7,r=1,sleeved=True,part='U_PWM')
    chip={q['chip_pin']:q for q in m['rows']}
    for c in p['adapter_local_parts']:
        x,y,z=c['body_center_local_mm'];bottom=TOP+z-c['body_size_mm'][2]/2
        for i,pin in enumerate(c['between_chip_pins']):
            q=chip[pin];ex,ey=q['footprint_eagle_xy_mm']
            pad=[90.32-(ey-17.78),-3.81+(17.78-ex-8.89),96.9602]
            a=[91.59+x+(-1.27 if i==0 else 1.27),y,bottom]
            lead(c['ref']+'.'+str(i+1),terms['U1.'+str(pin)]['net'],
                [a,[a[0],a[1],bottom-1.52],[pad[0],pad[1],bottom-1.52],pad],7,r=.35,part=c['ref'])
    assert len(rows)==39,len(rows)
    for pin,q in chip.items():
        t=terms['U1.'+str(pin)];x=91.59+t['x'];y=t['y']
        for label,z0,z1 in [('FemaleTail',81.3202,84.3202),('MaleTail',96.9602,98.3602)]:
            rows.append(dict(ref=label+str(pin),part=label,net=t['net'],vertices_mm=[[x,y,z0],[x,y,z1]],
                bend_radius_project_mm=.5,guide_mm=z1-z0,source_available_min_mm=z1-z0,
                required_lead_stock_mm=z1-z0,space_radius_mm=.64/math.sqrt(2),
                qualification='Circumscribed0.64mm square pin envelope, not round actual pin; male tail trim<=1.4mm above adapter'))
    return dict(status='PENDING',selected=False,E1_complete=False,physical_pass=False,leads=rows,
        assumptions=['Single hand-formed component lead bends, not manufacturer forming approval',
                     'Bare fixed short logic leads within isolated PCB/carrier space; long R15/R16 and regulator leads individually sleeved',
                     'No separate cosmetic underside shell: retained PETG carrier floor isolates underside; fixed-wire capture and no loose conductive objects required',
                     'Two caps solder directly to source TSSOP power/ground pads; no remote decoupler substitution',
                     '0.6mm bare lead envelope is project allowance; MRS16 catalogue lead nominal0.5 and minimum stock29mm',
                     'All actual solder joints/insulation retained for phase2 unpowered inspection, no energized acceptance'],
        chip_fine_pitch_solder_gate='Inspect all0.65mm pitch pads/adjacent pins and both decoupler joints under magnification before any power')


def run():
    tick=time.monotonic();f=OUT/'u1-socket-carrier-plan.json';mf=OUT/'u1-documented-adapter.json'
    p=plan(json.loads(f.read_text()),json.loads(mf.read_text()));all_curves=curves(p)
    lf=OUT/'u1-socket-links-plan.json';lp=json.loads(lf.read_text());assert not lp['conflicts']
    for q in lp['links']:all_curves[q['ref']]=(L.path(q['start_mm'],q['end_mm'],q['underside_plane_world_mm'],q['via_xy_mm']),.4,q['net'])
    all_curves['JG_COMB']=(Part.makeLine(*[A.Vector(*v) for v in lp['ground_bus']['centreline_mm']]),.25,'G_SYS')
    p.update(pairs=0,conflicts=[],same_net_touch_requirements=[],stock_failures=[])
    for q in p['leads']:
        if q['required_lead_stock_mm']>q['source_available_min_mm']+1e-5:p['stock_failures'].append(q)
    names=list(all_curves)
    for i,a in enumerate(names):
        c,ra,na=all_curves[a]
        for b in names[i+1:]:
            if a.split('/')[0]==b.split('/')[0]:continue  # Consecutive regions of ONE continuous physical lead.
            d,rb,nb=all_curves[b];bb=c.BoundBox;bb.enlarge(ra+rb+.1)
            if not bb.intersect(d.BoundBox):continue
            p['pairs']+=1;dist=c.distToShape(d)[0]
            if dist<ra+rb+.1-1e-5:
                row=dict(a=a,b=b,distance_mm=dist,required_mm=ra+rb+.1,net_a=na,net_b=nb)
                (p['same_net_touch_requirements'] if na==nb else p['conflicts']).append(row)
    p['status']='LOCAL_LEAD_FORMING_REQUIRES_CHANGE' if p['conflicts'] or p['stock_failures'] else 'LOCAL_LEAD_FORMING_MUTUAL_ONLY_MATERIAL_AND_JOINTS_OPEN'
    refs=[f,mf,lf,Path(__file__),Path(L.__file__),ROOT/'hardware/reference/pwm-passives-2026-09-26/MRS-outline.png',
          ROOT/'hardware/reference/u1-socket-connectors-2026-10-12/sleeve-facts.json']
    p['source_sha256']={r.relative_to(ROOT).as_posix():SHA(r) for r in refs};p['worker_seconds']=round(time.monotonic()-tick,3)
    (OUT/'u1-socket-passive-leads.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:p[k] for k in ('status','pairs','conflicts','same_net_touch_requirements','stock_failures','worker_seconds')}),flush=True)


if __name__=='__main__':run()
