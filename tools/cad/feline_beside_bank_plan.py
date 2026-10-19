"""One constructive under-bank side gallery, all purchased mouths together.

Changed functional axes, not a scalar retry: pitch X, lever UP, all tails
inward/down to the common spine beside the battery. Bank/ATO stays put.
No full-world approval or N01 score implied by this constructor.
"""
import json
from feline_underplate_station_templates import build_underplate
from plan_feline_layout import OUT


def slots():
    rows=[]
    for profile,dims,y,pitch in (('standard',[30.,19.,9.],66.,31.25),
                                 ('large',[37.,22.,11.],75.,40.)):
        xs=[(i-3.5)*pitch for i in range(8)] if profile=='standard' else [-85.,-45.,-5.,35.,75.,115.]
        for side in (-1,1):
            for x in xs:
                rows.append(dict(id=len(rows),profile=profile,centre_mm=[x,side*y,44.5],dimensions_mm=dims,
                    pose_family='BESIDE_BANK_INWARD_DOWN_COMMON_SPINE',head_side=-side,
                    datum='Standard case below bankbedZ52: top49+3gap; large top50+2gap. Tail spine outside batteryY27.'))
    return rows


def unit(st,slot):
    return build_underplate(st,slot,1,slot['head_side'])


if __name__=='__main__':
    plan=json.loads((OUT/'n01-flat-station-architecture.json').read_text())
    for ref in ('D_FL','FL_P','P_FRONT','G1'):
        st=next(s for s in plan['stations'] if s['ref']==ref)
        profile='large' if st['flat_dimensions_pitch_departure_thickness_mm'][2]>10 else 'standard'
        slot=next(s for s in slots() if s['profile']==profile and s['centre_mm'][1]>0)
        model=unit(st,slot)
        for w in model['wires']:
            for n in ('case','split_common_comb','band_budget','head_budget'):
                c=model['parts']['wire:'+w['endpoint']].common(model['parts'][n]);assert c.isValid() and c.Volume<1e-5,(ref,w['endpoint'],n,c.Volume)
        assert model['parts']['head_budget'].Volume==216
        assert model['nylon_loop_upper_bound_mm']<100
        print(ref,'own full mouth/R/9grip/band/head received',flush=True)
