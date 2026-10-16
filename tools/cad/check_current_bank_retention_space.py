"""Shared bank-panel/foot/hardware/access gate before four structural roots.

Purchased housing bounds are reservations. A panel's prescribed flange/aperture
interface stays a delivered-fit gate, never reclassified as proven clearance.
"""
import json
import time
from pathlib import Path
import FreeCAD as A
from remaining25_shared_context import load,P
from current_source_retention_context import C,same_parent
from current_bank_retention_material import geometry
from current_work_guard import check


def run():
    check();tick=time.monotonic();targets,wires,pins,parents,grips=load();q=geometry()
    pieces={**q['prints'],**{'Foot/'+n:v['shape'] for n,v in q['feet'].items()},**q['hardware']}
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'current-bank-retention-pairs.json',bounds.near)
    rows=[];contacts=[];errors=[];interface_overlaps=[];access_conflicts=[];pairs=0
    def test(n,s,m,t,r=0,budget=False,interface=False):
        nonlocal pairs
        if not bounds.near(s,t,r+.0001):return
        if r and not t.Solids and len(t.Edges)>1:
            for i,e in enumerate(t.Edges):test(n,s,m+'/'+str(i),e,r,budget,interface)
            return
        check();pairs+=1
        try:gap,volume=cache.check(s,t,0,r)
        except (AssertionError,RuntimeError,ValueError) as e:
            errors.append(dict(a=n,b=m,error=str(e)));return
        if volume>1e-5 or (r and gap<r-1e-6):
            row=dict(a=n,b=m,volume_mm3=volume,gap_mm=gap,required_mm=r)
            (interface_overlaps if interface else access_conflicts if budget else contacts).append(row)
    for n,s in pieces.items():
        for m,t in targets.items():
            if not t.Solids:continue
            # Only the assigned housing/flange reservation of the same bank
            # row may overlap its aperture-bearing panel or retention bar.
            # TE/ATO/wires/other cases never receive this exception.
            side=n[4:5] if n.startswith('Bank') else None
            own_housing=bool(side and m.startswith('F_'+side) and m.endswith('_CP2_Housing'))
            test(n,s,m,t,interface=own_housing)
        for m,(w,r) in wires.items():test(n,s,m,w,r+.25)
        rows.append(n)
        print('bank shared material',n,'pairs',pairs,'contacts',len(contacts),flush=True)
    names=list(pieces)
    for i,n in enumerate(names):
        for m in names[i+1:]:test(n,pieces[n],m,pieces[m])
    for category,items in [('ATO',q['ATO_access']),('Lkey',q['tools'])]:
        for n,s in items.items():
            for m,t in {**targets,**pieces}.items():
                if t.Solids:test(category+'/'+n,s,m,t,budget=True)
            for m,(w,r) in wires.items():test(category+'/'+n,s,m,w,r+.25,budget=True)
    sources=[Path(__file__),Path(__file__).with_name('current_bank_retention_material.py'),
        P.ROOT/'hardware/reference/servo-holder-p0-2026-09-24/ENVELOPE.md',
        P.ROOT/'tools/electronics/servo_fuse_side_bank_r4.py']
    pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in sources})
    result=dict(status='BANK_SHARED_MATERIAL_OR_ACCESS_REQUIRES_CHANGE' if contacts or errors or access_conflicts else
                'BANK_SHARED_NOMINAL_MATERIAL_ACCESS_CLEAR_ROOTS_NATIVE_OPEN',
        completed_material=rows,contacts=contacts,errors=errors,access_reservation_conflicts=access_conflicts,
        assigned_flange_reservation_overlaps=interface_overlaps,
        assigned_interface_remains_delivered_fit_gate=True,
        recipe=q['recipe'],pairs=pairs,source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3),
        root_goals={n:{k:v for k,v in r.items() if k!='shape'} for n,r in q['feet'].items()},
        open=['Four actual structural roots, changed current parent unions',
              'Shared gate with all55 chosen new saddle profiles and their roots',
              'Native/parameter/reopen/STL/stock/whole assembled selection',
              'Delivered holder/body/aperture/ATO/tool fit; nominal reservation is not measured action'],
        selected=False,W5_complete=False,M4_complete=False,physical_pass=False)
    f=P.OUT/'current-bank-retention-space.json';f.write_text(json.dumps(result,indent=2)+'\n');cache.save()
    print(json.dumps({k:result[k] for k in ('status','pairs','worker_seconds')}),flush=True)


if __name__=='__main__':run()
