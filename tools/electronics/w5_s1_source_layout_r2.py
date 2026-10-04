"""A compact joint source candidate, not another scalar lane search.

P_SYS lowers11mm in a new Deck pocket so its S1 mouths are below F_PI.
This necessarily reopens W043/W066 and their supports BEFORE any selection.
Rotate the four S1 rings outward along Y, preserving bolts/holes/net labels.
P_REAR .1 uses the free +13.6 cage; -13.6 is already PWM .4, not vacant.
"""
from datetime import datetime,timezone
from pathlib import Path
import math,json
from w5_s1_source_layout_r1 import CentreLine as Base,add,mul,norm,X,Y,Z
from servo_fuse_inputs_r1 import save,sha

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r2'


class CentreLine(Base):
    def arc(self,normal,angle=math.pi/2,radius=25.2):
        assert abs(norm(normal)-1)<1e-8
        assert abs(sum(a*b for a,b in zip(self.t,normal)))<1e-8
        origin=list(self.p);tangent=list(self.t)
        def point(a):return add(origin,add(mul(tangent,radius*math.sin(a)),mul(normal,radius*(1-math.cos(a)))))
        self.edges.append(dict(kind='arc',start=origin,mid=point(angle/2),end=point(angle),radius_mm=radius,angle_rad=angle,length_mm=radius*angle))
        self.p=point(angle);self.t=add(mul(tangent,math.cos(angle)),mul(normal,math.sin(angle)))


def layout():
    fronts=47.877;rears=104.123
    specs={
        'W064':('P_FRONT.1','S1.3',[-39,11,113.5],[117,fronts,62],Y),
        'W065':('P_REAR.1','S1.6',[32,13.6,129],[129,fronts,62],X),
        'W067':('P_SYS.3','S1.2',[-69,-11,102.5],[117,rears,62],mul(Y,-1)),
        'W068':('P_SYS.4','S1.5',[-61.5,-11,102.5],[129,rears,62],mul(Y,-1))}
    rows=[]
    for wire,(a,b,start,end,tangent) in specs.items():
        c=CentreLine(start,tangent)
        if wire=='W064':
            c.line(add(c.p,mul(Y,.01)));c.arc(mul(Z,-1))
            c.line([c.p[0],c.p[1],87.2]);c.arc(X)
            c.shift([0,fronts-25.2-c.p[1],0]);c.line([117-25.2,c.p[1],62]);c.arc(Y)
        elif wire=='W065':
            # A diagonal YZ descent avoids the blocked high flight over F_AUX.
            delta=[0,fronts-32.7-start[1],62-start[2]];height=norm(delta)
            normal=mul(delta,1/height);c.arc(normal)
            c.line(add(c.p,mul(normal,height-50.4)));c.arc(X)
            c.line([129-32.7,c.p[1],62]);c.arc(Y,radius=32.7)
        else:
            c.shift([0,0,-40.5]);c.arc(mul(X,-1));c.arc(Y)
            final_radius=25.2 if wire=='W067' else 32.7
            lane=rears+final_radius
            c.line([c.p[0],lane-25.2,62]);c.arc(X)
            c.line([end[0]-final_radius,c.p[1],62]);c.arc(mul(Y,-1),radius=final_radius)
        assert norm([x-y for x,y in zip(c.p,end)])<1e-7
        assert norm([x-y for x,y in zip(c.t,Y if wire in ('W064','W065') else mul(Y,-1))])<1e-7
        length=sum(e['length_mm'] for e in c.edges)
        rows.append(dict(wire=wire,a=a,b=b,wire_sku='HELU23802',wire_mm2=4,OD_mm=4.2,
            minimum_static_radius_mm=25.2,start=start,end=end,edges=c.edges,exposed_path_mm=length,
            nominal_trial_blank_mm=math.ceil((length+14+8.73+30)/10)*10,
            end_allowance_mm={'WAGO615_max_strip':14,'TE130171_max_strip':8.73,'unpowered_trial_reserve':30},actual_cut_mm=None))
    return rows


def main():
    started=datetime.now(timezone.utc)
    assert not (OUT/'intent.json').exists()
    OUT.mkdir(parents=True,exist_ok=True)
    rows=layout();graph=ROOT/'hardware/electronics/full-cat/source-switch-selected-r1/body-harness.json'
    conductors={r['id']:r for r in json.loads(graph.read_text(encoding='utf-8'))['conductors']}
    for r in rows:assert {r['a'],r['b']}=={conductors[r['wire']]['a'],conductors[r['wire']]['b']}
    pins=[Path(__file__),Path(__file__).with_name('w5_s1_source_layout_r1.py'),graph,
        ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r1/checks.json',
        ROOT/'hardware/electronics/power-platform/switch-terminations-p0.json',
        ROOT/'tools/electronics/pwm_fused_pigtail_r1.py']
    finished=datetime.now(timezone.utc)
    save(OUT/'intent.json',dict(status='JOINT_SOURCE_CANDIDATE_NOT_SELECTED',routes=rows,
        P_SYS_displacement_mm=[0,0,-11],P_SYS_new_body_bounds_mm=[-87.5,-11,98,-50.5,11,109],
        source_qualified_wires_reopened=['W043','W066'],source_supports_reopened=True,
        P_REAR_project_map={'.1':13.6,'.2':-6.8,'.3':6.8,'.4':-13.6,'.5':0},
        P_REAR_port_census_provisional=True,unchanged_PWM_fourth_cage_preserved=True,
        S1_ring_axis_change='Front pair outward-South, rear pair outward-North; no changed terminal centres, fasteners or nets.',
        new_nominal_trial_total_mm=sum(r['nominal_trial_blank_mm'] for r in rows),
        open=['Verify new P_SYS body/pocket against ALL unchanged owners.',
              'Reroute BOTH W043 and W066 and their real grips; never retain their old qualified count after selecting this displacement.',
              'Check four S1 routes together and against the new six-lead source family.',
              'Construct full-depth Deck pocket/retention and four ring tool clearances; reconcile stock once.'],
        selected=False,native_supports_ready=False,W5_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in pins},
        started_utc=started.isoformat(),finished_utc=finished.isoformat(),worker_wall_seconds=(finished-started).total_seconds()))
    print(json.dumps(dict(routes=4,trial_mm=sum(r['nominal_trial_blank_mm'] for r in rows),reopened=['W043','W066'],selected=False)))


if __name__=='__main__':main()
