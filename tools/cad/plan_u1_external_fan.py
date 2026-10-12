"""All22 real external ends, independent grip lands and common fan together.

Bounded prefix gate before global routes/native grip details. A failed endpoint
is not patched by changing an unrelated middle curve. Old service and static
proofs are reused, never rerun here. No selection or physical acceptance.
"""
import json,math,time,sys
from pathlib import Path
import FreeCAD as A
import Part
from u1_socket_current_context import context
from plan_current_main_sources import ROOT,OUT,SHA
from plan_u1_socket_passives import rounded
from plan_current_joined_leg_looms import exact_quarter
from plan_current_mta_interfaces import line
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'electronics'))
import plan_u1_external_interfaces as E


def parts(w):
    out=[]
    for e in w.Edges:
        a=e.valueAt(e.FirstParameter);b=e.valueAt(e.LastParameter)
        q=dict(kind='line' if isinstance(e.Curve,Part.Line) else 'arc',start=list(a),end=list(b),length_mm=e.Length)
        if q['kind']=='arc':q['mid']=list(e.valueAt((e.FirstParameter+e.LastParameter)/2))
        out.append(q)
    return out


def build():
    p=E.build();routes={};bare={};lands=[]
    for q in p['wires']:
        wid=q['id'];fine=q.get('AWG')==30;ends={}
        for side in ('a','b'):
            e=q[side];a=list(e['world_mm']);x,y,z=a;key=wid+'/'+side
            if e['kind']=='current_WAGO_port':
                # Outside the existing G_TAIL5 vertical grip/back atY-44.5.
                # Both quarters and the9mm entry grip are one allocation.
                seg=[line(a,[x+9,y,z])]
                seg.append(exact_quarter(seg[-1]['end'],[1,0,0],[0,-1,0],10))
                seg.append(exact_quarter(seg[-1]['end'],[0,-1,0],[0,0,-1],10))
                seg.append(line(seg[-1]['end'],[seg[-1]['end'][0],seg[-1]['end'][1],z-19]))
                axis=[0,0,-1];land=[a,[x+9,y,z]]
            elif fine:
                if e['kind']=='actual1608pad':
                    i=int(wid[2])-1;yy=-3.81-1.27*i
                    v=[[x,y,z+.5],[x,y,90.3]]
                    if i:v.append([x,yy,90.3])
                    v.extend([[61,yy,90.3],[61,yy,93.]])
                    land=[[62,yy,90.3],[71,yy,90.3]]
                else:
                    v=[[x,y,z+.5],[x,y,86.82],[x,-19,86.82],[x,-19,93.]]
                    land=[[x,-17.5,86.82],[x,-8.5,86.82]]
                seg=parts(rounded(v,.5));axis=[0,0,1]
            else:
                # Pi factory connector has no new bare solder end here.
                start=a if e['kind']=='project40pin_housing_wire_exit' else [x,y,z+1]
                end=[x,y,start[2]+9];seg=[line(start,end)];axis=[0,0,1];land=[start,end]
            if e['kind'] in ('actual1608pad','supplier815revCpad'):
                stop=seg[0]['start'];bare[key]=dict(parts=[line([x,y,81.2202],stop)],
                    radius=.13 if fine else math.sqrt((.129 if q.get('AWG')==26 else .25)/math.pi),
                    ends_on_source_pad=e['ref'],stripped_nominal_mm=stop[2]-81.2202,
                    instruction='Untinned strands through named existing hole, solder only at pad; inspect actual fillet/insulation. Not a free cable grip.')
            radius=q.get('OD_project_upper_mm',1.4)/2
            ends[side]=dict(parts=seg,radius=radius,end_axis=axis,end_mm=seg[-1]['end'],physical_terminal=e['ref'])
            lands.append(dict(wire=wid,side=side,line_mm=land,wire_OD_project_mm=2*radius,
                              owner='Carrier-rooted replaceable insulation grip; not socket bar or copper pad',native_open=True))
        routes[wid]=dict(ends=ends,source=q,actual_cut_mm=None,middle_route_open=True)
    return dict(status='WHOLE11WIRE_PREFIX_PLAN_ONLY',selected=False,E1_complete=False,W5_complete=False,physical_pass=False,
                routes=routes,bare=bare,grip_lands=lands,
                limits='Fine0.5mm bends only fixed1446PWM. All other wires retainR10. No whole cable is declared from these prefixes.',
                required_next=['Qualified end departures -> one common middle allocation including all retained wires/material',
                               'Native independent grips, complete insulation, service, stock and selection'],
                source_sha256={str(Path(E.__file__).relative_to(ROOT)).replace('\\','/'):SHA(Path(E.__file__)),
                               str(Path(__file__).relative_to(ROOT)).replace('\\','/'):SHA(Path(__file__))})


def run():
    tick=time.monotonic();p=build();reader,pins,targets,old=context()
    print('Shared U1 context ready',round(time.monotonic()-tick,2),flush=True)
    curves={}
    from current_prototype_harness_scene import wire
    for n,r in p['routes'].items():
        for side,q in r['ends'].items():curves[n+'/'+side]=(wire(q['parts']),q['radius'])
    curves.update({n+'/bare':(wire(q['parts']),q['radius']) for n,q in p['bare'].items()})
    result=dict(status='PENDING',pairs=0,material_contacts=[],wire_contacts=[],errors=[],selected=False,
                E1_complete=False,W5_complete=False,physical_pass=False)
    def near(s,t,r):
        a=s.BoundBox;a.enlarge(r);return a.intersect(t.BoundBox)
    for n,(c,r) in curves.items():
        for other,s in targets.items():
            if not near(c,s,r):continue
            result['pairs']+=1
            try:
                d=c.distToShape(s)[0]
                if d<r-1e-5:result['material_contacts'].append(dict(a=n,b=other,distance_mm=d,required_mm=r))
            except Exception as e:result['errors'].append(dict(a=n,b=other,error=str(e)))
        for other,(w,rr) in old.items():
            if not near(c,w,r+rr):continue
            result['pairs']+=1
            try:
                d=c.distToShape(w)[0]
                if d<r+rr-1e-5:result['wire_contacts'].append(dict(a=n,b=other,distance_mm=d,required_mm=r+rr))
            except Exception as e:result['errors'].append(dict(a=n,b=other,error=str(e)))
        print('Shared prefix',n,'pairs',result['pairs'],'issues',len(result['material_contacts'])+len(result['wire_contacts']),round(time.monotonic()-tick,2),flush=True)
    names=list(curves)
    for i,n in enumerate(names):
        c,r=curves[n]
        for m in names[i+1:]:
            if n.split('/')[0]==m.split('/')[0]:continue
            d,rr=curves[m]
            if not near(c,d,r+rr):continue
            result['pairs']+=1;gap=c.distToShape(d)[0]
            if gap<r+rr-1e-5:result['wire_contacts'].append(dict(a=n,b=m,distance_mm=gap,required_mm=r+rr))
    result['status']='SHARED_END_DEPARTURES_REQUIRE_LAYOUT_CHANGE' if any(result[k] for k in ('material_contacts','wire_contacts','errors')) else 'SHARED_END_DEPARTURES_CLEAR_MIDDLES_NATIVE_OPEN'
    pins.update((Path(__file__),Path(E.__file__),ROOT/'tools/cad/u1_socket_current_context.py'))
    p['source_sha256'].update(E.build()['source_sha256'])
    (OUT/'u1-external-fan-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    result['source_sha256']={**reader.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in pins}}
    result['plan_sha256']=SHA(OUT/'u1-external-fan-plan.json');result['worker_seconds']=round(time.monotonic()-tick,3)
    (OUT/'u1-external-fan-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':run()
