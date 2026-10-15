"""Derive editable positive masks for the four received fixed Frame subsets.

Preserve the real bare native Frame feature plus both sibling source arms.
Common with original final native applies all inherited reliefs. Compare to
the received retained BRep, not a surrogate bounding box.
"""
import copy,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
import build_remaining_loom_supports as G
P=G.P


def run():
    tick=time.monotonic();files=[P.OUT/n for n in ('body-low-hip-retention-plan.json',
        'remaining-support-shared-paths.json','remaining-retention-entry.json','remaining-loom-roots-plan.json',
        'remaining-supports/manifest.json')]
    fixed,paths,retention,roots,native=[json.loads(f.read_text()) for f in files]
    byname={r['owner']:r for r in fixed['retained']}
    for collection,key in ((paths,'paths'),(retention,'ports'),(roots,'lands')):
        collection['groups']=[g for g in collection['groups'] if g['id'] in byname]
        for group in collection['groups']:
            omit=byname[group['id']]['removed_only'].split(' owned')[0]
            group[key]=[r for r in group[key] if r.get('land_id',r.get('id'))!=omit]
    barefile=P.OUT/'StationFramesCurrent.FCStd';files.append(barefile)
    reader=G.B.H.P.SavedShapes();parents={r['preserved_owner']:reader.shape(barefile,r['preserved_owner']) for r in roots['groups']}
    shapes,recipes,_,_,errors=G.allocation(paths,retention,roots,parents);assert not errors,errors
    src=P.ROOT/next(r['path'] for r in native['native_documents'] if r['path'].endswith('StationFramesSupported.FCStd'));files.append(src)
    assert P.SHA(src)==next(r['sha256'] for r in native['native_documents'] if P.ROOT/r['path']==src)
    archive=P.ROOT/fixed['archive'];assert P.SHA(archive)==fixed['archive_sha256'];files.append(archive)
    with zipfile.ZipFile(archive) as z:
        index=json.loads(z.read('index.json'));expected={}
        for name in recipes:
            item=next(r for r in index if r['name']=='Retained_'+name)
            s=Part.Shape();s.importBrepFromString(z.read(item['file']).decode());expected[name]=s
    d=A.openDocument(str(barefile));tips={r['preserved_owner']:d.getObject(r['preserved_owner']).Tip.Name for r in roots['groups']};A.closeDocument(d.Name)
    parts=[]
    for name,recipe in recipes.items():
        mask=parents[recipe['preserved_owner']].copy()
        for pad in recipe['pads']:mask=mask.fuse(G.oriented(pad['bounds_mm'],pad.get('placement'))).removeSplitter()
        original=reader.shape(src,recipe['preserved_owner']);kept=original.common(mask).removeSplitter()
        difference=[kept.cut(expected[name]).Volume,expected[name].cut(kept).Volume]
        assert max(difference)<1e-4,(name,difference)
        assert kept.isValid() and len(kept.Solids)==1 and not kept.check(True),name
        parts.append(dict(name=name,original_native_body=recipe['preserved_owner'],
            bare_native_tip=tips[recipe['preserved_owner']],positive_pads=recipe['pads'],
            exact_difference_mm3=difference,volume_mm3=kept.Volume))
        print('fixed native retained mask',name,'positive pads',len(recipe['pads']),flush=True)
    receipt=dict(status='FOUR_FIXED_NATIVE_POSITIVE_MASKS_EXACT_RETAINED_SUBSETS',parts=parts,
        source_native=src.relative_to(P.ROOT).as_posix(),bare_native=barefile.relative_to(P.ROOT).as_posix(),
        source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in [*files,Path(__file__)]},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,physical_pass=False)
    out=P.OUT/'fixed-native-retained-masks.json';out.write_text(json.dumps(receipt,indent=2)+'\n')


if __name__=='__main__':run()
