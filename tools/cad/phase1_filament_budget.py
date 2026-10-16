"""Upper solid-volume PETG budget of selected STL counts; not slicer mass."""
import json,math,time
from pathlib import Path
from collections import defaultdict
from phase1_stl_preflight import triangles
from plan_current_harness_interfaces import ROOT,BASE,SHA
from current_work_guard import check


def volume(raw):
    total=0.0;directions=defaultdict(int)
    for a,b,c in triangles(raw):
        total+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
        tri=[tuple(round(x,6) for x in v) for v in (a,b,c)]
        for u,v in zip(tri,tri[1:]+tri[:1]):
            k=(u,v) if u<v else (v,u);directions[k]+=1 if u<v else -1
    assert total and not any(directions.values()),'Inconsistent signed-volume orientation'
    return abs(total)


def run():
    check();tick=time.monotonic();p=BASE/'phase1-current-print-selection.json';d=json.loads(p.read_text());rows=[];pins={p.relative_to(ROOT).as_posix():SHA(p)}
    for r in d['prints']:
        check();f=ROOT/r['path'];assert SHA(f)==r['sha256'];v=volume(f.read_bytes())
        rows.append(dict(identity=r['identity'],quantity=r['quantity'],solid_volume_mm3=v,installed_solid_volume_mm3=v*r['quantity']))
    total=sum(r['installed_solid_volume_mm3'] for r in rows)
    # Project conservative supply allowance, NOT material manufacturer's density
    # or the mass of a chosen infill/profile. Do not turn this into robot CoM.
    upper_g=total/1000*1.3;budget_g=upper_g*1.35+200
    out=dict(status='NOMINAL_PETG_SOLID_UPPER_SUPPLY_BUDGET_NOT_SLICER',rows=rows,
        installed_solid_volume_mm3=total,project_density_g_cm3=1.3,solid_mass_project_upper_g=upper_g,
        support_waste_project_fraction=.35,coupon_project_allowance_g=200,
        planned_total_g=budget_g,selected_1kg_spools=math.ceil(budget_g/1000),
        source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3),
        physical_pass=False,actual_infill_profile_mass_known=False,robot_mass_or_CoM_qualified=False)
    f=BASE/'phase1-filament-budget.json';f.write_text(json.dumps(out,indent=2)+'\n',newline='\n')
    print(json.dumps({k:out[k] for k in ('solid_mass_project_upper_g','planned_total_g','selected_1kg_spools','worker_seconds')}),flush=True)


if __name__=='__main__':run()
