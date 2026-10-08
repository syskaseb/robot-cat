"""Classify received common-space contacts without repeating any BRep check.

Exact same-conductor reservations/insulation overlap are not contacts between
distinct wires/parts. All actual cross-part contacts stay open, including U1's
provisional allowance. Preserve the received geometry snapshot unchanged.
"""
from datetime import datetime,timezone
from pathlib import Path
import json
from open_prototype_wiring_endpoints import ROOT,BASE,read,sha

OUT=BASE/'wiring-checkpoint'


def classify(contact, inputs):
    a,b=contact['a'],contact['b']
    if a.endswith('/input') and b=='entry/'+inputs.get(a.split('/')[0],''):
        return 'same factory input and its last9mm port reservation'
    if '/' in a and '/' in b:
        ah,ar=a.split('/',1);bh,br=b.split('/',1)
        if ah==bh and ah in inputs and {ar,br} in ({'output','sleeve'},{'sleeve','new_grip'}):
            return 'same conductor inside its explicit insulation clearance budget'
    return None


def main():
    proof=OUT/'main-entry-space-checks.json';plan=OUT/'main-entry-space-plan.json'
    dest=OUT/'main-entry-space-disposition.json'
    assert not dest.exists(),'Receive existing disposition before rewriting'
    r=read(proof);assert r['status']=='SHARED_ENTRY_SPACE_CAUSE_CHANGE_REQUIRED'
    inputs={q['holder']:q['target'] for q in r['factory_input_rows']}
    excluded=[];actual=[];seen=set()
    for c in r['contacts']:
        reason=classify(c,inputs)
        if reason:
            excluded.append(dict(c,reason=reason));continue
        key=tuple(sorted((c['a'],c['b'])))
        if key in seen:continue
        seen.add(key);actual.append(c)
    impossible=[q for q in r['factory_input_rows'] if q['impossible']]
    assert len(actual)==6 and {q['holder'] for q in impossible}=={'F_PI','F_AUX'}
    assert not r['errors'] and not r['outside_torso']
    data=dict(status='COMMON_LOWER_SOURCE_HYPOTHESIS_REJECTED_BEFORE_NATIVE_CHANGE',
        selected=False,stage_completed=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (proof,plan,Path(__file__))},
        raw_pair_checks=r['tested_pairs'],repeated_BRep_checks=0,
        same_conductor_insulation_or_reservation_disposition=excluded,
        distinct_remaining_contacts=actual,impossible_prefuse_inputs=impossible,
        U1_contact_is_provisional_reservation_not_delivered_pad_geometry=True,
        worker_seconds=r['worker_seconds'],preserved_native_commit='4903198',
        changed_native_documents=0,new_native_exports=0,
        rejected='Lowering all5FHAC/floor19.5mm and moving all output drops outward is NOT chosen. No smaller scalar-height retry.',
        next_contract=[
            'Plan all8 complete source/output feeds, both MTA exits, 5FHAC inputs and support/tool spaces together before another native rebuild.',
            'Keep P0/E6,actual S0 access,U1 allowance pending delivery,Pi/AUX prefuse50mm,HELU4.2/R25.2,torso325x200x160.',
            'Choose macro separation of bulky source bodies from main-feed receiving bends, not independent curve microshifts.',
            'Any new MTA/source/WAGO pose must explicitly invalidate its affected native mounts/route proof; do not copy local acceptance as whole-wire acceptance.',
            'Connectors/extensions use existing exact material facts, no guaranteed100mm factory length, no invented U1/S0 pinout.',
            'Do not repeat lowered source hypothesis, rejected low rear posts/S1driver, or unchanged87pair source/MTA mount checks.'],
        finished_utc=datetime.now(timezone.utc).isoformat())
    dest.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=data['status'],actual_contacts=len(actual),
                         prefuse_limits_exceeded=len(impossible),rerun_pairs=0)))


if __name__=='__main__':main()
