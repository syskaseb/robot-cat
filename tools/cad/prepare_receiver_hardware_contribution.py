"""Role-counted receiver hardware; dated selected offers, not a purchase.

The four Frame prints replace their source-only versions. Counts apply only
to this receiver scope, never to the whole robot or delivered inventory.
"""
import hashlib,json,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def quantities(groups):
    assert len(groups)==22
    wires=[w for g in groups.values() for w in g['wires']]
    assert len(wires)==len(set(wires))==36
    triples={n:g for n,g in groups.items() if g['kind']=='triple'}
    singles={n:g for n,g in groups.items() if g['kind']=='single'}
    assert len(triples)==7 and len(singles)==15
    bolted=[n for n,g in triples.items() if g.get('retainer')=='M2_cap']
    assert bolted==['RR_G']
    return dict(replacement_Frame_prints=4,separate_cap_prints=7,
                T18I_receiver_quantity=len(singles)+len(triples)-len(bolted),
                M2x14_receiver_quantity=1,M2_nut_receiver_quantity=1)


def thread_fit(take_up):
    assert 0<=take_up<=.7
    # Local bearing N=-5; nut N=5.5..7.1. Shop's b=5 on L=14.
    nut=(10.5-take_up,12.1-take_up);thread=(9,14)
    return dict(project_cap_take_up_mm=take_up,nut_from_bearing_mm=nut,
                shop_declared_thread_interval_from_bearing_mm=thread,
                nominal_engagement_inside_thread=thread[0]<=nut[0]<nut[1]<=thread[1])


def run():
    tick=time.monotonic();choicefile=OUT/'receiver-joint-selection.json'
    choice=json.loads(choicefile.read_text());assert not choice['errors']
    files=[choicefile,ROOT/choice['domain_receipt'],ROOT/choice['override_receipt'],
           ROOT/'hardware/cad/studies/main-p0-mount/r3/FASTENERS.md',Path(__file__)]
    for n,h in choice['source_sha256'].items():assert SHA(ROOT/n)==h,n
    domains=json.loads(files[1].read_text())['qualified_options']
    domains.update(json.loads(files[2].read_text())['replacement_options'])
    groups={n:domains[n][i] for n,i in choice['selected_options'].items()}
    counts=quantities(groups);fits=[thread_fit(t) for t in (0,.7)]
    assert all(f['nominal_engagement_inside_thread'] for f in fits)
    result=dict(status='RECEIVER_SCOPE_HARDWARE_CONTRIBUTION_PREPARED_NOT_WHOLE_STOCK',
        quantities=counts,thread_checks=fits,
        hardware=[dict(role='RR_G_cap_screw',quantity=1,sku='SKL000596',
            description='BEJMET DIN912 A2 M2x14',
            url='https://bejmet-nierdzewne.pl/pl/p/Sruba-imbusowa-nierdzewna-DIN-912-A2-M2x14/2040'),
            dict(role='RR_G_cap_nut',quantity=1,sku='SKL000381',
            description='BEJMET DIN934 A2 M2',
            url='https://bejmet-nierdzewne.pl/pl/p/Nakretka-szesciokatna-nierdzewna-DIN-934-A2-M-2/1762')],
        offer_evidence_date='2026-09-24',current_price_and_availability_not_checked=True,
        no_purchase=True,no_existing_MAIN_or_ear_hardware_recount=True,
        print_replacement_rule='Four fixed Frames supersede source-only Frame prints; never print both.',
        assembly='Seat nut in NC-side trap before fitting RR_G cap. Hand-tighten with1.5mm hex; do not infer PETG torque from steel data.',
        physical_fit_gates=['Delivered thread/head/nut dimensions','Cap take-up and insulation grip without crush',
                           'Printed nut capture and PETG creep/loosening'],
        open=['Full36middle acceptance and native exports','Other19guides and whole materials reconciliation'],
        source_sha256={p.relative_to(ROOT).as_posix():SHA(p) for p in files},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    (OUT/'receiver-hardware-contribution.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(quantities=counts,worker_seconds=result['worker_seconds'])))


if __name__=='__main__':run()
