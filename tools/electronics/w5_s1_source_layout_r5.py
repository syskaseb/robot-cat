"""One outside-bank source family with full 3D approach geometry.

R4 is rejected by real bank wires, not just PETG. Do not trim those wires or
waive the bank. Lift both P_SYS outputs before crossing their inlet family;
give S1 two vertical left approaches and one separate right approach. The
remaining P_REAR lead dips diagonally below its adjacent bought pigtail.
This changes the cover envelope; a native guarded E6 replacement is required
before selecting this candidate, not inferred from a clear route check.
"""
import math,json
from pathlib import Path
import w5_s1_source_layout_r4 as parent
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import add,mul,norm,X,Y,Z
from servo_fuse_inputs_r1 import save,sha
ROOT=parent.ROOT
OUT=ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r5'
EZ=parent.ENTRY_Z;LEFT=parent.ENTRY_LEFT;RIGHT=parent.ENTRY_RIGHT

def layout():
    rows=[]
    def finish(w,a,b,c,end):
        assert norm([x-y for x,y in zip(c.p,end)])<1e-7
        assert norm([x-y for x,y in zip(c.t,X if w in ('W064','W067') else mul(X,-1))])<1e-7
        length=sum(e['length_mm'] for e in c.edges)
        rows.append(dict(wire=w,a=a,b=b,start=c.edges[0]['start'],end=list(c.p),edges=c.edges,
            wire_sku='HELU23802',OD_mm=4.2,minimum_static_radius_mm=25.2,
            exposed_path_mm=length,nominal_trial_blank_mm=math.ceil((length+52.73)/10)*10,
            strip_allowance_mm=22.73,trial_reserve_mm=30,actual_cut_mm=None,
            ring_seating_Z_provisional_mm=62,wire_entry_from_exact_TE_STEP=True,
            selected=False,physical_pass=False))
    c=CentreLine([-39,11,113.5],Y)
    c.arc(Z);c.line([-39,36.2,166.5]);c.arc(mul(X,-1))
    c.line([-81.8,36.2,191.7]);c.arc(Y);c.line([-107,95.2,191.7]);c.arc(X)
    c.line([LEFT-50.4,120.4,191.7]);c.arc(mul(Y,-1));c.arc(mul(Z,-1))
    c.line([LEFT-25.2,70,EZ+25.2]);c.arc(X)
    finish('W064','P_FRONT.1','S1.3',c,[LEFT,70,EZ])
    c=CentreLine([32,13.6,129],X)
    theta=math.pi/6
    c.arc([0,-math.cos(theta),-math.sin(theta)])
    c.arc([0,-math.sin(theta),math.cos(theta)],angle=theta)
    c.line([c.p[0],-133,c.p[2]]);c.arc(mul(Z,-1));c.arc(X)
    c.shift([0,0,EZ-c.p[2]]);c.line([RIGHT,c.p[1],EZ]);c.arc(Y)
    c.line([RIGHT+25.2,44.8,EZ]);c.arc(mul(X,-1))
    finish('W065','P_REAR.1','S1.6',c,[RIGHT,70,EZ])
    c=CentreLine([-69,7,135.5],mul(Y,-1))
    c.arc(Z);c.line([-69,-18.2,166.5]);c.arc(mul(X,-1))
    c.line([-101.8,-18.2,191.7]);c.arc(Y);c.line([-127,107.2,191.7]);c.arc(X)
    c.line([LEFT-50.4,132.4,191.7]);c.arc(mul(Y,-1));c.arc(mul(Z,-1))
    c.line([LEFT-25.2,82,EZ+25.2]);c.arc(X)
    finish('W067','P_SYS.3','S1.2',c,[LEFT,82,EZ])
    c=CentreLine([-61.5,7,135.5],mul(Y,-1))
    c.line([-61.5,-.5,135.5]);c.arc(Z);c.line([-61.5,-25.7,174]);c.arc(X)
    c.line([RIGHT,-25.7,199.2]);c.arc(Y);c.line([RIGHT+25.2,56.8,199.2]);c.arc(mul(Z,-1))
    c.line([RIGHT+25.2,82,EZ+25.2]);c.arc(mul(X,-1))
    finish('W068','P_SYS.4','S1.5',c,[RIGHT,82,EZ])
    return rows

def main():
    proof=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r4/checks.json'
    r=json.loads(proof.read_text(encoding='utf-8'))
    assert r['status']=='SOURCE_JOINT_REJECTED' and len(r['hits'])==41 and not r['errors']
    assert all(sha(ROOT/k)==v for k,v in {**r['source_sha256'],**r['files']}.items())
    parent.OUT=OUT;parent.layout=layout;parent.main()
    p=OUT/'intent.json';r=json.loads(p.read_text(encoding='utf-8'))
    r['status']='FOUR_SOURCE_FULL_3D_APPROACH_CANDIDATE_UNSELECTED'
    r['source_sha256'].update({q.relative_to(ROOT).as_posix():sha(q) for q in [Path(__file__),proof]})
    r['new_cover_required']=True
    r['assumptions'].append('Upper source axisZ191.7/199.2 cannot claim unchanged E6 roof. Construct a shared guarded, removable replacement after current non-PETG clearance proof.')
    save(p,r)

if __name__=='__main__':main()
