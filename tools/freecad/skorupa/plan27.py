"""Correct inverted mounting of all four hip servos; geometry untouched.

Evidence: WConnector M2 axes coincide with servo housing pilot axes. The
root servo CASE must move with WConnector; its two horns attach to chassis.
Knee case / horns were already assigned correctly; ankle also unchanged.
"""
from pathlib import Path
import json
import hashlib

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'hardware/skorupa/v27'


def main():
    old=json.loads((ROOT/'hardware/skorupa/v24/assembly-plan.json').read_text(encoding='utf8'))
    old['source_sha256']=hashlib.sha256((ROOT/'hardware/skorupa/v25/Kot_v25_DOMOWA_OSLONA.FCStd').read_bytes()).hexdigest()
    changes=[]
    for axis in old['axes']:
        if axis['stage']!='Hip':continue
        stage='Motion_'+axis['code']+'_Hip'
        connector=next(p['name'] for p in old['components'] if p['stage']==stage and p['label'].startswith('WConnector'))
        number=int(axis['horn'].replace('Part__Feature',''))
        for i in range(number-6,number+2):
            name='Part__Feature%03d'%i
            c=next(p for p in old['components'] if p['name']==name)
            j=next(p for p in old['joints'] if p['child']==name)
            assert j['type']=='Fixed'
            body=i<number
            assert c['stage']==('Chassis' if body else stage)
            changes.append(dict(name=name,old_stage=c['stage'],old_parent=j['parent'],
                                new_stage=stage if body else 'Chassis',new_parent=connector if body else 'FrameFront20'))
            c['stage']=stage if body else 'Chassis';j['parent']=connector if body else 'FrameFront20'
            j['status']='hip case attached to WConnector; horns grounded to frame (mount-hole axes verified)'
    assert len(changes)==32
    parents={j['child']:j['parent'] for j in old['joints']}
    for p in old['components']:
        n=p['name'];seen=set()
        while n!=old['ground']:
            assert n not in seen;seen.add(n);n=parents[n]
    old['scope']='12 leg DOF with corrected inverted hip mounting. 64 head/tail/electronics temporary locks remain. No print approval.'
    (OUT/'assembly-plan.json').write_text(json.dumps(old,indent=2,ensure_ascii=False),encoding='utf8')
    (OUT/'ownership-changes.json').write_text(json.dumps(changes,indent=2),encoding='utf8')
    print('32 Fixed references to update; 12 Revolute axes and all shapes unchanged')


if __name__=='__main__':main()
