"""Propagate an actual BOX CASE versus unchanged named wire witness.

No bbox-overlap rejection and no assumption that whole units are identical.
Only actual case geometry is shared. Wire identity must explicitly match its
logical owner; ambiguous historical cache ordering is never guessed.
"""
import json


def case_key(bounds):
    return json.dumps(bounds.tolist() if hasattr(bounds,'tolist') else bounds,
                      separators=(',',':'))


def extra_case_cuts(cuts,mutual_cache,choices,idx,bygeometry,geometry,bounds):
    bycase={}
    for i,(group,row) in enumerate(choices):
        if 'slot' in row:
            bycase.setdefault(case_key(bounds(row)),[]).append(i)
    result=set();used=[]
    for a,b in cuts:
        pair=mutual_cache.get('|'.join(sorted((a,b))),{})
        if pair.get('ok') or not pair.get('pairs'):continue
        witness=pair['pairs'][-1]
        for ckey,wkey in ((a,b),(b,a)):
            cr=choices[idx[ckey]][1];wg=choices[idx[wkey]][0]
            if 'slot' not in cr:continue
            wire='wire:'+wg+'.'
            if not ((witness.get('part')=='case' and witness.get('other','').startswith(wire))
                    or (witness.get('other')=='case' and witness.get('part','').startswith(wire))):continue
            for ia in bycase[case_key(bounds(cr))]:
                for ib in bygeometry[geometry[wkey]]:
                    if choices[ia][0]!=choices[ib][0]:result.add(tuple(sorted((ia,ib))))
            used.append(dict(case_source_key=ckey,unchanged_wire_unit=wkey,
                             actual_pair_key='|'.join(sorted((a,b))),witness=witness))
    return result,used
