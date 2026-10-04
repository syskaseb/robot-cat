"""Four complete nominal S1 centre-lines, independent of the leg worker.

Use the selected switch holes and original ring directions. The old920mm
allowance is not a routed harness. Save analytic R25.2 arcs before CAD checks;
no collision, native support, stock selection or physical PASS is inferred.
"""
from datetime import datetime, timezone
from pathlib import Path
import json, math, sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r1'
R=25.2
X=[1,0,0];Y=[0,1,0];Z=[0,0,1]


def add(a,b):return [x+y for x,y in zip(a,b)]
def mul(a,s):return [x*s for x in a]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def norm(a):return math.sqrt(dot(a,a))


class CentreLine:
    def __init__(self,start,tangent):
        self.p=list(start);self.t=list(tangent);self.edges=[]

    def line(self,end):
        delta=[x-y for x,y in zip(end,self.p)];length=norm(delta)
        assert length>1e-8
        tangent=mul(delta,1/length)
        assert norm([x-y for x,y in zip(tangent,self.t)])<1e-7,'Non-tangent line'
        self.edges.append(dict(kind='line',start=list(self.p),end=list(end),length_mm=length))
        self.p=list(end)

    def arc(self,normal,angle=math.pi/2):
        assert abs(norm(normal)-1)<1e-8 and abs(dot(self.t,normal))<1e-8
        origin=list(self.p);tangent=list(self.t)
        def point(a):return add(origin,add(mul(tangent,R*math.sin(a)),mul(normal,R*(1-math.cos(a)))))
        end=point(angle)
        self.edges.append(dict(kind='arc',start=origin,mid=point(angle/2),end=end,
                               radius_mm=R,angle_rad=angle,length_mm=R*angle))
        self.p=end;self.t=add(mul(tangent,math.cos(angle)),mul(normal,math.sin(angle)))

    def shift(self,delta):
        height=norm(delta);assert 0<height<2*R and abs(dot(self.t,delta))<1e-8
        normal=mul(delta,1/height);tangent=list(self.t)
        angle=math.acos(1-height/(2*R))
        self.arc(normal,angle)
        self.arc(add(mul(tangent,math.sin(angle)),mul(normal,-math.cos(angle))),angle)


def layout():
    # The three occupied P_REAR centres are a prototype map, not certified
    # NKK/WAGO dimensions: two existing source ends stay atY-6.8/+6.8;
    # unused far-negative cage becomes S1 feed .1 atY-13.6.
    starts={'W064':[-39,11,113.5],'W065':[32,-13.6,129],
            'W067':[-69,-11,113.5],'W068':[-61.5,-11,113.5]}
    specs={'W064':('P_FRONT.1','S1.3',[117-22.123,70,62]),
           'W065':('P_REAR.1','S1.6',[129+22.123,70,62]),
           'W067':('P_SYS.3','S1.2',[117-22.123,82,62]),
           'W068':('P_SYS.4','S1.5',[129+22.123,82,62])}
    routes=[]
    for wire,(port,terminal,end) in specs.items():
        tangent=X if wire=='W065' else Y if wire=='W064' else mul(Y,-1)
        c=CentreLine(starts[wire],tangent)
        if wire=='W065':
            c.line(add(c.p,mul(X,10)));c.arc(Y)
            c.line([c.p[0],95.2,129]);c.arc(mul(Z,-1))
            c.line([c.p[0],c.p[1],87.2]);c.arc(X)
        else:
            c.line(add(c.p,mul(tangent,2.5)));c.arc(mul(Z,-1))
            c.line([c.p[0],c.p[1],74 if wire=='W068' else 80]);c.arc(X)
            if wire=='W064':c.shift([0,70-c.p[1],0])
            else:
                c.arc(Y)
                c.line([c.p[0],(132.4 if wire=='W068' else 82)-R,c.p[2]])
                c.arc(X)
            c.line([70 if wire=='W068' else 63,c.p[1],c.p[2]])
            c.shift([0,0,62-c.p[2]])
        if wire in ('W065','W068'):
            c.line([160,c.p[1],62]);c.arc(mul(Y,-1));c.arc(mul(X,-1))
        c.line(end)
        length=sum(e['length_mm'] for e in c.edges)
        blank=math.ceil((length+14+8.73+30)/10)*10
        routes.append(dict(wire=wire,a=port,b=terminal,wire_sku='HELU23802',
            wire_mm2=4,OD_mm=4.2,radius_mm=R,start=starts[wire],end=end,
            edges=c.edges,exposed_path_mm=length,nominal_trial_blank_mm=blank,
            end_allowance_mm={'WAGO615_max_strip':14,'TE130171_max_strip':8.73,'unpowered_trial_reserve':30},
            actual_cut_mm=None,port_positions_provisional=True,physical_pass=False))
    return routes


def main():
    started=datetime.now(timezone.utc)
    assert not (OUT/'intent.json').exists(),'Preserve the saved intent'
    graph=ROOT/'hardware/electronics/full-cat/source-switch-selected-r1/body-harness.json'
    selected=ROOT/'hardware/manufacturing/one-batch-prototype-r53/selection.json'
    termination=ROOT/'hardware/electronics/power-platform/switch-terminations-p0.json'
    source=ROOT/'hardware/electronics/full-cat/source-switch-selected-r1/interface.json'
    rear=ROOT/'hardware/electronics/full-cat/servo-fuse-rl-source-complete-r2/checks.json'
    rear2=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-source-complete-r8/checks.json'
    conductor={r['id']:r for r in json.loads(graph.read_text(encoding='utf-8'))['conductors']}
    routes=layout()
    for row in routes:assert {row['a'],row['b']}=={conductor[row['wire']]['a'],conductor[row['wire']]['b']}
    process=json.loads(termination.read_text(encoding='utf-8'))
    assert process['s1_crimp_process']['strip_length_mm']==[7.94,8.73]
    assert process['terminal_candidate']['hole_center_to_wire_entry_max_mm']==22.123
    src=json.loads(source.read_text(encoding='utf-8'));assert src['nominal_wire_blanks_mm']['W066']==330
    total=sum(r['nominal_trial_blank_mm'] for r in routes)
    finished=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    save(OUT/'intent.json',dict(status='FOUR_COMPLETE_ANALYTIC_PATHS_CAD_AND_RESTRAINTS_OPEN',
        routes=routes,legacy_unqualified_allowance_mm=920,new_nominal_trial_total_mm=total,
        added_rings=0,rings_installed=4,original_NKK_screws_retained=4,
        bought_wire_selected=False,body_source_stock_after_all_other_allocations_pending=True,
        switch_axis_xy_mm=[123,70],ring_seating_z_assumption_mm=62,
        assumptions=['Exact delivered S1 mounting stack/terminal-number orientation/pocket and bearing still need dry-fit.',
            'Source connector positions are the selected prototype map, not delivered port measurements.',
            'P_REAR.1 uses the unoccupied far-negative physical cage; retain currentW044Y-6.8 andW052Y+6.8.',
            'Original left/right ring direction retained. Do not use wire length bounds as collision or support proof.'],
        open=['All four routes versus the current populated body and leg candidate.',
              'Insulation-only supports on both ends and below the source bridge; guard exposed edge crossings.',
              'Exact four ring envelopes and tool access on the removed Deck.',
              'Reconcile HELU stock once with all already-selected bank/source leads.'],
        native_supports_ready=False,selected=False,W5_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (graph,selected,termination,source,rear,rear2,Path(__file__))},
        started_utc=started.isoformat(),finished_utc=finished.isoformat(),worker_wall_seconds=(finished-started).total_seconds()))
    print(json.dumps(dict(routes=4,legacy_mm=920,nominal_trial_mm=total,selected=False)))


if __name__=='__main__':main()
