from common import *
def read(n):return rd(P/(n+'.json'))
def no_hits(n):return all(not r['hits'] for r in read(n)['rows'])
assert all(no_hits(n) for n in ['fl-hand-check','lower-profile-fit','battery-jackets','tap-sections'])
assert no_hits('affected-bearer')
assert no_hits('battery-lower-fit')
assert all(not q['hits'] for q in read('changed-branch-fit')['rows'] if not q['field'].startswith('W041/'))
assert not any(read('seated-units')['rows'].values()) and not any(read('front-mouths')['rows'].values())
assert all(q['full_driver_common']<.001 and q['solids']==1 for q in read('anchor-access').values())
assert all(not v for k,v in read('installed-rests').items() if k!='tail0')
assert abs(read('rear-cap-bearing')['post_common_mm3'])<.001
assert not any(read('load-and-seats')['installed_R_common'].values()) and not read('load-and-seats')['P_AUX_full']
seats=read('final-anchor-seats')['pads'];assert len(seats)==8 and all(v['contact_patch_mm2']>0 for v in seats)
assert not any(v.get('common_mm3',0)>.001 or 'error' in v for v in read('final-anchor-seats')['yaw_full_steel'].values())
ba=read('battery-jackets');assert min(ba['rest_margin_mm'].values())>0 and min(ba['parked_withdrawal_margin_mm'].values())>0
idx=read('material-index');assert all(v.get('stl') and max(v['envelope_with_allowance'])<=256 for v in idx['parts'])
assert idx['native_sha256']==sha(native) and all(r['steel_after']<.00001 and r['tool_after']<.00001 for r in read('gimbal-steel-access').values())
eff=rd(G/'effectivity.json')['source_coverage'];rr=read('whole-termination-plan');assert len(rr['wires'])==160
wr('decision.json',dict(digital_first_fit=True,label_pl='Komplet cyfrowy do pierwszej przymiarki bez zasilania.',decision_pl='Znane kolizje montażowe zmienionych podstaw, pięciu opraw, dojść G1/P_FRONT oraz górnej i dolnej strony XT60 rozstrzygnięto w zapisanym modelu. Warunki pomiaru dostarczonych części są wymienione w instrukcji.',source_H=sha(H19/'whole-cat19H.FCStd'),source_coverage=eff,effective_prints=len(idx['parts']),installed_print_qty=sum(r['qty'] for r in idx['parts']),source_connections=rr['source_counts'],corrected_anchors=read('anchor-access'),lower_battery_test='lower-profile-fit.json / pack±1, W001 and fixed W075. Two-jacket model. Delivered pack exit estimated at +X end of upper face.',seated_pack_min_clearance_to_allocated_groups=min(ba['rest_margin_mm'].values()),neutral_14mm_withdrawal_min_clearance_to_allocated_groups=min(ba['parked_withdrawal_margin_mm'].values()),r7_method='Source eb18a705, conditional continuous window taps and insulated lead lengths; 50+196=246 within each JR',neck='Opaque front-quarter and reverse view show a narrow running seam. Fixed side guard covers the outer approach to the connector; inspect manual movement and snagging before power.',leg_scope='49 source planning poses, selected=false; only the affected wheel-well material evaluated. No certified deep lie, joint limits or payload.',physical_checks=rr['physical_checks'],physical_PASS=False,actual_cut_fit_slack=None))
