"""One RR station with its post north of G_AUX and bands outside insulation.

Preserve the complete R8 source. Extension grip moves1mm along straight
insulation, outside the26mm sleeve; shorten its PETG roof to clear W078.
Check only new stock/straps before the expensive inherited Deck operation.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rr_source_station_native_r2.py')
wrapper=parent.read_text(encoding='utf-8')
tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
code=code.replace("servo-fuse-rr-source-station-native-r2'","servo-fuse-rr-source-station-native-r3'")
code=code.replace('    assert j[\'intact_insulation_overlap_each_mm\']==9 and j[\'grip_length_mm\']==4',
    "    assert j['intact_insulation_overlap_each_mm']==9 and j['grip_length_mm']==4\n    j['extension_grip_centre_mm'][1]=-34\n    assert j['extension_grip_centre_mm'][1]-2==j['centre_mm'][1]+13")
code=code.replace('-59.5','-47').replace('-55.5','-43')
code=code.replace('cx+4.5,-31,z','cx+4.5,-32,z')
code=code.replace('jointclear.Height=28','jointclear.Height=27')
code=code.replace('xa=cx-1.9;xb=cx+5.7','xa=cx-od/2-1.2;xb=cx+5.7')
code=code.replace('cx-.7,y+1.25,z+4.2','cx-od/2,y+1.25,z+4.2')
needle="    ties={};seats=[];d=A.openDocument(str(deckpath));deckdest=CAD/'DeckRRSourceStation.FCStd'"
assert needle in code
code=code.replace(needle, '''    # Exact small construction stock and both real bands first. Reject here
    # without repeating a20minute inherited Deck operation on bad support.
    foot=[cx+.5,-47,108.8,cx+4.5,-43,109]
    area=olddeck.common(box(foot)).Volume/.2
    assert abs(area-16)<1e-5,dict(foot=foot,bearing_mm2=area)
    prospective=box([cx+.5,-47,108.8,cx+4.5,-43,z]).fuse(box([cx-.7,-67,z-8,cx+4.5,-32,z]))
    cuttools=[Part.makeCylinder(5,27,V(cx,-63,z),V(0,1,0))];pre_ties={}
    for role,key,od in [('Factory','factory_grip_centre_mm',5),('Extension','extension_grip_centre_mm',4.2)]:
        x,y,zz=j[key]
        cuttools += [Part.makeCylinder(od/2+.2,6,V(cx,y-3,z),V(0,1,0)),box([cx-2,y-1.4,z-6.3,cx+6,y+1.4,z-4.5])]
        xa=cx-od/2-1.2;xb=cx+5.7
        bs=[[xa,y-1.25,z-6,xb,y+1.25,z-4.8],
            [xa,y-1.25,z-6,cx-od/2,y+1.25,z+4.2],
            [cx+4.5,y-1.25,z-6,xb,y+1.25,z+4.2],
            [xa,y-1.25,z+3,xb,y+1.25,z+4.2]]
        for k,b in enumerate(bs):pre_ties[f'RR{role}_TieBand{k}']=box(b)
        pre_ties[f'RR{role}_TieHead']=box([xb,y-2.25,z-.5,xb+4.8,y+2.25,z+3])
    for t in cuttools:prospective=prospective.cut(t)
    assert prospective.isValid() and len(prospective.Solids)==1
    pre_hits=[];pre_errors=[];pre_pairs=0
    for n,s in {'RRStock':prospective,**pre_ties}.items():
        targets=dict(owners)
        if n!='RRStock':targets.update(RRStock=prospective,OriginalDeck=olddeck)
        for m,t in targets.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            pre_pairs+=1
            try:
                h=s.common(t)
                if h.Volume>1e-5:pre_hits.append(dict(part=n,owner=m,volume_mm3=h.Volume,bounds_mm=bounds(h)))
            except Exception as exc:pre_errors.append(dict(part=n,owner=m,error=str(exc)))
    save(OUT/'support-preflight.json',dict(pairs=pre_pairs,hits=pre_hits,errors=pre_errors,
        bearing_mm2=area,source_sha256=pins,selected=False,physical_pass=False))
    print('RR_SMALL_STOCK_PREFLIGHT',len(pre_hits),len(pre_errors),flush=True)
    assert not pre_hits and not pre_errors,pre_hits
    ties={};seats=[];d=A.openDocument(str(deckpath));deckdest=CAD/'DeckRRSourceStation.FCStd' ''')
code=code.replace('    pins={};V=A.Vector',"    pins={};V=A.Vector\n    pins['tools/electronics/servo_fuse_rr_source_station_native_r2.py']=sha(ROOT/'tools/electronics/servo_fuse_rr_source_station_native_r2.py')")
code=code.replace("d.recompute();deck=final.Shape.copy()", "d.recompute();print('RR_DECK_COMPUTED',flush=True);deck=final.Shape.copy()")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
