"""Compose the front-port pair with native FR seats/cover, not old casing.

Reuse exact R2 shared routing proof for retained owners and all other feeds;
test only the changed native bank/cover/ties. No duplicated whole baseline
audit or inference of service/outer cable protection/selection from fit.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-front-station-shared-fit-r1'
def main():
    import FreeCAD
    import Part
    start=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'checks.json').exists()
    pins={}
    def pin(p):pins[p.relative_to(ROOT).as_posix()]=sha(p)
    def load(p):pin(p);return Part.read(str(p))
    folder=ROOT/'hardware/electronics/full-cat/servo-fuse-front-source-ports-r2'
    q=folder/'checks.json';pin(q);r=json.loads(q.read_text(encoding='utf-8'))
    assert not r['errors'] and not r['factory_failures']
    affected=('W041','W042')
    old_hits=[h for h in r['hits'] if h['part'].startswith(affected) or h['owner'].startswith(affected)]
    assert all(h['owner']=='RetainedCover' for h in old_hits),old_hits
    station=ROOT/'hardware/electronics/full-cat/servo-fuse-fr-joint-station-native-r1'
    q=station/'checks.json';pin(q);native=json.loads(q.read_text(encoding='utf-8'))
    assert not native['hits'] and not native['errors'] and all(x['single_solid'] and x['closed_STL'] and x['relocated_reopen'] and x['strict_BOP_errors']==0 for x in native['exports'])
    changed={p.stem:load(p) for p in folder.glob('*_DESIGN.brep') if p.stem.startswith(affected)}
    owners={tag:load(ROOT/f'hardware/cad/studies/servo-fuse-fr-joint-station-native-r1/{tag}_WORLD.brep') for tag in ('BankRight','Cover')}
    owners.update({p.stem:load(p) for p in station.glob('*Tie*_DESIGN.brep')})
    pairs=0;hits=[];errors=[]
    for n,s in changed.items():
        for m,t in owners.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            pairs+=1
            try:
                h=s.common(t)
                if h.Volume>1e-5:hits.append(dict(part=n,owner=m,volume_mm3=h.Volume))
            except Exception as ex:errors.append(dict(part=n,owner=m,error=str(ex)))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='FRONT_PAIR_NATIVE_STATION_STATIC_CLEAR' if not hits and not errors else 'FRONT_PAIR_NATIVE_CONTACTS',
        selected=False,physical_pass=False,W5_complete=False,hits=hits,errors=errors,pairs=pairs,
        replaced_old_cover_contacts=old_hits,inherited_other_feed_contacts=[h for h in r['hits'] if h not in old_hits],
        same_net_port_permutation='servo-fuse-front-source-ports-r2/port-permutation.json',
        additional_T18I_ties=2,additional_prints=0,
        open=['Exterior west return of FR wire still needs protected construction, not a bare loop outside the cover.',
              'Native WAGO/other joint grips, remaining feeds, RR clip tool access/shared removal, one selection/stock/E3.'],
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print(json.dumps(dict(pairs=pairs,hits=len(hits),errors=len(errors),inherited_other_contacts=len(r['hits'])-len(old_hits))),flush=True)
    assert not hits and not errors
if __name__=='__main__':main()
