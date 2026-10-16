"""Changed complete W041 factory/custom pair; no source limit relaxation."""
import math
from plan_current_main_sources import entry,turn,offset,straight,finish,E,W,S,U


def routes(plan,receiving):
    old=plan['factory_routes']['W041_FACTORY'];start=old['parts'][0]['start']
    factory=entry(start,E);turn(factory,E,U);straight(factory,[36.7,80.5,185.6])
    length=sum(p['length_mm'] for p in factory)
    assert length<=old['usable_lead_assumption_mm'] and abs(length-old['guide_mm'])<1e-7
    # Opposed joint35.5 is still a real separate purchased envelope, not wire.
    custom_start=[36.7,80.5,221.1];q=entry(custom_start,U);turn(q,U,W)
    top=q[-1]['end'][2];assert abs(top-255.3)<1e-7
    offset(q,W,S,34)
    port=receiving['P_FRONT']['ports']['2'];p=entry(port,W);turn(p,W,U)
    straight(p,[p[-1]['end'][0],port[1],top-25.2]);turn(p,U,E)
    straight(q,p[-1]['end']);custom=finish(q,p)
    assert math.dist(custom[-1]['end'],port)<1e-7
    return dict(W041_FACTORY=dict(parts=factory,radius_mm=old['radius_mm'],guide_mm=length,
        usable_lead_assumption_mm=old['usable_lead_assumption_mm'],nominal_strip_mm=old['nominal_strip_mm']),
        W041_CUSTOM=dict(parts=custom,radius_mm=2.1,guide_mm=sum(p['length_mm'] for p in custom),actual_cut_mm=None))
