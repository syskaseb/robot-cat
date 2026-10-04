"""One complete source/short-AUX branch remap on the same five-port bus.

The centre cage is NOT vacant: XA01 occupies it. Exchange its physical cage
with W065, retaining all five logical labels/nets and all other mouths. The
short XA01 lead is explicitly reconstructed, counted and checked together.
Avoid the XL05 sleeve by an eastward P_SYS exit, and the W061 return with two
matched downward S offsets. Separate upper lanes vertically, not by deleting
real bank wiring. A changed guarded E6 cover/carrier remains mandatory.
"""
from pathlib import Path
import math,json
import w5_s1_source_layout_r4 as parent
from w5_s1_source_layout_r2 import CentreLine
from w5_s1_source_layout_r1 import add,mul,norm,X,Y,Z
from servo_fuse_inputs_r1 import save,sha
ROOT=parent.ROOT
OUT=ROOT/'hardware/electronics/full-cat/w5-s1-source-layout-r6'
EZ=parent.ENTRY_Z;LEFT=parent.ENTRY_LEFT;RIGHT=parent.ENTRY_RIGHT

def layout():
    rows=[]
    def finish(w,a,b,c,end,od=4.2,radius=25.2,sku='HELU23802'):
        assert norm([x-y for x,y in zip(c.p,end)])<1e-7
        length=sum(e['length_mm'] for e in c.edges)
        rows.append(dict(wire=w,a=a,b=b,start=c.edges[0]['start'],end=list(c.p),edges=c.edges,
            wire_sku=sku,OD_mm=od,minimum_static_radius_mm=radius,
            exposed_path_mm=length,nominal_trial_blank_mm=math.ceil((length+52.73)/10)*10,
            strip_allowance_mm=22.73,trial_reserve_mm=30,actual_cut_mm=None,
            ring_seating_Z_provisional_mm=62 if b.startswith('S1') else None,
            wire_entry_from_exact_TE_STEP=b.startswith('S1'),selected=False,physical_pass=False))
    def down_left(c,x,y):
        c.shift([0,10,0]);c.line([x,y+10,128]);c.shift([0,-10,0])
        c.line([x,y,EZ+25.2]);c.arc(X)
    c=CentreLine([-39,11,113.5],Y)
    c.arc(Z);c.line([-39,36.2,166.5]);c.arc(mul(X,-1))
    c.line([-81.8,36.2,191.7]);c.arc(Y);c.line([-107,95.2,191.7]);c.arc(X)
    c.line([LEFT-50.4,120.4,191.7]);c.arc(mul(Y,-1));c.arc(mul(Z,-1))
    down_left(c,LEFT-25.2,70)
    finish('W064','P_FRONT.1','S1.3',c,[LEFT,70,EZ])
    c=CentreLine([32,0,129],X)
    c.arc(Z);c.line([57.2,0,190]);c.arc(X)
    c.line([RIGHT,0,215.2]);c.arc(Y);c.line([RIGHT+25.2,44.8,215.2]);c.arc(mul(Z,-1))
    c.line([RIGHT+25.2,70,EZ+25.2]);c.arc(mul(X,-1))
    finish('W065','P_REAR.1','S1.6',c,[RIGHT,70,EZ])
    c=CentreLine([-69,7,135.5],mul(Y,-1))
    c.arc(Z);c.line([-69,-18.2,182]);c.arc(mul(X,-1))
    c.line([-101.8,-18.2,207.2]);c.arc(Y);c.line([-127,107.2,207.2]);c.arc(X)
    c.line([LEFT-50.4,132.4,207.2]);c.arc(mul(Y,-1));c.arc(mul(Z,-1))
    down_left(c,LEFT-25.2,82)
    finish('W067','P_SYS.3','S1.2',c,[LEFT,82,EZ])
    c=CentreLine([-61.5,7,135.5],mul(Y,-1))
    c.arc(X);c.arc(Z);c.line([-11.1,-18.2,174]);c.arc(X)
    c.line([RIGHT,-18.2,199.2]);c.arc(Y);c.line([RIGHT+25.2,56.8,199.2]);c.arc(mul(Z,-1))
    c.line([RIGHT+25.2,82,EZ+25.2]);c.arc(mul(X,-1))
    finish('W068','P_SYS.4','S1.5',c,[RIGHT,82,EZ])
    # Retain R15 fixed bend rule for the selected 1mm2 red wire. The holder
    # internal input path is still unknown and must not be silently set to0.
    c=CentreLine([32,13.6,129],X)
    delta=[0,4,3];normal=mul(delta,.2);angle=math.acos(1-5/30)
    c.arc(normal,angle=angle,radius=15)
    c.arc(add(mul(X,math.sin(angle)),mul(normal,-math.cos(angle))),angle=angle,radius=15)
    c.line([51,17.6,132])
    finish('XA01','P_REAR.5','F_AUX.in',c,[51,17.6,132],od=2.5,radius=15,sku='HELU23502')
    rows[-1].update(nominal_trial_blank_mm=40,trial_reserve_mm=0,strip_allowance_mm=12,
        complete_prefuse_limit_mm=50,holder_internal_path_mm=None,
        holder_internal_available_budget_mm=50-rows[-1]['exposed_path_mm']-12,
        full_prefuse_length_verified=False)
    return rows

def main():
    proof=ROOT/'hardware/electronics/full-cat/w5-s1-source-check-r5/checks.json'
    old=json.loads(proof.read_text(encoding='utf-8'))
    assert len(old['hits'])==24 and not old['errors']
    assert all(sha(ROOT/k)==v for k,v in {**old['source_sha256'],**old['files']}.items())
    parent.OUT=OUT;parent.layout=lambda:layout()[:4];parent.main()
    path=OUT/'intent.json';record=json.loads(path.read_text(encoding='utf-8'))
    aux=ROOT/'hardware/electronics/full-cat/aux-power-r1/circuit.json'
    branch=next(r for r in json.loads(aux.read_text(encoding='utf-8'))['feeds'] if r['id']=='XA01')
    assert branch['from']=='P0 P_REAR.5' and branch['to']=='F_AUX.in'
    record.update(status='WHOLE_FOUR_SOURCE_AND_SHORT_AUX_BRANCH_CANDIDATE_UNSELECTED',routes=layout(),
        new_cover_required=True,physical_cage_exchange={'P_REAR.1':[32,0,129],'P_REAR.5':[32,13.6,129]},
        preserved_other_P_REAR_cages={'.2':-6.8,'.3':6.8,'.4':-13.6},
        circuit_change='None: all five ports share the same P_REAR bus. Relabel physical .1/.5 and wire them together before selecting.',
        short_branch_reopened='XA01 included explicitly; centre was occupied, never NC.',
        new_four_S1_trial_mm=sum(r['nominal_trial_blank_mm'] for r in layout()[:4]))
    record['assumptions'].append('Upper source reachesZ215.2; guard/support and E6-compatible removable roof must be built before selection. No unchanged original-cover claim.')
    record['source_sha256'].update({q.relative_to(ROOT).as_posix():sha(q) for q in [Path(__file__),proof,aux,
        ROOT/'tools/electronics/w5_s1_source_layout_r2.py',ROOT/'tools/electronics/pwm_fused_pigtail_r1.py']})
    save(path,record)

if __name__=='__main__':main()
