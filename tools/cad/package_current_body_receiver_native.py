"""One current12-print component set; never select whole W5 by accident."""
import json,time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,OUT,SHA


def run():
    tick=time.monotonic();rf=OUT/'receiver-supports/manifest.json';uf=OUT/'upper-fixed-feed-supports/manifest.json'
    receiver,upper=[json.loads(f.read_text()) for f in (rf,uf)]
    assert receiver['status']=='FOUR_CURRENT_RECEIVER_FRAMES_SEVEN_CAPS_NATIVE_PREPARED'
    assert upper['status']=='CURRENT_UPPER_FEED_NATIVE_COMPONENT_COMPLETE'
    assert upper['relocated_reopen'] and upper['original_material_preserved']
    assert len(receiver['parts'])==len(receiver['exports'])==11
    for proof in (receiver,upper):
        for n,h in proof['source_sha256'].items():assert SHA(ROOT/n)==h,n
    assert SHA(ROOT/upper['native'])==upper['native_sha256']
    prints=[]
    for r in receiver['exports']:
        assert SHA(ROOT/r['path'])==r['sha256'] and r['printing']['fits_with_5mm_brim']
        native=next(p for p in receiver['parts'] if p['part']==r['part'])
        assert native['relocated_reopen'] and native['core_bore_restore_mm']==[1.3,1.4,1.3]
        assert native['arm_restore_mm']==[4,4.2,4]
        prints.append(dict(r,native='receiver-supports/ReceiverSupportsCurrent.FCStd',native_object=native['object'],
                           identity='CP2:'+r['part'],replaces=r['part'] if native['kind']=='replacement_Frame' else None))
    assert len(upper['records'])==1
    r=upper['records'][0];assert SHA(ROOT/r['export'])==r['export_sha256'] and r['closed_manifold']
    assert max([r['size_mm'][0]+10,r['size_mm'][1]+10,r['size_mm'][2]])<256
    prints.append(dict(identity='CP2:UpperCarrier',part=r['part'],path=r['export'],sha256=r['export_sha256'],
                       quantity=1,native=upper['native'],native_object='UpperCarrierFixedFeedsCurrent',
                       replaces=upper['replaces'],printing=dict(size_mm=r['size_mm'],fits_with_5mm_brim=True)))
    assert len({r['identity'] for r in prints})==12 and sum(r['quantity'] for r in prints)==12
    result=dict(status='CURRENT_BODY_RECEIVER_COMPONENT_NATIVE_SET_NOT_W5_SELECTION',
        prints=prints,replacement_Frame_quantity=4,replacement_UpperCarrier_quantity=1,new_CAP_quantity=7,
        receiver_T18I_quantity=21,receiver_M2x14_quantity=1,receiver_M2_nut_quantity=1,
        feed_lacing_blanks=receiver['lacing_feed_blanks']+upper['lacing_references'],
        feed_lacing_candidate_mm=receiver['lacing_feed_project_total_mm']+upper['lacing_candidate_mm'],
        scope='Current body receiver and G1/G2 feed parts only. Existing Hip/Knee/Ankle/P0/head/tail/bank parts remain in their own current packages; not extra Frame prints.',
        open=['Remaining source carriers and25interfaces','Whole assembled service/stock/current whole-model selection'],
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (rf,uf,Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,stock_selected=False,
        W5_complete=False,physical_pass=False,print_ready=False)
    assert result['feed_lacing_blanks']==18 and result['feed_lacing_candidate_mm']==2700
    (OUT/'current-body-receiver-native-set.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(prints=12,replacements=5,new_caps=7,worker_seconds=result['worker_seconds'])))


if __name__=='__main__':run()
