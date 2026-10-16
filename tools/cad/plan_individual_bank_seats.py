"""Twelve local catalog2mm snap panels, no wide strap comb or moved wiring.

Panel material stays within its own28x15 flange footprint. The drawing cutout
is22.2x11.3(+.3/-0);11.6 is chosen provisionally. Nominal gross Housing
overlap is assigned ONLY inside that2mm panel, not a tolerance/clip proof.
Root paths, native construction and all installed service remain OPEN.
"""
import json,time
from pathlib import Path
import FreeCAD as A
from remaining25_shared_context import load,P
from current_source_retention_context import C,same_parent
from current_bank_datums import datums
from plan_remaining25_restraint_space import profile
from plan_axial_source_supports import arm_box
from loom_land_port import box
from current_work_guard import check


def seats(placed):
    result={}
    for r in placed:
        x,y=r['centre_xy_mm'];z=r['flange_top_z_mm']
        shape=box([x-14,y-7.5,z-4,x+14,y+7.5,z-2]).cut(box([x-11.1,y-5.8,z-5,x+11.1,y+5.8,z-1])).removeSplitter()
        assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
        result[r['id']]=dict(body=shape,recipe=dict(centre_mm=[x,y,z],panel_thickness_mm=2,
            flange_footprint_mm=[28,15],aperture_mm=[22.2,11.6],
            source='hardware/reference/servo-holder-p0-2026-09-24/0300330.png',
            catalog_basis='MTA B0-100.E10A d2 panel,a22.2,b11.3(+.3/-0); no measured clip/force claim',
            delivered_fit_gate=True,root_path=None,new_case_ties=0))
    return result


def run():
    check();tick=time.monotonic();targets,wires,pins,parents,grips=load()
    files=[P.OUT/(n+'.json') for n in ('remaining25-restraint-space','remaining25-saddle-roots')]
    saddles,roots=[json.loads(f.read_text()) for f in files]
    assert roots['accepted_groups']==54 and not roots['errors']
    for receipt in (saddles,roots):
        for n,h in receipt['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    groups={g['id']:g for g in saddles['spatial_groups']}
    for gid,i in saddles['selected_options'].items():
        rec=saddles['domains'][gid][i]['recipe'];s=profile(groups[gid],rec['normal'],rec['knot_sign']);assert s['recipe']==rec
        targets.update({'Remaining25/'+gid+'/'+k:s[k] for k in ('body','band')})
    for row in roots['groups']:
        for i,(a,b) in enumerate(zip(row['path'],row['path'][1:])):
            targets['CurrentSaddleRoot/'+row['owner']+'/'+row['id']+'/'+str(i)]=arm_box(a,b,roots['arm_half_widths_mm'])
    placed=datums(targets);panels=seats(placed)
    files.extend([Path(__file__),Path(__file__).with_name('current_bank_datums.py'),
        P.ROOT/'hardware/reference/servo-holder-p0-2026-09-24/0300330.png'])
    pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files})
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(P.OUT/'individual-bank-seat-pairs.json',bounds.near)
    checks=0;records=[];errors=[]
    def save():
        result=dict(status='TWELVE_INDIVIDUAL_BANK_SEATS_MATERIAL_CLEAR_ROOTS_SERVICE_OPEN' if len(records)==12 and not errors and not any(r['contacts'] for r in records) else 'INDIVIDUAL_BANK_SEAT_MATERIAL_PENDING_OR_REJECTED',
            seats=records,checks=checks,errors=errors,source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3),
            changed_purchased_parts=0,changed_wires=0,retained_saddle_roots=54,
            open=['Twelve actual rooted load paths with service reservations','Full installed ATO/tool access including current G1 and obstructing feeds',
                  'Native editable CAD/parameter/reopen/exports and assembly/stock/physical delivered snap fit'],
            selected=False,W5_complete=False,M4_complete=False,physical_pass=False)
        f=P.OUT/'individual-bank-seat-space.json';tmp=f.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(f);cache.save()
    def hit(a,b,r=0):
        nonlocal checks
        if not bounds.near(a,b,r+.0001):return None
        if r and not b.Solids and len(b.Edges)>1:return next((v for e in b.Edges if (v:=hit(a,e,r)) is not None),None)
        try:
            check();checks+=1;gap,volume=cache.check(a,b,0,r)
        except (TimeoutError,AssertionError,RuntimeError,ValueError) as e:errors.append(str(e));save();raise
        if volume>1e-5 or (r and gap<r-1e-6):return dict(volume_mm3=volume,gap_mm=gap,required_mm=r)
        return None
    save()
    for r in placed:
        gid=r['id'];q=panels[gid];s=q['body'];row=dict(id=gid,recipe=q['recipe'],contacts=[],catalog_panel_interfaces=[],parent_union_candidates=[]);records.append(row)
        own=r['parts']['Housing']['name']
        for n,t in targets.items():
            if not t.Solids:continue
            v=hit(s,t)
            if v is None:continue
            if n==own:row['catalog_panel_interfaces'].append(dict(part=n,**v));continue
            if any(same_parent(o,n,grips) for o in parents) or n.startswith('CurrentSaddleRoot/'):
                row['parent_union_candidates'].append(dict(part=n,**v));continue
            row['contacts'].append(dict(obstacle=n,**v))
        for n,(w,rad) in wires.items():
            if (v:=hit(s,w,rad+.25)) is not None:row['contacts'].append(dict(obstacle=n,**v))
        for other,o in panels.items():
            if other!=gid and (v:=hit(s,o['body'])) is not None:row['contacts'].append(dict(obstacle='Seat/'+other,**v))
        save();print('individual bank seat',gid,'contacts',len(row['contacts']),'pairs',checks,flush=True)
    print(json.dumps(dict(seats=len(records),contacts=sum(len(r['contacts']) for r in records),checks=checks,seconds=round(time.monotonic()-tick,3))),flush=True)


if __name__=='__main__':run()
