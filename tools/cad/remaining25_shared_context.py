"""Saved current material context, avoiding repeated native-history recovery."""
import json
import zipfile
from pathlib import Path
import Part
from current_source_retention_context import context, P
from check_main_p0_placement import SavedShapes


def load():
    archive=P.OUT/'remaining25-space-context.zip'
    if archive.exists():
        with zipfile.ZipFile(archive) as z:
            index=json.loads(z.read('index.json'))
            assert index['source_sha256'][Path(__file__).relative_to(P.ROOT).as_posix()]==P.SHA(Path(__file__))
            for n,h in index['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,('Changed cached scene source',n)
            targets={};wires={};parents={}
            for r in index['entries']:
                s=Part.Shape();s.importBrepFromString(z.read(r['file']).decode())
                if r['kind']=='wire':wires[r['name']]=(s,r['radius_mm'])
                elif r['kind']=='parent':parents[r['name']]=s
                else:targets[r['name']]=s
        pins=dict(index['source_sha256']);pins[archive.relative_to(P.ROOT).as_posix()]=P.SHA(archive)
        print('reused pinned remaining25 material context',len(targets),len(wires),flush=True)
        return targets,wires,pins,parents,index['grips']
    targets,wires,pins,oldprofiles,recipes,parents,grips=context()
    f=P.OUT/'local-source-retention-native/manifest.json';p=json.loads(f.read_text())
    assert p['status']=='THIRTEEN_SOURCE_LANDS_FIVE_NATIVE_PARENT_REPLACEMENTS_COMPLETE'
    reader=SavedShapes()
    for r in p['models']:assert P.SHA(P.ROOT/r['path'])==r['sha256']
    for r in p['parts']:
        shape=reader.shape(P.ROOT/r['native'],r['object']);owner=r['part']
        parents[owner]=shape
        if owner in ('LeftRiser','RightRiser'):targets['neck/'+owner]=shape
        else:targets['CurrentNative/'+owner]=shape
        for name in r['lacing_reference_objects']:
            targets['RetainedSourceLacing/'+name]=reader.shape(P.ROOT/r['native'],name)
    pins.update(reader.hashes);pins[f.relative_to(P.ROOT).as_posix()]=P.SHA(f)
    pins[Path(__file__).relative_to(P.ROOT).as_posix()]=P.SHA(Path(__file__))
    small_grips=dict(groups={n:dict(owner=g['owner']) for n,g in grips['groups'].items()})
    entries=[];tmp=archive.with_suffix('.tmp')
    with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for kind,items in [('target',targets),('wire',wires),('parent',parents)]:
            for name,value in items.items():
                s,r=value if kind=='wire' else (value,None)
                file='part'+str(len(entries))+'.brep';z.writestr(file,s.exportBrepToString())
                entries.append(dict(kind=kind,name=name,file=file,**(dict(radius_mm=r) if r is not None else {})))
        z.writestr('index.json',json.dumps(dict(entries=entries,source_sha256=pins,grips=small_grips)))
    tmp.replace(archive);pins[archive.relative_to(P.ROOT).as_posix()]=P.SHA(archive)
    print('saved pinned remaining25 material context',len(targets),len(wires),flush=True)
    return targets,wires,pins,parents,small_grips
