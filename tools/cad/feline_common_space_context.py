"""One current56-module/source + rooted-foundation planning scene.

No source edits, native recompute, automatic removal of reservations or
conversion of accounting endpoints into supplier connector pins.
"""
import json
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_common_retention_roots import archived
from feline_two_lane_receive import world_context


def current():
    world,fixed=world_context()
    files={k:OUT/n for k,n in dict(shared='n01-shared54-current.json',inline='n01-remaining-inline-body-closure.json',
        frame='n01-channelled-foundation-static.json',ends='n01-shared-routing-boundaries.json').items()}
    docs={k:json.loads(p.read_text()) for k,p in files.items()}
    assert docs['shared']['status']=='CURRENT_SHARED54_FULL_UNITS_AND_ATO_RECEIVED_ROOTS_CORRIDORS_OPEN'
    assert docs['inline']['status']=='TWO_WHOLE_INLINE_KITS_RECEIVED_ROOTS_CORRIDORS_OPEN'
    assert docs['frame']['status']=='COMMON_FOUNDATION_CLEAR_NOT_ALL_ROOTS'
    for key in ('inline','frame'):assert docs[key]['world_source_sha256']==world.pins
    parts=dict(fixed);meta={n:dict(world.meta.get(n,{})) for n in parts}
    for key,field,prefix in (('shared','parts',''),('inline','geometry','CurrentInline:'),('frame','geometry','CurrentFoundation:')):
        pp=archived(docs[key],field);records={r['name']:r for r in docs[key][field]}
        for n,s in pp.items():
            name=prefix+n;assert name not in parts,name;parts[name]=s;meta[name]=dict(records[n])
    for n in ('StructureReserve:BankBed-1','StructureReserve:BankBed1'):
        assert n in parts;parts.pop(n);meta.pop(n)
    pins={**world.pins,**{p.relative_to(ROOT).as_posix():sha(p) for p in files.values()}}
    return world,parts,meta,pins,docs


def is_jacket(name,row):
    if ':bare' in name.lower() or 'BodyBare' in name or 'PadBare' in name or row.get('kind')=='bare':return False
    return row.get('kind') in ('wire','proposal_wire','actual_wire','insulation_reservation','curve_profile_reservation') or bool(row.get('wire_owner')) or name.startswith(('End:','Factory:','CustomPrefix:','BankFullPrefix:','ShelfPWM:jacket:','PiGPIO:','PiPower:','PiUSBData')) or name in ('W043','W077','W078')
